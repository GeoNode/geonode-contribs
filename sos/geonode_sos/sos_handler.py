import json
import logging
import requests
import re
from collections import namedtuple
from typing import NamedTuple
from uuid import uuid4

import requests
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
from geonode import settings
from geonode.base.bbox_utils import BBOXHelper
from geonode.base.models import ExtraMetadata, Link
from geonode.layers.models import Layer
from geonode.services.enumerations import INDEXED
from geonode.services.serviceprocessors.base import (
    ServiceHandlerBase,
    get_geoserver_cascading_workspace,
)

from geonode_sos.models import FeatureOfInterest, Offerings
from geonode_sos.parser import DescribeSensorParser

logger = logging.getLogger(__name__)


class SosServiceHandler(ServiceHandlerBase):

    service_type = "SOS"

    def __init__(self, url):
        ServiceHandlerBase.__init__(self, url)
        self.proxy_base = None
        self.url = url
        self.indexing_method = INDEXED
        self.json_response = None
        self.name = slugify(self.url)[:255]
        self.workspace = get_geoserver_cascading_workspace(create=False)

    @property
    def parsed_service(self):
        if self.json_response is None:
            payload = json.dumps({"request": "GetCapabilities", "service": "SOS"})
            headers = {"Content-Type": "application/json"}
            self.json_response = requests.request(
                "POST", self.url, headers=headers, data=payload
            ).json()
        return self.json_response

    def has_resources(self) -> bool:
        return len(self.parsed_service.get("contents", [])) > 0

    def get_keywords(self):
        return []

    def get_resource(self, resource_id):
        """Return a single resource's representation."""
        procedure = [
            proc
            for proc in self._get_procedure_list()
            if resource_id in self._generate_id(proc)
        ]
        return procedure[0] if procedure else None

    def get_detailed_procedure(self, procedure_id):
        """Return a single resource's representation."""
        procedure = [
            proc
            for proc in self.parsed_service.get("contents", [])
            if procedure_id == proc.get("procedure")[0]
        ]
        return procedure[0] if procedure else None

    def get_resources(self):
        """Return an iterable with the service's resources."""
        return [self._create_obj(x, None, None) for x in self._get_procedure_list()]

    def create_geonode_service(self, owner, parent=None):
        """Create a new geonode.service.models.Service instance
        Saving the service instance in the database is not a concern of this
        method, it only deals with creating the instance.

        :arg owner: The user who will own the service instance
        :type owner: geonode.people.models.Profile
        """
        from geonode.services.models import Service

        _response = self.parsed_service.get("serviceIdentification", {})
        instance = Service(
            uuid=str(uuid4()),
            base_url=self.url,
            type=self.service_type,
            method=self.indexing_method,
            owner=owner,
            parent=parent,
            metadata_only=True,
            version=self.parsed_service.get("version", "2.0.0"),
            name=self.name,
            title=_response.get("title").get("eng"),
            abstract=_response.get("abstract", {}).get("eng", None)
            or _("Not provided"),
            online_resource=self.url,
        )
        return instance

    def harvest_resource(self, resource_id: str, geonode_service) -> Layer:
        """Harvest a single resource from the service
        This method creates new ``geonode.layers.models.Layer``
        instances (and their related objects too) and save them in the
        database.

        :arg resource_id: The resource's identifier
        :type resource_id: str
        :arg geonode_service: The already saved service instance
        :type geonode_service: geonode.services.models.Service
        """
        _exists = self.get_resource(resource_id=resource_id)
        if _exists:
            _resource_detail = self._get_procedure_detail(_exists)
            _resource_as_dict = self._from_resource_to_layer(_resource_detail)

            existance_test_qs = Layer.objects.filter(
                name=_resource_as_dict["name"],
                store=_resource_as_dict["store"],
                workspace=_resource_as_dict["workspace"],
            )
            if existance_test_qs.exists():
                raise RuntimeError(
                    f"Resource {_resource_as_dict['name']} has already been harvested"
                )
            if settings.RESOURCE_PUBLISHING or settings.ADMIN_MODERATE_UPLOADS:
                _resource_as_dict["is_approved"] = False
                _resource_as_dict["is_published"] = False
            layer = self._create_layer(_resource_as_dict, geonode_service)
            self._set_extra_metadata(layer, _resource_detail)
            self._set_feature_of_interest(layer, _resource_detail)
            self._set_offerings(layer, _resource_detail)
            return layer
        raise RuntimeError(f"Resource {resource_id} cannot be harvested")

    def _create_layer(self, _resource_as_dict: dict, geonode_service) -> Layer:
        _ows_url = _resource_as_dict.pop("ows_url")
        _ = _resource_as_dict.pop("keywords") or []
        geonode_layer = Layer(
            owner=geonode_service.owner,
            remote_service=geonode_service,
            uuid=str(uuid4()),
            resource_type="sos_sensor",
            **_resource_as_dict,
        )
        srid = geonode_layer.srid
        bbox_polygon = geonode_layer.bbox_polygon
        geonode_layer.full_clean()
        geonode_layer.save(notify=True)
        # geonode_layer.keywords.add(*keywords)
        geonode_layer.set_default_permissions()
        # geonode_layer.extra_metadata.set()
        if bbox_polygon and srid:
            try:
                # Dealing with the BBOX: this is a trick to let GeoDjango storing original coordinates
                Layer.objects.filter(id=geonode_layer.id).update(
                    bbox_polygon=bbox_polygon, srid="EPSG:4326"
                )
                match = re.match(r"^(EPSG:)?(?P<srid>\d{4,6})$", str(srid))
                bbox_polygon.srid = int(match.group("srid")) if match else 4326
                Layer.objects.filter(id=geonode_layer.id).update(
                    ll_bbox_polygon=bbox_polygon, srid=srid
                )
            except Exception as e:
                logger.error(e)

            # Refresh from DB
            geonode_layer.refresh_from_db()
        self._create_ows_link(geonode_layer=geonode_layer, _url=_ows_url)
        return geonode_layer

    def _from_resource_to_layer(self, _resource):
        srs = f"EPSG:{_resource.srs}"
        payload = {
            "name": self._generate_id(_resource.id),
            "store": slugify(self.url)[:255],
            "storeType": "remoteStore",
            "workspace": "remoteWorkspace",
            "alternate": f"{self.workspace.name}:{self._generate_id(_resource.id)}",
            "title": _resource.title,
            "abstract": _resource.abstract,
            "srid": srs,
            "keywords": [_resource.title],
            "ows_url": _resource.id,
        }
        if _resource.bbox:
            payload["bbox_polygon"] = BBOXHelper.from_xy(
                [
                    _resource.bbox[0],
                    _resource.bbox[2],
                    _resource.bbox[1],
                    _resource.bbox[3],
                ]
            ).as_polygon()
        return payload

    def _create_ows_link(self, geonode_layer: Layer, _url: str) -> None:
        Link.objects.get_or_create(
            resource=geonode_layer.resourcebase_ptr,
            url=_url,
            name="OGC:WMS",
            defaults={
                "extension": "html",
                "name": f"{geonode_layer.remote_service.type}: {geonode_layer.store} Service",
                "url": _url,
                "mime": "text/html",
                "link_type": f"{geonode_layer.remote_service.type}",
            },
        )

    def _create_obj(self, _id: str, name: str, descr: str) -> NamedTuple:
        SOSLayer = namedtuple("SosLayer", ["id", "title", "abstract"])
        return SOSLayer(self._generate_id(_id), name, descr)

    def _generate_id(self, _id: str) -> str:
        return slugify(_id)

    def _get_procedure_list(self):
        return [
            item.get("procedure")[0]
            for item in self.parsed_service.get("contents", [])
            if item.get("procedure", [])
        ]

    def _get_procedure_detail(self, single_procedure):
        SOSProcedureDetail = namedtuple(
            "ProcedureDetail",
            [
                "id",
                "title",
                "abstract",
                "offerings",
                "feature_of_interest",
                "bbox",
                "srs",
                "extra",
            ],
        )

        headers = {"Content-type": "application/json", "Accept": "application/json"}

        payload = json.dumps(
            {
                "request": "DescribeSensor",
                "service": "SOS",
                "version": "2.0.0",
                "procedure": f"{single_procedure}",
                "procedureDescriptionFormat": "http://www.opengis.net/sensorml/2.0",
            }
        )

        _response = requests.request(
            "POST", self.url, headers=headers, data=payload
        ).json()
        _xml = _response.get("procedureDescription").get("description")
        # getting the metadata needed
        parser = DescribeSensorParser(
            _xml, sos_service=self.url, procedure_id=single_procedure
        )
        _bbox = None
        srs = "4326"
        bbox = self.get_detailed_procedure(single_procedure).get("observedArea")
        if bbox:
            _bbox = [
                bbox["lowerLeft"][1],
                bbox["lowerLeft"][0],
                bbox["upperRight"][1],
                bbox["upperRight"][0],
            ]
            srs = (
                self.get_detailed_procedure(single_procedure)
                .get("observedArea")
                .get("crs")
                .get("properties")
                .get("href")
                .split("/")[-1]
            )

        return SOSProcedureDetail(
            id=parser.get_id(),
            title=parser.get_short_name(),
            abstract=parser.get_long_name(),
            offerings=parser.get_offerings(),
            feature_of_interest=parser.get_feature_of_interest(),
            bbox=_bbox,
            srs=srs,
            extra=parser.get_extra_metadata(),
        )

    def _set_extra_metadata(self, layer, _resource_detail):
        for mdata in _resource_detail.extra:
            new_m = ExtraMetadata.objects.create(
                resource=layer,
                metadata=mdata,
            )
            layer.metadata.add(new_m)

    def _set_feature_of_interest(self, layer, _resource_detail):
        for data in _resource_detail.feature_of_interest:
            new_m = FeatureOfInterest.objects.create(resource=layer, **data)
            layer.featureofinterest_set.add(new_m)

    def _set_offerings(self, layer, _resource_detail):
        for data in _resource_detail.offerings:
            new_m = Offerings.objects.create(resource=layer, **data)
            layer.offerings_set.add(new_m)


class HandlerDescriptor:
    services_type = {
        "SOS": {"OWS": True, "handler": SosServiceHandler, "label": _("SOS Services")}
    }

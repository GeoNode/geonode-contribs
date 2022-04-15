#########################################################################
#
# Copyright (C) 2022 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################
from dynamic_rest.filters import DynamicFilterBackend, DynamicSortingFilter
from geonode.base.api.filters import DynamicSearchFilter, ExtentFilter
from dynamic_rest.viewsets import DynamicModelViewSet
from geonode.base.api.pagination import GeoNodeApiPagination
from geonode.layers.models import Layer
from geonode_sos.api.serializer import FeatureOfInterestSerializer, SOSSensorSerializer
from geonode_sos.models import FeatureOfInterest
from rest_framework.exceptions import NotFound
from rest_framework.filters import SearchFilter, BaseFilterBackend
from rest_framework.response import Response
from rest_framework import status
from django.contrib.gis.geos import GEOSGeometry
import re

class FOISFilter(BaseFilterBackend):
    """
    Filter the FOIS by the value inside the payload.
    Accept a dictionary where:
     - the key is the Model fiel
     - an array with the value to use for filtering
    """

    def filter_queryset(self, request, queryset, view):
        if request.data:
            _filter = {f"{key}__in": value for key, value in request.data.items()}
            return queryset.filter(**_filter)
        return queryset


class CustomSensorsFilter(SearchFilter):
    def filter_queryset(self, request, queryset, _):
        _filters = request.GET
        if not _filters:
            return queryset

        sos_url = _filters.pop("sos_url", None)
        title = _filters.pop("title", None)
        observable_property = _filters.pop("observable_property", None)
        sensor_name = _filters.pop("sensor_name", None)
        _filter = {}
        if sos_url:
            _filter["remote_service__base_url__icontains"] = sos_url[0]
        if title:
            _filter["title__icontains"] = title[0]
        if sensor_name:
            _filter["name__icontains"] = sensor_name[0]
        if observable_property:
            _filter[
                "extrametadata__metadata__definition__icontains"
            ] = observable_property[0]

        # generating the other filters dynamically
        for _key, _value in _filters.items():
            _filter[f"{_key}__icontains"] = _value
        return queryset.filter(**_filter)


class SOSSensorsViewSet(DynamicModelViewSet):
    filter_backends = [CustomSensorsFilter]
    queryset = Layer.objects.filter(resource_type="sos_sensor").order_by("id")
    serializer_class = SOSSensorSerializer
    pagination_class = GeoNodeApiPagination
    http_method_names = ["get"]


class FeatureOfInterestViewSet(DynamicModelViewSet):
    queryset = FeatureOfInterest.objects.all().order_by('id')
    serializer_class = FeatureOfInterestSerializer
    filter_backends = [
        DynamicFilterBackend, DynamicSortingFilter, DynamicSearchFilter,
        ExtentFilter, FOISFilter
    ]
    pagination_class = GeoNodeApiPagination
    http_method_names = ["get"]

    def retrieve(self, request, pk=None):
        _queryset = self.queryset.filter(pk=pk)
        if not _queryset.exists():
            raise NotFound(
                detail=f"The requested FeatureOfInterest does not exists: {pk}"
            )

        _foi = _queryset.first()
        return Response(
            {
                "id": _foi.id,
                "identifier": _foi.identifier,
                "name": _foi.name,
                "sosUrl": _foi.resource.remote_service.base_url,
                "codespace": _foi.codespace,
                "feature_type": _foi.feature_type,
                "sampled_feature": _foi.sampled_feature,
                "geom": self._get_geojson(_foi),
                "procedure": {
                    "id": _foi.resource.id,
                    "offeringsIDs": _foi.resource.offerings_set.values_list('value', flat=True),
                    "observablePropertiesIDs": [
                        x.get("definition")
                        for x in _foi.resource.extrametadata_set.values_list('metadata', flat=True)
                    ],
                },
            },
            status=status.HTTP_200_OK,
        )

    def _get_geojson(self, _foi):
        # getting the Geometry from the XML with regex. only the GML tags are needed
        import json
        _gml = re.match(r".*?(<gml:.*)</sams.*", _foi.shape_blob)
        return json.loads(GEOSGeometry.from_gml(_gml.groups()[0]).json)

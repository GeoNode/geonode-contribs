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
from django.db.models.query import QuerySet
from dynamic_rest.filters import DynamicFilterBackend, DynamicSortingFilter
from dynamic_rest.viewsets import DynamicModelViewSet
from geonode.base.api.filters import DynamicSearchFilter, ExtentFilter
from geonode.base.api.pagination import GeoNodeApiPagination
from geonode.base.models import ExtraMetadata
from geonode.layers.models import Layer
from geonode.services.models import Service
from geonode_sos.api.filters import CustomSensorsFilter, FOISFilter
from geonode_sos.api.serializer import (FeatureOfInterestSerializer,
                                        SOSObservablePropertiesSerializer,
                                        SOSSensorSerializer,
                                        SOSServiceSerializer)
from dynamic_models.models import ModelSchema


class SOSSensorsViewSet(DynamicModelViewSet):
    filter_backends = [CustomSensorsFilter]
    queryset = Layer.objects.filter(resource_type="sos_sensor").order_by("id")
    serializer_class = SOSSensorSerializer
    pagination_class = GeoNodeApiPagination
    http_method_names = ["get"]


class SOSServicesViewSet(DynamicModelViewSet):
    filter_backends = [CustomSensorsFilter]
    queryset = Service.objects.filter(type="SOS").order_by("id")
    serializer_class = SOSServiceSerializer
    pagination_class = GeoNodeApiPagination
    http_method_names = ["get"]


class SOSObservablePropertyViewSet(DynamicModelViewSet):
    filter_backends = [CustomSensorsFilter]
    queryset = ExtraMetadata.objects.filter(resource__resource_type="sos_sensor").order_by('id')
    serializer_class = SOSObservablePropertiesSerializer
    pagination_class = GeoNodeApiPagination
    http_method_names = ["get"]


class FeatureOfInterestViewSet(DynamicModelViewSet):
    queryset = ModelSchema.objects.all().order_by('id')
    serializer_class = FeatureOfInterestSerializer
    filter_backends = [FOISFilter]
    pagination_class = GeoNodeApiPagination
    http_method_names = ["get"]

    def get_queryset(self, queryset=None):
        data = None
        for _model in ModelSchema.objects.iterator():
            _model_instance = _model.as_model()
            if _model_instance.objects.exists():
                if not data:
                    data = _model_instance.objects.all()
                else:
                    data = data.union(_model_instance.objects.all())

        return data.order_by('id')

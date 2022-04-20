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
from dynamic_rest.serializers import DynamicModelSerializer
from geonode.layers.models import Layer
from urllib.parse import unquote
from rest_framework import serializers
from geonode.services.models import Service
from geonode_sos.models import FeatureOfInterest


class SOSSensorSerializer(DynamicModelSerializer):
    class Meta:
        model = Layer
        fields = (
            "pk",
            "title",
            "sensor_name",
            "sosUrl",
            "offeringsIDs",
            "observablePropertiesIDs",
        )

    sensor_name = serializers.SerializerMethodField()
    sosUrl = serializers.SerializerMethodField()
    offeringsIDs = serializers.SerializerMethodField()
    observablePropertiesIDs = serializers.SerializerMethodField()

    def get_sensor_name(self, obj):
        return unquote(obj.name)

    def get_sosUrl(self, obj):
        return Service.objects.get(layer=obj).base_url

    def get_offeringsIDs(self, obj):
        return [x.value for x in obj.offerings_set.all()]

    def get_observablePropertiesIDs(self, obj):
        return [x.metadata.get("definition") for x in obj.extrametadata_set.all()]


class SOSServiceSerializer(DynamicModelSerializer):
       class Meta:
        model = Service
        fields = "__all__"


class FeatureOfInterestSerializer(DynamicModelSerializer):
    class Meta:
        model = FeatureOfInterest
        fields = ("pk", "identifier", "name", "codespace", "sampled_feature")
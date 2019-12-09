# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2019 OSGeo
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

from __future__ import print_function

import json
import logging

from django.conf import settings
from django.views.generic import TemplateView, View
from django.contrib.gis.gdal import OGRGeometry

from geonode.utils import json_response
from .models import (HazardType, AdministrativeDivision,
                                          RiskAnalysisDymensionInfoAssociation)
from .views import AppAware

from .datasource import GeoserverDataSource

log = logging.getLogger(__name__)


class AdministrativeGeometry(AppAware, View):
    

    def _get_geometry(self, val):
        """
        converts geometry to geojson geom
        """
        g = OGRGeometry(val)
        return json.loads(g.json)

    def _get_properties(self, val):
        return val.export()

    def _make_feature(self, val, app):
        """
        Returns feature from the object

        """
        return {"type": "Feature",
                "properties": self._get_properties(val.set_app(app)),
                "geometry": self._get_geometry(val.geom)
                }


    def get(self, request, adm_code, **kwargs):
        try:
            app = self.get_app()
        except KeyError:
            app = None
        try:
            adm = AdministrativeDivision.objects.get(code=adm_code)
        except AdministrativeDivision.DoesNotExist:
            adm = None
        if adm is None:
            return json_response(errors=["Invalid code"], status=404)

        children = adm.children.all()
        _features = [adm] + list(children)

        features = [self._make_feature(item, app) for item in _features]
        out = {'type': 'FeatureCollection',
               'features': features}
        return json_response(out)
                           

administrative_division_view = AdministrativeGeometry.as_view()

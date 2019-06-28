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

from django.conf import settings
from geonode import get_version


def resource_urls(request):
    """Global values to pass to templates"""
    defaults = dict()

    defaults['GEONODE_CLIENT_LOCATION'] = getattr(
        settings,
        'GEONODE_CLIENT_LOCATION',
        '/static/worldmap/worldmap_client/'
    )
    defaults['USE_HYPERMAP'] = getattr(
        settings,
        'USE_HYPERMAP',
        False
    )
    # TODO disable DB_DATASTORE setting
    defaults['DB_DATASTORE'] = True
    defaults['HYPERMAP_REGISTRY_URL'] = settings.HYPERMAP_REGISTRY_URL
    defaults['MAPPROXY_URL'] = settings.HYPERMAP_REGISTRY_URL
    defaults['SOLR_URL'] = settings.SOLR_URL
    defaults['USE_GAZETTEER'] = settings.USE_GAZETTEER
    defaults['GAZETTEER_SERVICES'] = getattr(
        settings,
        'GAZETTEER_SERVICES',
        'worldmap,geonames,nominatim'
    )
    defaults['GOOGLE_API_KEY'] = settings.GOOGLE_API_KEY
    defaults['GOOGLE_MAPS_API_KEY'] = settings.GOOGLE_MAPS_API_KEY
    defaults['WM_COPYRIGHT_URL'] = getattr(
                                               settings,
                                               'WM_COPYRIGHT_URL',
                                               'http://gis.harvard.edu/'
                                           )
    defaults['WM_COPYRIGHT_TEXT'] = getattr(
                                                settings,
                                                'WM_COPYRIGHT_TEXT',
                                                'Center for Geographic Analysis'
                                            )
    defaults['HYPERMAP_REGISTRY_URL'] = settings.HYPERMAP_REGISTRY_URL

    return defaults

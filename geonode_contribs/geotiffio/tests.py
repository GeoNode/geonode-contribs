# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2016 OSGeo
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
# along with this profgram. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

from .base import GeoNodeLiveTestSupport

import timeout_decorator

import os
import json
import datetime
import urllib2
# import base64
import time
import logging

from StringIO import StringIO
# import traceback
import gisdata
from decimal import Decimal
from lxml import etree
from urlparse import urljoin

from django.conf import settings
from django.test.utils import override_settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.contrib.staticfiles.templatetags import staticfiles
from django.contrib.auth import get_user_model
# from guardian.shortcuts import assign_perm
from geonode.base.populate_test_data import reconnect_signals, all_public
from tastypie.test import ResourceTestCaseMixin

from geonode.qgis_server.models import QGISServerLayer

from geoserver.catalog import FailedRequestError

# from geonode.security.models import *
from geonode.contrib import geotiffio
from geonode.decorators import on_ogc_backend
from geonode.base.models import TopicCategory, Link
from geonode.layers.models import Layer
from geonode.maps.models import Map
from geonode import GeoNodeException, geoserver, qgis_server
from geonode.layers.utils import (
    upload,
    file_upload,
)
from geonode.tests.utils import check_layer, get_web_page

from geonode.geoserver.helpers import cascading_delete, set_attributes_from_geoserver
from geonode.geoserver.signals import gs_catalog
from geonode.utils import check_ogc_backend

from contextlib import closing
from zipfile import ZipFile, ZIP_DEFLATED

LOCAL_TIMEOUT = 300

LOGIN_URL = "/accounts/login/"

logger = logging.getLogger(__name__)


def _log(msg, *args):
    logger.debug(msg, *args)


# Reconnect post_save signals that is disconnected by populate_test_data
reconnect_signals()


def zip_dir(basedir, archivename):
    assert os.path.isdir(basedir)
    with closing(ZipFile(archivename, "w", ZIP_DEFLATED, allowZip64=True)) as z:
        for root, dirs, files in os.walk(basedir):
            # NOTE: ignore empty directories
            for fn in files:
                absfn = os.path.join(root, fn)
                zfn = absfn[len(basedir) + len(os.sep):]  # XXX: relative path
                z.write(absfn, zfn)


@override_settings(SITEURL='http://localhost:8008/')
class GeoTIFFIOTest(GeoNodeLiveTestSupport):
    """
    Tests integration of geotiff.io
    """
    port = 8008

    def testLink(self):
        thefile = os.path.join(gisdata.RASTER_DATA, 'test_grid.tif')
        uploaded = file_upload(thefile, overwrite=True)
        access_token = "8FYB137y87sdfb8b1l8ybf7dsbf"

        # changing settings for this test
        geotiffio.settings.GEOTIFF_IO_ENABLED = True
        geotiffio.settings.GEOTIFF_IO_BASE_URL = "http://app.geotiff.io"

        url = geotiffio.create_geotiff_io_url(uploaded, access_token)
        expected = (
            'http://app.geotiff.io?url='
            'http%3A//localhost%3A8080/geoserver/wcs%3F'
            'service%3DWCS'
            '%26format%3Dimage%252Ftiff'
            '%26request%3DGetCoverage'
            '%26srs%3DEPSG%253A4326'
            '%26version%3D2.0.1'
            '%26coverageid%3Dgeonode%253Atest_grid'
            '%26access_token%3D8FYB137y87sdfb8b1l8ybf7dsbf')
        self.assertTrue(url, expected)

        # Clean up and completely delete the layer
        uploaded.delete()

    def testNoLinkForVector(self):
        thefile = os.path.join(
            gisdata.VECTOR_DATA,
            "san_andres_y_providencia_poi.shp")
        uploaded = file_upload(thefile, overwrite=True)
        access_token = None
        created = geotiffio.create_geotiff_io_url(uploaded, access_token)
        self.assertEqual(created, None)

        # Clean up and completely delete the layer
        uploaded.delete()

    def testNoAccessToken(self):
        thefile = os.path.join(gisdata.RASTER_DATA, 'test_grid.tif')
        uploaded = file_upload(thefile, overwrite=True)
        access_token = None

        # changing settings for this test
        geotiffio.settings.GEOTIFF_IO_ENABLED = True
        geotiffio.settings.GEOTIFF_IO_BASE_URL = "http://app.geotiff.io"

        url = geotiffio.create_geotiff_io_url(uploaded, access_token)
        expected = (
            'http://app.geotiff.io?url='
            'http%3A//localhost%3A8080/geoserver/wcs%3F'
            'service%3DWCS'
            '%26format%3Dimage%252Ftiff'
            '%26request%3DGetCoverage'
            '%26srs%3DEPSG%253A4326'
            '%26version%3D2.0.1'
            '%26coverageid%3Dgeonode%253Atest_grid')
        self.assertTrue(url, expected)

        # Clean up and completely delete the layer
        uploaded.delete()

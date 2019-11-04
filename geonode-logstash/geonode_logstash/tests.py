# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2017 OSGeo
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

import logging
import datetime
import pytz
import binascii
from geonode.tests.base import GeoNodeBaseTestSupport
from django.test.utils import override_settings
from django.core.management import call_command
from models import CentralizedServer
from logstash import LogstashDispatcher
from django_celery_beat.models import PeriodicTask, IntervalSchedule

logger = logging.getLogger(__name__)


class GeonodeLogstashTest(GeoNodeBaseTestSupport):
    """
    Test the geonode_logstash application.
    """
    resources = [
        {
            "hits": 17,
            "name": "/",
            "ogc_hits": 0,
            "url": "/",
            "type": "url",
            "unique_visits": 14,
            "unique_visitors": 5
        },
        {
            "hits": 5,
            "name": "geonode:waterways",
            "ogc_hits": 0,
            "url": "",
            "type": "layer",
            "unique_visits": 2,
            "unique_visitors": 2,
            "publications": 2
        },
        {
            "hits": 4,
            "name": "geonode:railways",
            "ogc_hits": 0,
            "url": "",
            "downloads": 1,
            "type": "layer",
            "unique_visits": 1,
            "unique_visitors": 1,
            "publications": 2
        },
        {
            "hits": 3,
            "name": "geonode:roads",
            "ogc_hits": 0,
            "url": "",
            "type": "layer",
            "unique_visits": 1,
            "unique_visitors": 1,
            "publications": 2
        },
        {
            "hits": 1,
            "name": "San Francisco Transport Map",
            "ogc_hits": 0,
            "url": "",
            "type": "map",
            "unique_visits": 1,
            "unique_visitors": 1,
            "publications": 1
        },
        {
            "hits": 1,
            "name": "Amsterdam Waterways Map",
            "ogc_hits": 0,
            "url": "",
            "type": "map",
            "unique_visits": 1,
            "unique_visitors": 1,
            "publications": 1
        }
    ]
    ua_families = [
        {
            "hits": 174,
            "name": "PC / Ubuntu / Firefox 68.0"
        },
        {
            "hits": 17,
            "name": "Other / Other / Apache-HttpClient 4.5.5"
        },
        {
            "hits": 7,
            "name": "Other / Other / Python Requests 2.22"
        },
        {
            "hits": 1,
            "name": "Spider / Other / Java 8.0.212"
        }
    ]

    def setUp(self):
        super(GeonodeLogstashTest, self).setUp()
        call_command('loaddata', 'metric_data', verbosity=0)
        date_from = datetime.strptime('2018-09-11T20:00:00.000Z', '%Y-%m-%dT%H:%M:%S.%fZ')
        self._valid_from = pytz.utc.localize(date_from)
        date_to = datetime.strptime('2019-09-11T20:00:00.000Z', '%Y-%m-%dT%H:%M:%S.%fZ')
        self._valid_to = pytz.utc.localize(date_to)

    @override_settings(MONITORING_ENABLED=True, USER_ANALYTICS_ENABLED=True)
    def centralized_server_config_test(self):
        CentralizedServer.objects.get_or_create(
            host="192.168.1.95", port="5000", interval=3600
        )
        pts = PeriodicTask.objects.filter(
            name="dispatch-metrics-task",
            task="geonode_logstash.tasks.dispatch_metrics",
        )
        self.assertTrue(pts.count() == 1)
        pt = pts.first()
        self.assertEqual(pt.name, "geonode_logstash.tasks.dispatch_metrics")
        self.assertIsNotNone(pt.interval)
        self.assertEqual(pt.interval.every, 3600)
        self.assertEqual(pt.interval.period, IntervalSchedule.SECONDS)

    @override_settings(MONITORING_ENABLED=True, USER_ANALYTICS_ENABLED=True)
    def test_get_message(self):
        ld = LogstashDispatcher()
        ld._valid_from = self._valid_from
        ld._valid_to = self._valid_to
        for data_type in LogstashDispatcher.DATA_TYPES_MAP:
            msg = ld._get_message(data_type)
            self.assertTrue(msg["instance"])
            self.assertTrue(msg["instance"]["ip"])
            self.assertTrue(msg["instance"]["name"])
            self.assertEqual(msg["format_version"], "1.0")
            self.assertTrue(msg["time"])
            self.assertEqual(msg["time"]["startTime"], "2018-09-11 20:00:00+00:00")
            self.assertEqual(msg["time"]["endTime"], "2019-09-11 20:00:00+00:00")
            if data_type["name"] == "overview":
                self.assertEqual(msg["layers"], 0)
                self.assertEqual(msg["documents"], 0)
                self.assertEqual(msg["maps"], 0)
                self.assertEqual(msg["errors"], 5)
                self.assertEqual(msg["hits"], 201)
                self.assertEqual(msg["unique_visits"], 14)
                self.assertEqual(msg["unique_visitors"], 5)
                self.assertEqual(msg["registered_users"], 4)
            if data_type["name"] == "resources":
                self.assertEqual(msg["resources"], self.resources)
            if data_type["name"] == "countries":
                self.assertTrue(msg["countries"])
            if data_type["name"] == "ua_families":
                self.assertEqual(msg["ua_families"], self.ua_families)

    @override_settings(MONITORING_ENABLED=True, USER_ANALYTICS_ENABLED=True)
    def test_format_record(self):
        ld = LogstashDispatcher()
        ld._valid_from = self._valid_from
        ld._valid_to = self._valid_to
        msg = ld._get_message(LogstashDispatcher.DATA_TYPES_MAP[0])
        formatter = ld._handler.formatter
        compressed = formatter.json_gzip(msg)
        self.assertTrue(binascii.hexlify(compressed), b'1f8b')

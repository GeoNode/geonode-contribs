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
import json
import gzip
import pytz
import time
import socket
import logging
import sqlite3
import pycountry

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
# from django_celery_beat.models import PeriodicTask

from geonode.maps.models import Map
from geonode.layers.models import Layer
from geonode.documents.models import Document
from geonode.monitoring.models import EventType
from geonode.monitoring.collector import CollectorAPI
from geonode.monitoring.views import ExceptionsListView

from logstash_async import EVENT_CACHE
from logstash_async.constants import constants
from logstash_async.database import DatabaseCache
from logstash_async.transport import TcpTransport
from logstash_async.memory_cache import MemoryCache
from logstash_async.worker import LogProcessingWorker
from logstash_async.formatter import LogstashFormatter
from logstash_async.handler import AsynchronousLogstashHandler

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from .models import (
    COUNTRIES_GEODB,
    CentralizedServer
)

log = logging.getLogger(__name__)

IS_ENABLED = settings.MONITORING_ENABLED and settings.USER_ANALYTICS_ENABLED
GZIP_COMPRESSED = getattr(settings, 'USER_ANALYTICS_GZIP', False)

DATA_TYPES_MAP = [
    {
        "name": "overview",
        "metrics": [
            {
                "name": "request.count",
                "hooks": {
                    "hits": "val"
                }
            },
            {
                "name": "request.users",
                "params": {
                    "group_by": "label"
                },
                "hooks": {
                    "unique_visits": "val"
                }
            },
            {
                "name": "request.users",
                "params": {
                    "group_by": "user"
                },
                "hooks": {
                    "unique_visitors": "val"
                }
            }
        ],
        "extra": [
            "registered_users",
            "layers",
            "documents",
            "maps",
            "errors"
        ]
    },
    {
        "name": "resources",
        "metrics": [
            {
                "name": "request.count",
                "params": {
                    "group_by": "resource"
                },
                "hooks": {
                    "name": "resource.name",
                    "type": "resource.type",
                    "url": "resource.href",
                    "hits": "val",
                }
            },
            {
                "name": "request.users",
                "params": {
                    "group_by": "resource_on_label"
                },
                "hooks": {
                    "name": "resource.name",
                    "unique_visits": "val"
                }
            },
            {
                "name": "request.users",
                "params": {
                    "group_by": "resource_on_user"
                },
                "hooks": {
                    "name": "resource.name",
                    "unique_visitors": "val"
                }
            },
            {
                "name": "request.count",
                "params": {
                    "group_by": "resource",
                    "event_type": EventType.EVENT_DOWNLOAD
                },
                "hooks": {
                    "name": "resource.name",
                    "downloads": "val"
                }
            },
            {
                "name": "request.count",
                "params": {
                    "group_by": "resource",
                    "event_type": EventType.EVENT_OWS
                },
                "hooks": {
                    "name": "resource.name",
                    "ogc_hits": "val"
                }
            },
            {
                "name": "request.count",
                "params": {
                    "group_by": "resource",
                    "event_type": EventType.EVENT_PUBLISH
                },
                "hooks": {
                    "name": "resource.name",
                    "publications": "val"
                }
            }
        ],
    },
    {
        "name": "countries",
        "metrics": [
            {
                "name": "request.country",
                "hooks": {
                    "name": "label",
                    "hits": "val"
                }
            }
        ],
    },
    {
        "name": "ua_families",
        "metrics": [
            {
                "name": "request.ua.family",
                "hooks": {
                    "name": "label",
                    "hits": "val"
                }
            }
        ]
    }
]


class LogstashDispatcher(object):
    """
    Dispatcher of GeoNode metric data for Logstash server
    """

    def __init__(self):
        self._centralized_server = None
        self._logger = None
        self._handler = None
        self._interval = 0
        self._collector = None
        self._init_server()

    def _init_server(self):
        """
        Initializing Dispatcher with basic information
        :return: None
        """
        # self.manage_task()
        if IS_ENABLED:
            self._centralized_server = self._get_centralized_server()
            if self._centralized_server:
                # self._centralized_server.sync_periodic_task()
                host = self._centralized_server.host
                port = self._centralized_server.port
                db_path = self._centralized_server.db_path if self._centralized_server.db_path else None
                self._logger = logging.getLogger('geonode-logstash-logger')
                self._logger.setLevel(logging.INFO)
                self._handler = GeonodeAsynchronousLogstashHandler(
                    host, port, database_path=db_path, transport=GeonodeTcpTransport
                )
                self._logger.addHandler(self._handler)
                # self.client_ip = socket.gethostbyname(socket.gethostname())
                self.client_ip = self._centralized_server.local_ip
                self._collector = CollectorAPI()
                self._set_time_range()
        else:
            log.error("Monitoring/analytics disabled, centralized server cannot be set up.")

    # @staticmethod
    # def manage_task():
    #     """
    #     Disable celery task
    #     """
    #     pts = PeriodicTask.objects.filter(
    #         name="dispatch-metrics-task",
    #         task="geonode_logstash.tasks.dispatch_metrics",
    #     )
    #     for pt in pts:
    #         pt.enabled = IS_ENABLED
    #         pt.save()

    @staticmethod
    def _get_centralized_server():
        """
        Get the Centralized Server instance
        :return: Centralized Server
        """
        try:
            cs = CentralizedServer.objects.first()
            return cs
        except CentralizedServer.DoesNotExist:
            log.error("Centralized server not found.")
        except Exception:
            pass

    @staticmethod
    def get_socket_timeout():
        """
        Configuring the SOCKET_TIMEOUT from the model
        :return: SOCKET_TIMEOUT
        """
        cs = LogstashDispatcher._get_centralized_server()
        if cs and cs.socket_timeout is not None:
            log.debug(" ---------------------- socket_timeout %s " % cs.socket_timeout)
            return cs.socket_timeout
        else:
            return constants.SOCKET_TIMEOUT

    @staticmethod
    def get_queue_check_interval():
        """
        Configuring the QUEUE_CHECK_INTERVAL from the model
        :return: QUEUE_CHECK_INTERVAL
        """
        cs = LogstashDispatcher._get_centralized_server()
        if cs and cs.queue_check_interval is not None:
            return cs.queue_check_interval
        else:
            return constants.QUEUE_CHECK_INTERVAL

    @staticmethod
    def get_queue_events_flush_interval():
        """
        Configuring the QUEUED_EVENTS_FLUSH_INTERVAL from the model
        :return: QUEUED_EVENTS_FLUSH_INTERVAL
        """
        cs = LogstashDispatcher._get_centralized_server()
        if cs and cs.queue_events_flush_interval is not None:
            return cs.queue_events_flush_interval
        else:
            return constants.QUEUED_EVENTS_FLUSH_INTERVAL

    @staticmethod
    def get_queue_events_flush_count():
        """
        Configuring the QUEUED_EVENTS_FLUSH_COUNT from the model
        :return: QUEUED_EVENTS_FLUSH_COUNT
        """
        cs = LogstashDispatcher._get_centralized_server()
        if cs and cs.queue_events_flush_count is not None:
            return cs.queue_events_flush_count
        else:
            return constants.QUEUED_EVENTS_FLUSH_COUNT

    @staticmethod
    def get_queue_events_batch_size():
        """
        Configuring the QUEUED_EVENTS_BATCH_SIZE from the model
        :return: QUEUED_EVENTS_BATCH_SIZE
        """
        cs = LogstashDispatcher._get_centralized_server()
        if cs and cs.queue_events_batch_size is not None:
            return cs.queue_events_batch_size
        else:
            return constants.QUEUED_EVENTS_BATCH_SIZE

    @staticmethod
    def get_logstash_db_timeout():
        """
        Configuring the DATABASE_TIMEOUT from the model
        :return: DATABASE_TIMEOUT
        """
        cs = LogstashDispatcher._get_centralized_server()
        if cs and cs.logstash_db_timeout is not None:
            return cs.logstash_db_timeout
        else:
            return constants.DATABASE_TIMEOUT

    def dispatch_metrics(self):
        """
        Sending the messages
        :return: None
        """
        if self._centralized_server:
            if IS_ENABLED:
                for data_type in DATA_TYPES_MAP:
                    try:
                        msg = self._get_message(data_type)
                        if msg:
                            self._logger.info(msg)
                            time.sleep(LogstashDispatcher.get_socket_timeout())
                    except Exception as e:
                        # Note: it catches exceptions on current thread only
                        log.error("Sending data failed: " + str(e))
                # Updating CentralizedServer
                self._update_server()
            else:
                log.error("Monitoring/analytics disabled, centralized server cannot be set up.")
        else:
            log.error("Centralized server not found.")

    def _update_server(self):
        """
        Updating the CentralizedServer instance
        :return: None
        """
        # We have to wait for db to be updated
        time.sleep(LogstashDispatcher.get_logstash_db_timeout())
        # We have to retrieve the "entry_date" of the last event in queue
        last_event_date = self._handler.get_last_entry_date()
        if last_event_date:
            date_time_obj = datetime.strptime(last_event_date, '%Y-%m-%d %H:%M:%S')
            self._centralized_server.last_failed_deliver = pytz.utc.localize(date_time_obj)
        else:
            # If no events in queue then it means all events have been flushed
            self._centralized_server.last_successful_deliver = self._valid_to
            self._centralized_server.last_failed_deliver = None
        self._centralized_server.next_scheduled_deliver = self._valid_to + timedelta(
            seconds=self._centralized_server.interval
        )
        self._centralized_server.save()

    def _set_time_range(self):
        """
        Set up the time range as valid_to/valid_from and interval
        :return: None
        """
        self._valid_to = datetime.utcnow().replace(tzinfo=pytz.utc)
        self._valid_from = self._valid_to - timedelta(
            seconds=self._centralized_server.interval
        )
        self._valid_from = self._valid_from.replace(tzinfo=pytz.utc)
        self._interval = (self._valid_to - self._valid_from).total_seconds()

    def _get_message(self, data_type):
        """
        Retrieving data querying the MetricValue model
        :param data_type: field mapping to keep only interesting information
        :return: data dictionary
        """
        has_data = False
        # Name of the object read by logstash filter (not used in case of "overview")
        data_name = data_type["name"]
        # Define data HEADER
        data = {
            "format_version": "1.0",
            "data_type": data_name,
            "instance": {
                "name": settings.HOSTNAME,
                "ip": self.client_ip
            },
            "time": {
                "startTime": unicode(self._valid_from.isoformat()),
                "endTime": unicode(self._valid_to.isoformat())
            }
        }
        # List data container (not used in case of "overview")
        list_data = []
        # For each metric we want to execute a query
        for metric in data_type["metrics"]:
            # Name omitted in hooks when retrieving no-list data (es. "overview")
            is_list = "name" in metric["hooks"]
            group_by = metric["params"]["group_by"] \
                if "params" in metric and "group_by" in metric["params"] \
                else None
            event_type = EventType.get(metric["params"]["event_type"]) \
                if "params" in metric and "event_type" in metric["params"] \
                else None
            # Retrieving data through the CollectorAPI object
            metrics_data = self._collector.get_metrics_data(
                metric_name=metric["name"],
                valid_from=self._valid_from,
                valid_to=self._valid_to,
                interval=self._interval,
                event_type=event_type,
                group_by=group_by
            )
            if metrics_data:
                # data dictionary updating
                for item in metrics_data:
                    if is_list:
                        name_value = self._build_data(item, metric["hooks"]["name"])
                    item_value = {
                        k: self._build_data(item, v)
                        for k, v in metric["hooks"].iteritems()
                    }
                    if "countries" == data_name:
                        try:
                            country_iso_3 = pycountry.countries.get(
                                alpha_3=name_value).alpha_3
                            center = self._get_country_center(country_iso_3)
                            item_value['center'] = center or ''
                        except BaseException as e:
                            log.error(str(e))
                    if is_list:
                        try:
                            list_item = filter(
                                lambda l_item: l_item["name"] == name_value, list_data
                            )[0]
                            i = list_data.index(list_item)
                            list_data[i].update(item_value)
                        except IndexError:
                            list_data.append(item_value)
                    else:
                        data.update(item_value)
                        has_data = True
        if list_data:
            data.update({data_name: list_data})
            has_data = True
        if "extra" in data_type:
            for extra in data_type["extra"]:
                # For each "extra" entry we have to define a "_get_{extra}" method
                data.update({
                    extra: getattr(self, '_get_{}'.format(extra))()
                })
                has_data = True
        return data if has_data else None

    @staticmethod
    def _build_data(item, key):
        """
        Extract interesting data from the query result
        :param item: query result item
        :param key: interesting key
        :return: interesting value
        """
        data = ""
        try:
            data = int(item[key])
        except KeyError:
            if "." in key:
                k, v = key.split(".")
                data = item[k][v]
            else:
                e = Exception
                e.message("DATA_TYPES_MAP not valid for item {}.".format(str(item)))
                raise e
        except ValueError:
            data = item[key]
        return data

    @staticmethod
    def _get_registered_users():
        """
        Retrieving the users currently registered in GeoNode
        :return: users count
        """
        User = get_user_model()
        return User.objects.count()

    @staticmethod
    def _get_layers():
        """
        Retrieving all the existing layers
        :return: layers count
        """
        return Layer.objects.count()

    @staticmethod
    def _get_maps():
        """
        Retrieving all the existing maps
        :return: maps count
        """
        return Map.objects.count()

    @staticmethod
    def _get_documents():
        """
        Retrieving all the existing documents
        :return: documents count
        """
        return Document.objects.count()

    def _get_errors(self):
        """
        Retrieving errors
        :return: errors count
        """
        return ExceptionsListView().get_queryset(
            valid_to=self._valid_to,
            valid_from=self._valid_from,
            interval=self._interval
        ).count()

    @staticmethod
    def _get_country_center(iso_3):
        output = None
        for _cnt in COUNTRIES_GEODB:
            if iso_3 == _cnt['country.iso_3']:
                output = [float(i) for i in _cnt['country.center']]
                break
        return output

    def test_dispatch(self, host=None, port=None):
        """
        Testing connection to the centralized server
        :return: None
        """
        if self._centralized_server:
            test_msg = {
                "format_version": "1.0",
                "instance": {
                    "name": settings.HOSTNAME,
                    "ip": self.client_ip,
                },
                "test": "test"
            }
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(constants.SOCKET_TIMEOUT)
            test_host = host if host else self._centralized_server.host
            test_port = int(port) if port else self._centralized_server.port
            sock.connect((test_host, test_port))
            compressed_msg = self._handler.formatter.json_gzip(test_msg)
            sock.sendall(compressed_msg)


class GeonodeAsynchronousLogstashHandler(AsynchronousLogstashHandler):
    """
    Extends AsynchronousLogstashHandler to allow gzip compression
    """

    def __init__(self, *args, **kwargs):
        super(GeonodeAsynchronousLogstashHandler, self).__init__(*args, **kwargs)
        self.formatter = GeonodeLogstashFormatter(gzip=GZIP_COMPRESSED)

    def _start_worker_thread(self):
        """
        Super method override to use GeonodeLogProcessingWorker
        :return: None
        """
        if self._worker_thread_is_running():
            return
        AsynchronousLogstashHandler._worker_thread = GeonodeLogProcessingWorker(
            host=self._host,
            port=self._port,
            transport=self._transport,
            ssl_enable=self._ssl_enable,
            ssl_verify=self._ssl_verify,
            keyfile=self._keyfile,
            certfile=self._certfile,
            ca_certs=self._ca_certs,
            database_path=self._database_path,
            cache=EVENT_CACHE,
            event_ttl=self._event_ttl)
        AsynchronousLogstashHandler._worker_thread.start()

    def _format_record(self, record):
        """
        Super method overriding to allow gzip compression
        :param record: message to be formatted
        :return: formatted message
        """
        self._create_formatter_if_necessary()
        return self.formatter.format(record)

    def get_last_entry_date(self):
        """
        Get entry date of the last queued event
        :return: Events
        """
        if self._worker_thread_is_running():
            return self._worker_thread.get_last_queued_event_date()


class GeonodeLogstashFormatter(LogstashFormatter):
    """
    Extends LogstashFormatter to allow gzip compression
    """

    def __init__(self, gzip=False, *args, **kwargs):
        super(GeonodeLogstashFormatter, self).__init__(*args, **kwargs)
        self._gzip = gzip

    def format(self, record):
        """
        Super method overriding to allow json compression
        :param record: message
        :return: gzip compressed message
        :ref: https://stackoverflow.com/questions/8506897/how-do-i-gzip-compress-a-string-in-python
        """
        _output = self._serialize(record.msg)
        if _output is None or len(_output) == 0:
            log.error("No record.msg content found!")
            return None
        if self._gzip:
            _output = self.json_gzip(_output)
        return _output

    def json_gzip(self, data):
        """
        Gzip compression of serialized json
        :param j: input json to be compressed
        :return: compressed object
        """
        if data:
            try:
                _out = StringIO()
                with gzip.GzipFile(fileobj=_out, mode="w") as fout:
                    fout.write(data)
                    fout.flush()
                gzip_j = sqlite3.Binary(_out.getvalue())
            except BaseException as e:
                log.error(str(e))
        return gzip_j


class GeonodeTcpTransport(TcpTransport):
    """
    Extends TcpTransport to avoid loss of messages
    """

    def _send(self, events):
        """
        Super method override to avoid loss of messages
        :param events: events to be processed
        :return: None
        """
        for event in events:
            # To avoid loss of messages we need a short sleep, see the following issues:
            # https://github.com/eht16/python-logstash-async/issues/22
            # https://github.com/eht16/python-logstash-async/issues/33
            time.sleep(0.1)
            self._send_via_socket(event)


class GeonodeLogProcessingWorker(LogProcessingWorker):
    """
    Extends LogProcessingWorker to use GeonodeDatabaseCache
    """

    def _setup_database(self):
        """
        Ovverride of the super method to use GeonodeDatabaseCache
        :return: None
        """
        if self._database_path:
            self._database = GeonodeDatabaseCache(
                path=self._database_path, event_ttl=self._event_ttl
            )
        else:
            self._database = MemoryCache(
                cache=self._memory_cache, event_ttl=self._event_ttl
            )

    def get_last_queued_event_date(self):
        """
        Get the entry date of the last queued event
        :return: last event entry date
        """
        query_fetch = "SELECT `entry_date` FROM `event` ORDER BY `entry_date` DESC LIMIT 1;"
        queued_events_dates = self._database.get_from_query(query_fetch)
        if queued_events_dates:
            return queued_events_dates[0]["entry_date"]


class GeonodeDatabaseCache(DatabaseCache):
    """
    Extends DatabaseCache to have more method
    """

    def get_from_query(self, query_fetch):
        """
        Method to execute query and retrieve results
        :return: query results
        """
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(query_fetch)
            results = cursor.fetchall()
        return results


constants.SOCKET_TIMEOUT = LogstashDispatcher.get_socket_timeout()
constants.QUEUE_CHECK_INTERVAL = LogstashDispatcher.get_queue_check_interval()
constants.QUEUED_EVENTS_FLUSH_INTERVAL = LogstashDispatcher.get_queue_events_flush_interval()
constants.QUEUED_EVENTS_FLUSH_COUNT = LogstashDispatcher.get_queue_events_flush_count()
constants.QUEUED_EVENTS_BATCH_SIZE = LogstashDispatcher.get_queue_events_batch_size()
constants.DATABASE_TIMEOUT = LogstashDispatcher.get_logstash_db_timeout()

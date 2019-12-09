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

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_noop as _
from django_celery_beat.models import PeriodicTask, IntervalSchedule


class CentralizedServer(models.Model):
    """
    Centralized Server for monitoring/analytics metrics data
    """
    host = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        help_text=_("Centralized Server IP address/Host name.")
    )
    port = models.IntegerField(
        null=False,
        blank=False,
        help_text=_("Centralized Server TCP port number.")
    )
    local_ip = models.GenericIPAddressField(
        null=False,
        blank=False,
        protocol='IPv4',
        help_text=_("Local Server IP address.")
    )
    interval = models.IntegerField(
        null=False,
        blank=False,
        default=3600,
        help_text=_("Data aggregation time interval (in seconds).")
    )
    db_path = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        default="logstash.db",
        help_text=_("The local SQLite database to cache log events between emitting and "
                    "transmission to the Logstash server. "
                    "This way log events are cached even across process restarts (and crashes).")
    )
    socket_timeout = models.FloatField(
        null=True,
        blank=True,
        default=5.0,
        help_text=_("Timeout in seconds for TCP connections.")
    )
    queue_check_interval = models.FloatField(
        null=True,
        blank=True,
        default=2.0,
        help_text=_("Interval in seconds to check the internal queue for new messages to be cached in the database.")
    )
    queue_events_flush_interval = models.FloatField(
        null=True,
        blank=True,
        default=0.1,
        help_text=_("Interval in seconds to send cached events from the database to Logstash.")
    )
    queue_events_flush_count = models.IntegerField(
        null=True,
        blank=True,
        default=50,
        help_text=_("Count of cached events to send from the database to Logstash; "
                    "events are sent to Logstash whenever QUEUED_EVENTS_FLUSH_COUNT or "
                    "QUEUED_EVENTS_FLUSH_INTERVAL is reached, whatever happens first.")
    )
    queue_events_batch_size = models.IntegerField(
        null=True,
        blank=True,
        default=50,
        help_text=_("Maximum number of events to be sent to Logstash in one batch. "
                    "Depending on the transport, this usually means a new connection to the Logstash is "
                    "established for the event batch.")
    )
    logstash_db_timeout = models.FloatField(
        null=True,
        blank=True,
        default=5.0,
        help_text=_("Timeout in seconds to 'connect' the SQLite database.")
    )
    last_successful_deliver = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Timestamp of the last successful deliver.")
    )
    next_scheduled_deliver = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Timestamp of the next scheduled deliver.")
    )
    last_failed_deliver = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Timestamp of the last failed deliver.")
    )

    def save(self, *args, **kwargs):
        """
        Overriding the 'save' super method.
        We have to sync PeriodicTask with CentralizedServer
        """
        self.sync_periodic_task()
        super(CentralizedServer, self).save(*args, **kwargs)

    def sync_periodic_task(self):
        """
        Sync django_celery_beat
        """
        if settings.MONITORING_ENABLED and settings.USER_ANALYTICS_ENABLED:
            try:
                i, _ci = IntervalSchedule.objects.get_or_create(
                    every=self.interval, period=IntervalSchedule.SECONDS
                )
            except IntervalSchedule.MultipleObjectsReturned:
                i = IntervalSchedule.objects.filter(
                    every=self.interval, period=IntervalSchedule.SECONDS
                ).first()
            try:
                pt, _cpt = PeriodicTask.objects.get_or_create(
                    name="dispatch-metrics-task",
                    task="geonode_logstash.tasks.dispatch_metrics",
                )
            except PeriodicTask.MultipleObjectsReturned:
                pt = PeriodicTask.objects.filter(
                    name="dispatch-metrics-task",
                    task="geonode_logstash.tasks.dispatch_metrics",
                ).first()
            pt.interval = i
            pt.enabled = True
            pt.save()
        else:
            # When MONITORING_ENABLED=True and USER_ANALYTICS_ENABLED=False we have to disable the task
            pts = PeriodicTask.objects.filter(
                name="dispatch-metrics-task",
                task="geonode_logstash.tasks.dispatch_metrics",
            )
            for pt in pts:
                pt.enabled = False
                pt.save()

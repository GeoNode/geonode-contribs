# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-04-23 09:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geonode_logstash', '0002_auto_20191209_0714'),
    ]

    operations = [
        migrations.AlterField(
            model_name='centralizedserver',
            name='db_path',
            field=models.CharField(blank=True, default=b'logstash_f7e13a74.db', help_text=b'The local SQLite database to cache log events between emitting and transmission to the Logstash server. This way log events are cached even across process restarts (and crashes).', max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='centralizedserver',
            name='queue_events_batch_size',
            field=models.IntegerField(blank=True, default=10, help_text=b'Maximum number of events to be sent to Logstash in one batch. Depending on the transport, this usually means a new connection to the Logstash is established for the event batch.', null=True),
        ),
        migrations.AlterField(
            model_name='centralizedserver',
            name='queue_events_flush_count',
            field=models.IntegerField(blank=True, default=10, help_text=b'Count of cached events to send from the database to Logstash; events are sent to Logstash whenever QUEUED_EVENTS_FLUSH_COUNT or QUEUED_EVENTS_FLUSH_INTERVAL is reached, whatever happens first.', null=True),
        ),
        migrations.AlterField(
            model_name='centralizedserver',
            name='socket_timeout',
            field=models.FloatField(blank=True, default=20.0, help_text=b'Timeout in seconds for TCP connections.', null=True),
        ),
    ]

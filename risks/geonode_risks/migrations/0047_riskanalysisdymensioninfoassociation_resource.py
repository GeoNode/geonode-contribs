# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geonode_risks', '0046_riskanalysisdymensioninfoassociation_layer_reference_attribute'),
    ]

    operations = [
        migrations.AddField(
            model_name='riskanalysisdymensioninfoassociation',
            name='resource',
            field=models.ForeignKey(blank=True, to='geonode_risks.FurtherResource', null=True),
        ),
    ]

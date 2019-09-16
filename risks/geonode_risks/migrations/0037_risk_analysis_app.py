# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models



def get_default_app():
    from ..models import RiskApp
    return RiskApp.objects.get(name=RiskApp.APP_DATA_EXTRACTION).id

class Migration(migrations.Migration):

    dependencies = [
        ('geonode_risks', '0036_costbenefit_app'),
    ]

    operations = [
        migrations.AddField(
            model_name='riskanalysis',
            name='app',
            field=models.ForeignKey(default=get_default_app, to='geonode_risks.RiskApp'),
            preserve_default=False,
        ),
    ]

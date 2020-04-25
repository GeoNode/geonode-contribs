# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2019-09-18 08:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geonode_risks', '0048_riskanalysisdymensioninfoassociation_scenraio_description'),
    ]

    operations = [
        migrations.RenameField(
            model_name='administrativedivision',
            old_name='geonode_risks_analysis',
            new_name='risks_analysis',
        ),
        migrations.RenameField(
            model_name='dymensioninfo',
            old_name='geonode_risks_analysis',
            new_name='risks_analysis',
        ),
        migrations.AlterModelTable(
            name='administrativedivision',
            table='risks_administrativedivision',
        ),
        migrations.AlterModelTable(
            name='analysistype',
            table='risks_analysistype',
        ),
        migrations.AlterModelTable(
            name='analysistypefurtherresourceassociation',
            table='risks_analysisfurtheresourceassociation',
        ),
        migrations.AlterModelTable(
            name='dymensioninfo',
            table='risks_dymensioninfo',
        ),
        migrations.AlterModelTable(
            name='dymensioninfofurtherresourceassociation',
            table='risks_dymensionfurtheresourceassociation',
        ),
        migrations.AlterModelTable(
            name='furtherresource',
            table='risks_further_resource',
        ),
        migrations.AlterModelTable(
            name='hazardset',
            table='risks_hazardset',
        ),
        migrations.AlterModelTable(
            name='hazardsetfurtherresourceassociation',
            table='risks_hazardsetfurtheresourceassociation',
        ),
        migrations.AlterModelTable(
            name='hazardtype',
            table='risks_hazardtype',
        ),
        migrations.AlterModelTable(
            name='pointofcontact',
            table='risks_pointofcontact',
        ),
        migrations.AlterModelTable(
            name='region',
            table='risks_region',
        ),
        migrations.AlterModelTable(
            name='riskanalysis',
            table='risks_riskanalysis',
        ),
        migrations.AlterModelTable(
            name='riskanalysisadministrativedivisionassociation',
            table='risks_riskanalysisadministrativedivisionassociation',
        ),
        migrations.AlterModelTable(
            name='riskanalysiscreate',
            table='risks_descriptor_files',
        ),
        migrations.AlterModelTable(
            name='riskanalysisdymensioninfoassociation',
            table='risks_riskanalysisdymensioninfoassociation',
        ),
        migrations.AlterModelTable(
            name='riskanalysisimportdata',
            table='risks_data_files',
        ),
        migrations.AlterModelTable(
            name='riskanalysisimportmetadata',
            table='risks_metadata_files',
        ),
    ]
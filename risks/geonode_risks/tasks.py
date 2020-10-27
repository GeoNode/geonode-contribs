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

import StringIO
import traceback

from django.conf import settings
from django.core.mail import send_mail
from django.core.management import call_command

from geonode.celery_app import app

from .models import RiskAnalysis, HazardSet

def create_risk_analysis(input_file, file_ini):
    _create_risk_analysis.apply_async(args=(input_file, file_ini))


@app.task(
    bind=True,
    name='geonode_risks.tasks.create_risk_analysis',
    queue='default',
    countdown=60,
    expires=120,
    acks_late=True,
    retry=True,
    retry_policy={
        'max_retries': 10,
        'interval_start': 0,
        'interval_step': 0.2,
        'interval_max': 0.2,
    })
def _create_risk_analysis(input_file, file_ini):
    out = StringIO.StringIO()
    risk = None
    try:
        call_command('createriskanalysis',
                     descriptor_file=str(input_file).strip(), stdout=out)
        value = out.getvalue()

        risk = RiskAnalysis.objects.get(name=str(value).strip())
        risk.descriptor_file = file_ini
        risk.save()
    except Exception, e:
        value = None
        if risk is not None:
            risk.set_error()
        error_message = "Sorry, the input file is not valid: {}".format(e)
        raise ValueError(error_message)


def import_risk_data(input_file, risk_app, risk_analysis, region, final_name):
    risk_analysis.set_queued()
    _import_risk_data.apply_async(args=(input_file, risk_app.name, risk_analysis.name, region.name, final_name,))


@app.task(
    bind=True,
    name='geonode_risks.tasks.import_risk_data',
    queue='default',
    countdown=60,
    expires=120,
    acks_late=True,
    retry=True,
    retry_policy={
        'max_retries': 10,
        'interval_start': 0,
        'interval_step': 0.2,
        'interval_max': 0.2,
    })
def _import_risk_data(input_file, risk_app_name, risk_analysis_name, region_name, final_name):
        out = StringIO.StringIO()
        risk = None
        try:
            risk = RiskAnalysis.objects.get(name=risk_analysis_name)
            risk.set_processing()
            # value = out.getvalue()
            call_command('importriskdata',
                         commit=False,
                         risk_app=risk_app_name,
                         region=region_name,
                         excel_file=input_file,
                         risk_analysis=risk_analysis_name,
                         stdout=out)
            risk.refresh_from_db()
            risk.data_file = final_name
            risk.save()
            risk.set_ready()
        except Exception, e:
            error_message = "Sorry, the input file is not valid: {}".format(e)
            if risk is not None:
                risk.save()
                risk.set_error()
            raise ValueError(error_message)

def import_risk_metadata(input_file, risk_app, risk_analysis, region, final_name):
    risk_analysis.set_queued()
    _import_risk_metadata.apply_async(args=(input_file, risk_app.name, risk_analysis.name, region.name, final_name,))


@app.task(
    bind=True,
    name='geonode_risks.tasks.import_risk_metadata',
    queue='default',
    countdown=60,
    expires=120,
    acks_late=True,
    retry=True,
    retry_policy={
        'max_retries': 10,
        'interval_start': 0,
        'interval_step': 0.2,
        'interval_max': 0.2,
    })
def _import_risk_metadata(input_file, risk_app_name, risk_analysis_name, region_name, final_name):
        out = StringIO.StringIO()
        risk = None
        try:
            risk = RiskAnalysis.objects.get(name=risk_analysis_name)
            risk.set_processing()
            call_command('importriskmetadata',
                         commit=False,
                         risk_app=risk_app_name,
                         region=region_name,
                         excel_file=input_file,
                         risk_analysis=risk_analysis_name,
                         stdout=out)
            # value = out.getvalue()
            risk.refresh_from_db()
            risk.metadata_file = final_name
            hazardsets = HazardSet.objects.filter(riskanalysis__name=risk_analysis_name,
                                                  country__name=region_name)
            if len(hazardsets) > 0:
                hazardset = hazardsets[0]
                risk.hazardset = hazardset

            risk.save()
            risk.set_ready()
        except Exception, e:
            error_message = "Sorry, the input file is not valid: {}".format(e)
            if risk is not None:
                risk.set_error()
            raise ValueError(error_message)

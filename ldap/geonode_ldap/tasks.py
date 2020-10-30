# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2020 OSGeo
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
from django.core.management import call_command

from geonode.celery_app import app

import logging

logger = logging.getLogger(__name__)


@app.task(
    bind=True,
    name='ldap.geonode_ldap.updateldapusers',
    queue='default',
    countdown=60,
    # expires=120,
    acks_late=True,
    retry=True,
    retry_policy={
        'max_retries': 10,
        'interval_start': 0,
        'interval_step': 0.2,
        'interval_max': 0.2,
    })
def updateldapusers():
    """
    Run management command for updating ldap users with geonode
    """
    call_command('updateldapusers')
    #logger.info('updateldapusers run')


@app.task(
    bind=True,
    name='ldap.geonode_ldap.updateldapgroups',
    queue='default',
    countdown=60,
    # expires=120,
    acks_late=True,
    retry=True,
    retry_policy={
        'max_retries': 10,
        'interval_start': 0,
        'interval_step': 0.2,
        'interval_max': 0.2,
    })
def updateldapgroups():
    """
    Run management command for updating ldap groups with geonode
    """
    call_command('updateldapgroups')
    #logger.info('updateldapgroups run')

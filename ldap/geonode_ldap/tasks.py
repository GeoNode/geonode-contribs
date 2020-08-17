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

from geonode.celery_app import app
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

@app.task(queue='default')
def updateldapusers():
    """
    Run management command for updating ldap users with geonode
    """
    call_command('updateldapusers')
    #logger.info('updateldapusers run')


@app.task(queue='default')
def updateldapgroups():
    """
    Run management command for updating ldap groups with geonode
    """
    call_command('updateldapgroups')
    #logger.info('updateldapgroups run')

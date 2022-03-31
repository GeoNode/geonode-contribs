#########################################################################
#
# Copyright (C) 2022 OSGeo
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
from django import apps


class SOSConfig(apps.AppConfig):
    name = "geonode_sos"

    def ready(self):
        """Finalize setup"""
        run_setup_hooks()
        super(SOSConfig, self).ready()


def run_setup_hooks(*args, **kwargs):
    from django.conf.urls import include, url
    from geonode.urls import urlpatterns

    urlpatterns += [
        url(r"^", include("geonode_sos.api.urls")),
    ]

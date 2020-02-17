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

from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from geonode_logstash.models import CentralizedServer
from geonode_logstash.logstash import LogstashDispatcher

csrf_protect_m = method_decorator(csrf_protect)


@admin.register(CentralizedServer)
class CentralizedServerAdmin(admin.ModelAdmin):
    list_display = (
        'host', 'port', 'interval', 'last_successful_deliver',
        'next_scheduled_deliver', 'last_failed_deliver'
    )
    list_filter = ('host', )
    readonly_fields = [
        'last_successful_deliver', 'next_scheduled_deliver', 'last_failed_deliver'
    ]
    change_form_template = "admin/centralized_server_change_form.html"

    host = None
    port = None

    def _test_connection(self, host, port):
        ld = LogstashDispatcher()
        ld.test_dispatch(host, port)

    @csrf_protect_m
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        # Exposing messages to the user once the connection have been tested
        if "_test-connection" in request.POST:
            try:
                self.host = request.POST["host"]
                self.port = request.POST["port"]
                self._test_connection(self.host, self.port)
                self.message_user(
                    request, "Connection test ends with success.", level=messages.INFO
                )
            except Exception as e:
                self.message_user(
                    request, "Connection test fails: {}.".format(e), level=messages.ERROR
                )
            return HttpResponseRedirect(".")
        else:
            return super(CentralizedServerAdmin, self).changeform_view(
                request, object_id, form_url, extra_context
            )

    def get_form(self, request, obj=None, **kwargs):
        # Prepopulated host/port once the connection have been tested
        # (by default obj properties are used)
        if obj and self.host and self.port:
            obj.host = self.host
            obj.port = self.port
        return super(CentralizedServerAdmin, self).get_form(
            request, obj=obj, **kwargs
        )

    def has_add_permission(self, request):
        # Avoid adding more than one record
        base_add_permission = super(CentralizedServerAdmin, self).has_add_permission(request)
        if base_add_permission:
            if CentralizedServer.objects.count():
                return False
        return True

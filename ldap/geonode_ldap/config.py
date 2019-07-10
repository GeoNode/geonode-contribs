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
from django.template.defaultfilters import slugify
from django_auth_ldap import config


class GeonodeNestedGroupOfNamesType(config.NestedGroupOfNamesType):
    """Reimplemented in order to truncate group names to 50 characters

    This is needed since geonode's ``groups.GroupProfile`` model mandates
    that the group's ``title`` and ``slug`` fields be at most 50 chars.

    """

    def group_name_from_info(self, group_info):
        name = super(GeonodeNestedGroupOfNamesType, self).group_name_from_info(
            group_info)
        safe_name = slugify(name)[:50]
        return safe_name

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
"""Custom utilities for managing LDAP logins"""

from django.template.defaultfilters import slugify

from django_auth_ldap import backend
import ldap

from . import settings


def get_ldap_groups_map(user=None):
    """Return a dict with group_slug, group_name for each LDAP group

    If ``user`` is provided, returns only the groups that the user is a member
    of in LDAP.

    """

    ldap_backend = backend.LDAPBackend()
    conn = ldap.initialize(ldap_backend.settings.SERVER_URI)
    conn.simple_bind_s(
        ldap_backend.settings.BIND_DN,
        ldap_backend.settings.BIND_PASSWORD
    )
    if user:
        filter_ = _get_ldap_groups_filter(user, ldap_backend)
    else:
        filter_ = "{}".format(settings.LDAP_GROUP_PROFILE_FILTERSTR)
    remote_groups = conn.search_s(
        base=ldap_backend.settings.GROUP_SEARCH.base_dn,
        scope=ldap.SCOPE_SUBTREE,
        filterstr=filter_
    )
    result = {}
    for cn, attributes in remote_groups:
        group_name = " ".join(
            attributes[settings.LDAP_GROUP_NAME_ATTRIBUTE])
        sanitized_name = sanitize_group_name(group_name)
        result[slugify(sanitized_name)] = {
            "original": group_name,
            "sanitized": sanitized_name,
        }
    return result


def sanitize_group_name(name):
    """Return a name that is suitable for use when creating geonode groups

    Geonode currently uses two group types:

    * standard ``django.contrib.auth.models.Group``

    * custom ``geonode.groups.models.GroupProfile`` - this model also manages
      user memberships, through  the ``geonode.groups.models.GroupMember``
      class. These memberships are used for the UI, but they are not used for
      enforcing permissions - the standard ``Group`` and its relation to the
      user model is used for that

    Geonode ``GroupProfile`` titles and slugs are restricted to 50 chars
    and the ``Group`` names are set from the ``GroupProfile.slug``

    """

    sanitized_name = name[:50]
    return sanitized_name


def _get_ldap_groups_filter(user, ldap_backend):
    if not hasattr(user, "ldap_user"):
        user = ldap_backend.populate_user(user.username)
    return "(&{}(member={}))".format(
        settings.LDAP_GROUP_PROFILE_FILTERSTR,
        user.ldap_user.dn
    )

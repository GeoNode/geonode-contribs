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
from django.test import TestCase
from django.template.defaultfilters import slugify

import ldap
import mock
import logging

from geonode_ldap import utils, settings

logger = logging.getLogger(__name__)


class LDAPTestCase(TestCase):

    @mock.patch('django_auth_ldap.backend.LDAPBackend', autospec=True)
    @mock.patch('ldap.initialize', autospec=True)
    def test_groups_name_encoding(self, mock_ldap_backend, mock_ldap_conn):
        conn = mock.MagicMock(object).return_value
        conn.simple_bind_s.return_value = []
        group_attrs = dict()
        group_attrs[settings.LDAP_GROUP_NAME_ATTRIBUTE] = [b"foo name", ]
        conn.search_s.side_effect = [[[1, group_attrs]]]
        mock_ldap_conn.side_effect = conn
        mock_ldap_backend.return_value = conn
        results = utils.get_ldap_groups_map()
        logger.error(f"results: {results}")
        self.assertIsNotNone(results)
        sanitized_name = utils.sanitize_group_name(
            b" ".join(group_attrs[settings.LDAP_GROUP_NAME_ATTRIBUTE]).decode("utf-8")
        )
        logger.error(f"sanitized_name: {sanitized_name}")
        self.assertIsNotNone(sanitized_name)
        self.assertTrue(slugify(sanitized_name) in results)

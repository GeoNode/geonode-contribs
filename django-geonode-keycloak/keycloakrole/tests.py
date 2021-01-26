from django.conf import settings
from django.test import TestCase
from unittest.mock import MagicMock
from geonode.tests.base import GeoNodeBaseTestSupport

from geonode.groups.models import GroupProfile
from .models import KeycloakRole
from . import helper


class KeycloakRoleTest(GeoNodeBaseTestSupport):

    def test_deleting_group_leads_to_deletion_of_role(self):
        group_test1 = GroupProfile.objects.create(title='test 1', slug='test1', description='test1')
        KeycloakRole.objects.create(keycloak_id='test1', name='test 1', group=group_test1)

        GroupProfile.objects.filter(slug='test1').delete()

        try:
            role_is_none = KeycloakRole.objects.get(keycloak_id='test1')
        except KeycloakRole.DoesNotExist:
            role_is_none = None

        self.assertEqual(None, role_is_none)

    def test_delete_role_leads_to_group_still_existing(self):
        group_test2 = GroupProfile.objects.create(title='test 2', slug='test2', description='test2')
        KeycloakRole.objects.create(keycloak_id='test2', name='test 2', group=group_test2)

        KeycloakRole.objects.filter(keycloak_id='test2').delete()
        group = GroupProfile.objects.get(slug='test2')

        self.assertEqual('test2', group.slug)


class MockPostRequest:

    def json(self):
        return {'access_token': 'TOKEN'}


class MockGetRequest:

    def json(self):
        return {'hello': 'world'}


class KeycloakRequestMockTest(TestCase):

    def test_post_call(self):
        BASE_URL = settings.KEYCLOAK_HOST_URL
        url = f'{BASE_URL}/auth/realms/master/protocol/openid-connect/token'
        data = {
            'client_id': settings.KEYCLOAK_CLIENT,
            'client_secret': settings.KEYCLOAK_CLIENT_SECRET,
            'grant_type': settings.KEYCLOAK_GRANT_TYPE,
            'scope': settings.KEYCLOAK_SCOPE,
        }

        helper.requests.post = MagicMock(return_value=MockPostRequest())
        ret = helper.get_token()

        helper.requests.post.assert_called_once_with(url=url, data=data)
        assert ret == 'TOKEN'

    def test_get_call(self):
        BASE_URL = settings.KEYCLOAK_HOST_URL

        url = f'{BASE_URL}/auth/admin/realms/{settings.KEYCLOAK_REALM}/clients/{settings.KEYCLOAK_CLIENT_ID}/roles'
        headers = {
            'Authorization': 'Bearer TOKEN',
        }

        helper.requests.get = MagicMock(return_value=MockGetRequest())
        ret = helper.get_roles('TOKEN')

        helper.requests.get.assert_called_once_with(url=url, headers=headers)
        assert ret == {'hello': 'world'}

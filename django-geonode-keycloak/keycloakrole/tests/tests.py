from unittest.mock import MagicMock, patch

from django.conf import settings
from django.test import TestCase
from django.contrib.auth import get_user_model

from geonode.groups.models import GroupProfile, GroupMember
from allauth.socialaccount.models import SocialApp, SocialAccount

from keycloakrole import helpers
from keycloakrole.models import KeycloakRole


BASE_URL = "https://my.keycloak.com/auth"
PROVIDER = "keycloak"
KEY = "01234567-890a-bcde-f012-34567890abcd"
SECRET = "abcdef01-2345-6789-0abc-def012345678"
USER_ID = "11111111-2222-3333-4444-555555555555"
CLIENT = "geonode"
REALM = "geonode-realm"
TOKEN = "ABCDEFG"
BEARER_AUTH_HEADERS = {'Authorization': f"Bearer {TOKEN}"}


# Mocks
class MockResponse(object):
    def raise_for_status(self):
        pass


class MockPostResponse(MockResponse):
    def json(self):
        return {
            'method': 'POST',
            'key': 'value',
            'access_token': TOKEN,
        }


class MockGetResponse(MockResponse):
    def json(self):
        return {
            'method': 'GET',
            'key': 'value',
        }


class MockSocialApp(object):
    provider = PROVIDER
    client_id = CLIENT
    key = KEY
    secret = SECRET


# Tests
class KeycloakRoleHelperAPITest(TestCase):

    @patch.multiple("keycloakrole.helpers.requests",
        get=MagicMock(return_value=MockGetResponse()),
        post=MagicMock(return_value=MockPostResponse()))
    @patch.dict(settings.SOCIALACCOUNT_PROVIDERS, {'keycloak':{'KEYCLOAK_URL': BASE_URL}})
    @patch("keycloakrole.helpers.allauth_configured", new=MagicMock(return_value=True))
    def test_fetch_keycloak_json(self):
        """Test that the helper function that queries the Keycloak REST API creates the correct
        requests and receives the correct response"""

        # test invalid method
        self.assertEqual(helpers.fetch_keycloak_json("endpoint", method='NOEXIST'), {})

        # test GET method
        self.assertEqual(helpers.fetch_keycloak_json("endpoint", method='GET')['method'], 'GET')

        # test POST method
        self.assertEqual(helpers.fetch_keycloak_json("endpoint", method='POST')['method'], 'POST')

    @patch.multiple("keycloakrole.helpers.requests",
        get=MagicMock(return_value=MockGetResponse()),
        post=MagicMock(return_value=MockPostResponse()))
    @patch("keycloakrole.helpers.get_keycloak_socialapp", new=MagicMock(return_value=MockSocialApp()))
    def test_get_token(self):
        """Test that the helper function that fetches a token from Keycloak can do so with
        the correct configuration"""

        settings.SOCIALACCOUNT_PROVIDERS['keycloak'] = {
            'KEYCLOAK_URL': BASE_URL,
            'KEYCLOAK_REALM': REALM,
        }

        self.assertEqual(helpers.get_token(), TOKEN)
        helpers.get_keycloak_socialapp.assert_called_once()
        helpers.requests.post.assert_called_once_with(
            f"{BASE_URL}/realms/{REALM}/protocol/openid-connect/token",
            data={
                'client_id': CLIENT,
                'client_secret': SECRET,
                'grant_type': "client_credentials",
                'scope': "openid roles",
            }
        )
        helpers.requests.get.assert_not_called()

    @patch.multiple("keycloakrole.helpers.requests",
        get=MagicMock(return_value=MockGetResponse()),
        post=MagicMock(return_value=MockPostResponse()))
    @patch("keycloakrole.helpers.get_keycloak_socialapp", new=MagicMock(return_value=MockSocialApp()))
    def test_get_roles(self):
        """Test that the helper function that fetches roles for a particular client from Keycloak can
        do so with the correct configuration"""

        settings.SOCIALACCOUNT_PROVIDERS['keycloak'] = {
            'KEYCLOAK_URL': BASE_URL,
            'KEYCLOAK_REALM': REALM,
        }

        self.assertEqual(
            helpers.get_roles(),
            {
                'method': 'GET',
                'key': 'value',
            }
        )
        helpers.get_keycloak_socialapp.assert_called()  # called twice: once each in get_token() and get_roles()
        helpers.requests.get.assert_called_once_with(
            f"{BASE_URL}/admin/realms/{REALM}/clients/{KEY}/roles",
            headers=BEARER_AUTH_HEADERS,
        )
        helpers.requests.post.assert_called_once() # once for get_token()

    @patch.multiple("keycloakrole.helpers.requests",
        get=MagicMock(return_value=MockGetResponse()),
        post=MagicMock(return_value=MockPostResponse()))
    @patch("keycloakrole.helpers.get_keycloak_socialapp", new=MagicMock(return_value=MockSocialApp()))
    def test_get_roles_for_user_id(self):

        settings.SOCIALACCOUNT_PROVIDERS['keycloak'] = {
            'KEYCLOAK_URL': BASE_URL,
            'KEYCLOAK_REALM': REALM,
        }

        self.assertEqual(
            helpers.get_roles_for_user_id(USER_ID),
            {
                'method': 'GET',
                'key': 'value',
            }
        )
        helpers.get_keycloak_socialapp.assert_called()  # called twice: once each in get_token() and get_roles_for_user_id()
        helpers.requests.get.assert_called_once_with(
            f"{BASE_URL}/admin/realms/{REALM}/users/{USER_ID}/role-mappings/clients/{KEY}",
            headers=BEARER_AUTH_HEADERS,
        )
        helpers.requests.post.assert_called_once()  # once for get_token()

    @patch.multiple("keycloakrole.helpers.requests",
        get=MagicMock(return_value=MockGetResponse()),
        post=MagicMock(return_value=MockPostResponse()))
    @patch("keycloakrole.helpers.get_keycloak_socialapp", new=MagicMock(return_value=MockSocialApp()))
    def test_get_users_with_role(self):
        """Test that the helper function that fetches users from a particular client and role
        from Keycloak can do so with the correct configuration"""

        settings.SOCIALACCOUNT_PROVIDERS['keycloak'] = {
            'KEYCLOAK_URL': BASE_URL,
            'KEYCLOAK_REALM': REALM,
        }

        self.assertEqual(
            helpers.get_users_with_role("role"),
            {
                'method': 'GET',
                'key': 'value',
            }
        )
        helpers.get_keycloak_socialapp.assert_called()  # called twice: once each in get_token() and get_users_with_role()
        helpers.requests.get.assert_called_once_with(
            f"{BASE_URL}/admin/realms/{REALM}/clients/{KEY}/roles/role/users",
            headers=BEARER_AUTH_HEADERS,
        )
        helpers.requests.post.assert_called_once()  # once for get_token()


class KeycloakRoleHelperTest(TestCase):
    """Tests for functions within the keycloakrole.helpers module"""

    def test_verify_uuid_invalid_type(self):
        """Test that verify_uuid returns False for an invalid type"""
        self.assertFalse(helpers.verify_uuid(KEY.encode()))

    def test_verify_uuid_invalid_string(self):
        """Test that verify_uuid returns False for an invalid string"""
        self.assertFalse(helpers.verify_uuid("not a valid uuid"))

    def test_verify_uuid_valid(self):
        """Test that verify_uuid returns True for a valid UUID string"""
        self.assertTrue(helpers.verify_uuid(KEY))

    def test_get_keycloak_socialapp(self):
        """Test that the helper method fetches the SocialApp correctly"""

        # no objects so should throw an error
        self.assertRaises(SocialApp.DoesNotExist, helpers.get_keycloak_socialapp)

        # create a a valid object
        app = SocialApp.objects.create(provider="keycloak")
        self.assertEquals(helpers.get_keycloak_socialapp(), app)

        # delete valid object
        app.delete()
        self.assertRaises(SocialApp.DoesNotExist, helpers.get_keycloak_socialapp)

        # create another valid object with different case
        app = SocialApp.objects.create(provider="Keycloak")
        self.assertEquals(helpers.get_keycloak_socialapp(), app)

        # delete valid object
        app.delete()
        self.assertRaises(SocialApp.DoesNotExist, helpers.get_keycloak_socialapp)

        # create invalid object (but does exist)
        app = SocialApp.objects.create(provider="google")
        self.assertRaises(SocialApp.DoesNotExist, helpers.get_keycloak_socialapp)
        app.delete()

    def test_allauth_configured(self):
        """Test that the helper method checking validity of configuration works"""

        # Initial settings should fail
        self.assertFalse(helpers.allauth_configured())

        # Set valid settings
        settings.INSTALLED_APPS = (
            'keycloakrole',
            'geonode',
            'allauth',
            'allauth.account',
            'allauth.socialaccount',
            'allauth.socialaccount.providers.keycloak',
        )
        settings.SOCIALACCOUNT_PROVIDERS['keycloak'] = {
            'KEYCLOAK_URL': BASE_URL,
            'KEYCLOAK_REALM': REALM,
        }
        
        # should fail as there is no SocialApp set up
        self.assertFalse(helpers.allauth_configured())

        # set up the missing SocialApp
        SocialApp.objects.create(
            provider=PROVIDER,
            key=KEY,
            secret=SECRET,
        )

        # config should now be valid
        self.assertTrue(helpers.allauth_configured())

    def test_get_or_create_keycloak_role(self):
        """Test that the helper function that creates all appropriate model objects for a new Keycloak role
        does so with the correct configuration"""

        helpers.get_or_create_keycloak_role({
            'id': "uid",
            'name': "test_role",
        })

        self.assertRaises(KeycloakRole.DoesNotExist, KeycloakRole.objects.get, uid="uid")

        helpers.get_or_create_keycloak_role({
            'id': "uid",
            'name': "test_role",
            'description': "this is a test role"
        })

        group = GroupProfile.objects.get(title="test_role", description="this is a test role")
        KeycloakRole.objects.get(uid="uid", name="test_role", group=group, description="this is a test role")

    def test_get_profile_from_user_id(self):
        profile = get_user_model().objects.create(id=0, username="profile0")
        SocialAccount.objects.create(user_id=0, uid=USER_ID, user=profile, provider="keycloak")

        self.assertEqual(helpers.get_profile_from_user_id(USER_ID), profile)

    def test_get_profile_from_user_id_invalid(self):
        self.assertIsNone(helpers.get_profile_from_user_id("invalid"))

    def test_get_profile_from_user_id_no_exist(self):
        self.assertIsNone(helpers.get_profile_from_user_id("00000000-0000-0000-0000-000000000000"))

    def test_get_keycloakroles_of_profile(self):
        group = GroupProfile.objects.create(title="profile1_group")
        profile = get_user_model().objects.create(id=1, username="profile1")
        role = KeycloakRole.objects.create(uid="22222222-3333-4444-5555-666666666666", name="profile1_group", group=group)

        GroupMember.objects.create(group=group, user=profile, role=GroupMember.MEMBER)

        queryset = helpers.get_keycloakroles_of_profile(profile)

        self.assertEquals(queryset.count(), 1)
        self.assertEquals(queryset.first(), role)


class KeycloakRoleHelperSyncTest(TestCase):

    roles = [
        {'id': "00000000-0000-0000-0000-000000000000", 'name': "testrole"},
    ]
    users = [
        {'id': "11111111-1111-1111-1111-111111111111"},
        {'id': "22222222-2222-2222-2222-222222222222"},
        {'id': "33333333-3333-3333-3333-333333333333"},
    ]

    @patch.multiple("keycloakrole.helpers",
            allauth_configured=MagicMock(return_value=True),
            get_token=MagicMock(return_value=TOKEN),
            get_roles=MagicMock(return_value=roles),
            get_users_with_role=MagicMock(return_value=[]))
    def test_sync_users_with_no_users(self):
        """Test the sync_users method of the KeycloakRole model when
        there are no users"""

        # case where there are no users in the role
        helpers.synchronise_all()
        self.assertEqual(SocialAccount.objects.count(), 0)
        self.assertEqual(GroupMember.objects.count(), 0)

    @patch.multiple("keycloakrole.helpers",
        allauth_configured=MagicMock(return_value=True),
        get_token=MagicMock(return_value=TOKEN),
        get_roles=MagicMock(return_value=roles),
        get_users_with_role=MagicMock(return_value=[{'invalid': "00000000-0000-0000-0000-000000000000"}]))
    def test_sync_users_with_no_id_user(self):
        """Test the sync_users method of the KeycloakRole model when
        there are users with no ID"""

        # case where there is no 'id' field in the response user object
        self.assertRaises(KeyError, helpers.synchronise_all)
        self.assertEqual(SocialAccount.objects.count(), 0)
        self.assertEqual(GroupMember.objects.count(), 0)

    @patch.multiple("keycloakrole.helpers",
        allauth_configured=MagicMock(return_value=True),
        get_token=MagicMock(return_value=TOKEN),
        get_roles=MagicMock(return_value=roles),
        get_users_with_role=MagicMock(return_value=[{'id': "invalid"}]))
    def test_sync_users_with_invalid_user_id(self):
        """Test the sync_users method of the KeycloakRole model when
        there are invalid user IDs"""

        # case where the 'id field is present but its value is invalid
        helpers.synchronise_all()
        self.assertEqual(SocialAccount.objects.count(), 0)
        self.assertEqual(GroupMember.objects.count(), 0)

    @patch.multiple("keycloakrole.helpers",
        allauth_configured=MagicMock(return_value=True),
        get_token=MagicMock(return_value=TOKEN),
        get_roles=MagicMock(return_value=roles),
        get_users_with_role=MagicMock(return_value=users))
    def test_sync_users_with_user_never_logged_in(self):
        """Test the sync_users method of the KeycloakRole model when
        there a user has never logged in using Keycloak"""

        # case where all values are valid but the users have not logged in before
        # i.e. no SocialAccount or Profile object for these users
        helpers.synchronise_all()
        self.assertEqual(SocialAccount.objects.count(), 0)
        self.assertEqual(GroupMember.objects.count(), 0)

    @patch.multiple("keycloakrole.helpers",
        allauth_configured=MagicMock(return_value=True),
        get_token=MagicMock(return_value=TOKEN),
        get_roles=MagicMock(return_value=roles),
        get_users_with_role=MagicMock(return_value=users))
    def test_sync_users_with_valid_users(self):
        """Test the sync_users method of the KeycloakRole model when
        all users are valid"""

        # case where all values are valid and users have logged in
        # i.e. GroupMember object representing the role binding should get created
        for id, user in enumerate(helpers.get_users_with_role()):
            get_user_model().objects.create(id=id, username=f"person-{id}")
            SocialAccount.objects.create(user_id=id, uid=user['id'], provider="keycloak")

        helpers.synchronise_all()

        role = KeycloakRole.objects.get(name="testrole")
        memberships = GroupMember.objects.filter(group=role.group)

        self.assertEqual(memberships.count(), len(self.users))

        helpers.get_token.assert_called_once()
        helpers.get_roles.assert_called_once_with(token=TOKEN)

    def test_synchronise_user_unconfigured(self):
        """Test synchronise_user funtion without configuration of django-allauth"""

        helpers.synchronise_user(USER_ID)

        self.assertEqual(SocialAccount.objects.count(), 0)
        self.assertEqual(GroupMember.objects.count(), 0)
        self.assertEqual(KeycloakRole.objects.count(), 0)

    def test_synchronise_user_invalid(self):
        """Test synchronise_user function with an invalid user ID"""

        helpers.synchronise_user("invalid")

        self.assertEqual(SocialAccount.objects.count(), 0)
        self.assertEqual(GroupMember.objects.count(), 0)
        self.assertEqual(KeycloakRole.objects.count(), 0)

    @patch.multiple("keycloakrole.helpers",
        allauth_configured=MagicMock(return_value=True),
        get_token=MagicMock(return_value=TOKEN))
    def test_synchronise_user(self):
        """Test synchronise_user function works correctly"""

        profile = get_user_model().objects.create(username="user0")

        SocialAccount.objects.create(uid=USER_ID, user=profile, provider="Keycloak")

        # mock a response that returns one role
        with patch("keycloakrole.helpers.get_roles_for_user_id", new=MagicMock(return_value=self.roles)):
            helpers.synchronise_user(USER_ID)

        role_data = self.roles[0]
        role = KeycloakRole.objects.get(uid=role_data['id'], name=role_data['name'])

        # should not throw any errors
        GroupMember.objects.get(user=profile, group=role.group)

        self.assertEqual(SocialAccount.objects.count(), 1)
        self.assertEqual(KeycloakRole.objects.count(), 1)

        # mock a response that returns no roles
        with patch("keycloakrole.helpers.get_roles_for_user_id", new=MagicMock(return_value=[])):
            helpers.synchronise_user(USER_ID)

        role = KeycloakRole.objects.get(uid=role_data['id'], name=role_data['name'])

        # membership should have been deleted
        self.assertRaises(GroupMember.DoesNotExist, GroupMember.objects.get, user=profile, group=role.group)

        self.assertEqual(SocialAccount.objects.count(), 1)
        self.assertEqual(KeycloakRole.objects.count(), 1)

        self.assertFalse(role.group.group in profile.groups.all())


class KeycloakRoleDeleteCascadeTest(TestCase):
    """Tests for the KeycloakRole model - deletion of roles"""

    def test_deleting_group_leads_to_deletion_of_role(self):
        """Test that the related KeycloakRole object is deleted when a GroupProfile is deleted
        which should get triggered by the on_delete=CASCADE kwarg"""

        group = GroupProfile.objects.create(title='test 1', slug='test1')

        KeycloakRole.objects.create(uid='test1', name='test 1', group=group)

        group.delete()

        self.assertRaises(KeycloakRole.DoesNotExist, KeycloakRole.objects.get, uid="test1")

    def test_delete_role_leads_to_deletion_of_group(self):
        """Test that the related GroupProfile is deleted when a KeycloakRole is deleted
        which should be triggered by the post_delete signal"""

        group = GroupProfile.objects.create(title='test 2', slug='test2')
        role = KeycloakRole.objects.create(uid='test2', name='test 2', group=group)

        role.delete()

        self.assertRaises(GroupProfile.DoesNotExist, GroupProfile.objects.get, slug="test2")

    def test_keycloakrole_delete_groups_setting(self):
        """Test the KEYCLOAKROLE_DELETE_GROUP_ENABLE setting on deletion of a KeycloakRole"""

        settings.KEYCLOAKROLE_DELETE_GROUP_ENABLE = False

        group = GroupProfile.objects.create(title='test 3', slug='test3')
        role = KeycloakRole.objects.create(uid='test3', name='test 3', group=group)

        role.delete()

        self.assertEqual(GroupProfile.objects.get(title="test 3", slug="test3"), group)

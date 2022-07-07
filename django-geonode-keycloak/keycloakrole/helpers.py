import uuid
import logging
import requests

try:
    from simplejson.errors import JSONDecodeError
except ImportError:
    from json import JSONDecodeError

from requests import HTTPError
from urllib.parse import urljoin
from django.conf import settings
from django.utils.text import slugify
from geonode.people.models import Profile
from geonode.groups.models import GroupProfile, GroupMember
from allauth.socialaccount.models import SocialApp, SocialAccount


REQUIRED_APPS = (
    'geonode',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.keycloak',
)


logger = logging.getLogger("geonode")


def verify_uuid(string):
    """Return True if a given string is a valid version 4 UUID"""
    try:
        uuid.UUID(string, version=4)
    except (ValueError, TypeError) as e:
        logger.debug(e)
        return False

    return str(string) == string


def get_keycloak_socialapp():
    """Fetch the django-allauth provider for Keycloak"""
    return SocialApp.objects.get(provider__iexact="keycloak")


def allauth_configured():
    valid = True
    provider = {}

    try:
        provider = settings.SOCIALACCOUNT_PROVIDERS['keycloak']
    except AttributeError:
        logger.warning("SOCIALACCOUNT_PROVIDERS is not configured. Keycloak authentication is unavailable.")
        return False
    except KeyError:
        logger.warning("SOCIALACCOUNT_PROVIDERS is configured but Keycloak is not available as a provider.")
        return False

    if provider.get("KEYCLOAK_URL") is None:
        logger.warning("Keycloak provider is missing KEYCLOAK_URL field.")
        valid = False

    if provider.get("KEYCLOAK_REALM") is None:
        logger.warning("Keycloak provider is missing KEYCLOAK_REALM field.")
        valid = False

    if not all(app in settings.INSTALLED_APPS for app in REQUIRED_APPS):
        logger.warning(f"Missing one or more of the following dependencies: {REQUIRED_APPS.join(' ')}")
        valid = False

    try:
        socialapp = get_keycloak_socialapp()
    except Exception as e:
        logger.warning(f"The Keycloak social app is misconfigured: {e}")
        valid = False
    else:
        valid = valid and verify_uuid(socialapp.key) and verify_uuid(socialapp.secret)

    return valid


def fetch_keycloak_json(endpoint, method='GET', **kwargs):
    """Make a request against Keycloak REST API and return the response JSON"""
    url = urljoin(settings.SOCIALACCOUNT_PROVIDERS['keycloak']['KEYCLOAK_URL'], endpoint)
    make_request = getattr(requests, method.lower(), None)  # get the correct method for the request type

    if make_request:
        resp = make_request(url, **kwargs)

        try:
            resp.raise_for_status()
            return resp.json()
        except (HTTPError, JSONDecodeError) as e:
            logger.exception(e)

    return {}


def get_token():
    """Fetches an access token from the Keycloak REST API"""
    realm = settings.SOCIALACCOUNT_PROVIDERS['keycloak']['KEYCLOAK_REALM']
    socialapp = get_keycloak_socialapp()

    return fetch_keycloak_json(
        endpoint=f"auth/realms/{realm}/protocol/openid-connect/token",
        method='POST',
        data={
            'client_id': socialapp.client_id,
            'client_secret': socialapp.secret,
            'grant_type': "client_credentials",
            'scope': "openid roles",
        }).get("access_token")


def get_roles(token=None):
    """Fetches a list of available roles a user can have for the configured client
    from the Keycloak REST API"""
    realm = settings.SOCIALACCOUNT_PROVIDERS['keycloak']['KEYCLOAK_REALM']
    client_id = get_keycloak_socialapp().key

    return fetch_keycloak_json(
        endpoint=f"auth/admin/realms/{realm}/clients/{client_id}/roles",
        method='GET',
        headers={
            'Authorization': f"Bearer {token or get_token()}",
        })


def get_roles_for_user_id(user_id, token=None):
    """Fetches a list of roles bound to the specific user for the configured client
    from the Keycloak REST API"""
    if not verify_uuid(user_id):
        raise ValueError(f"Could not fetch roles. Invalid user ID: {user_id}")

    realm = settings.SOCIALACCOUNT_PROVIDERS['keycloak']['KEYCLOAK_REALM']
    client_id = get_keycloak_socialapp().key

    return fetch_keycloak_json(
        endpoint=f"auth/admin/realms/{realm}/users/{user_id}/role-mappings/clients/{client_id}",
        method='GET',
        headers={
            'Authorization': f"Bearer {token or get_token()}",
        })


def get_users_with_role(role, token=None):
    """Fetches a list of users of the configured client from the Keycloak REST API"""
    realm = settings.SOCIALACCOUNT_PROVIDERS['keycloak']['KEYCLOAK_REALM']
    client_id = get_keycloak_socialapp().key

    return fetch_keycloak_json(
        endpoint=f"auth/admin/realms/{realm}/clients/{client_id}/roles/{role}/users",
        method='GET',
        headers={
            'Authorization': f"Bearer {token or get_token()}",
        })


def get_or_create_keycloak_role(data):
    """Creates a KeycloakRole and GroupProfile from raw role data from Keycloak"""
    uid = data.get("id")
    name = data.get("name")
    description = data.get("description")

    if uid and name:
        from .models import KeycloakRole

        # Sync GroupProfile object
        group, created = GroupProfile.objects.get_or_create(title=name)
        group.slug = slugify(name)

        try:
            role = KeycloakRole.objects.get(uid=uid)
            role.name = name
        except KeycloakRole.DoesNotExist as e:
            role = KeycloakRole.objects.create(uid=uid, name=name, group=group)
            logger.debug(e)

        # Sync description if one exists
        if description:
            group.description = description
            role.description = description

        group.save()
        role.save()

        return role


def get_profile_from_user_id(user_id):
    """Fetch a Profile object from a Keycloak user ID, if one exists, otherwise returns None"""

    if not verify_uuid(user_id):
        return None

    social_account = None
    try:
        social_account = SocialAccount.objects.get(uid=user_id, provider__iexact="keycloak")
    except SocialAccount.DoesNotExist as e:
        logger.debug(e)
    except KeyError as e:
        logger.exception(e)

    return getattr(social_account, "user", None)


def get_keycloakroles_of_profile(profile):
    """Fetches all KeycloakRole objects that are associated with the given Profile object"""

    from .models import KeycloakRole

    groups = {membership.group for membership in GroupMember.objects.filter(user=profile)}
    queryset = KeycloakRole.objects.filter(group__in=groups)

    return queryset or set()


def synchronise_all():
    """Fetch role and user data from Keycloak and sync with GeoNode groups and users"""

    if not allauth_configured():
        logger.warning("django-allauth must be configured correctly to synchronise roles from Keycloak.")
        return

    token = get_token()  # Retrieves the token from keycloak.
    roles = get_roles(token=token)

    # Create and synchronise all roles/groups that have users bound to them
    for role_data in roles:
        role = get_or_create_keycloak_role(role_data)
        role_name = role_data['name']

        for user in get_users_with_role(role_name, token=token):
            try:
                role.add_user_id(user['id'])
            except Profile.DoesNotExist as e:
                # user has probably not yet logged in so we can ignore
                logger.debug(e)


def synchronise_user(user_id):
    """Fetch role data for a single user from Keycloak and sync with GeoNode groups"""

    if not allauth_configured():
        logger.warning("django-allauth must be configured correctly to synchronise roles from Keycloak.")
        return
    elif not verify_uuid(user_id):
        logger.warning(f"Could not synchronise roles. Invalid user ID: {user_id}")
        return

    token = get_token()
    profile = get_profile_from_user_id(user_id)
    expected_roles = get_roles_for_user_id(user_id, token=token)
    expected_role_uids = {role['id'] for role in expected_roles}

    # Remove roles that have been unbound since last sync
    for role in get_keycloakroles_of_profile(profile):
        if role.uid not in expected_role_uids:
            role.remove_profile(profile)

    # Create and syncrhonise all roles/groups for a single user of those roles
    for role_data in expected_roles:
        role = get_or_create_keycloak_role(role_data)

        if role:
            role.add_user_id(user_id)

    logger.info(f"Keycloak roles of user ID {user_id} have been synchronised with the upstream server.")

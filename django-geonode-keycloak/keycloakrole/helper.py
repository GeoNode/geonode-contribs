import requests

from django.conf import settings

BASE_URL = settings.KEYCLOAK_HOST_URL


# get_token builds the url and constructs the data dictionary.
# It then creates a post request.
# Returns the access token.
def get_token():
    url = f'{BASE_URL}/auth/realms/master/protocol/openid-connect/token'
    data = {
        'client_id': settings.KEYCLOAK_CLIENT,
        'client_secret': settings.KEYCLOAK_CLIENT_SECRET,
        'grant_type': settings.KEYCLOAK_GRANT_TYPE,
        'scope': settings.KEYCLOAK_SCOPE,
    }

    resp = requests.post(url=url, data=data)
    data = resp.json()

    return data["access_token"]


# get_roles builds the url and constructs the header.
# It then creates a get request.
# Returns a dictionary of keycloak roles.
def get_roles(token):
    url = f'{BASE_URL}/auth/admin/realms/{settings.KEYCLOAK_REALM}/clients/{settings.KEYCLOAK_CLIENT_ID}/roles'
    headers = {
        'Authorization': f'Bearer {token}',
    }

    resp = requests.get(url=url, headers=headers)

    return resp.json()

import logging

import requests

from django.conf import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', datefmt='%d-%b-%y %H:%M:%S') 
logger = logging.getLogger(__name__)

def get_token():
    url = f'{settings.KEYCLOAK_URL}/realms/master/protocol/openid-connect/token'
    if settings.KEYCLOAK_USER:
        rqdata = {
            'username': settings.KEYCLOAK_USER,
            'password': settings.KEYCLOAK_PASSWORD,
            'grant_type': 'password',
            'client_id': 'admin-cli'
        }
    else:
        rqdata = {
            'client_id': settings.KEYCLOAK_CLIENT,
            'client_secret': settings.KEYCLOAK_CLIENT_SECRET,
            'grant_type': settings.KEYCLOAK_GRANT_TYPE,
            'scope': settings.KEYCLOAK_SCOPE,
        }
    resp = requests.post(url=url, data=rqdata)
    data = resp.json()
    access_token = data.get('access_token', None)
    if not access_token:
        r = f'{resp.status_code}: {resp.text} for data {rqdata}'
        raise Exception(f'Access token not found in response: {r}')
    return access_token

def get_json(url):
    token = get_token()
    headers = {
        'Authorization': f'Bearer {token}',
    }
    resp = requests.get(url=url, headers=headers)
    return resp.json()

def get_users(max=5000):
    url = f'{settings.KEYCLOAK_URL}/admin/realms/{settings.KEYCLOAK_REALM}/users?max={max}'
    users = get_json(url)
    return users

def flatten_groups(groups):
    flattened = []
    for g in groups:
        sg = g['subGroups']
        g.pop('subGroups')
        flattened.append(g)
        if len(sg):
            flattened += flatten_groups(sg)
    return flattened

def get_groups():
    url = f'{settings.KEYCLOAK_URL}/admin/realms/{settings.KEYCLOAK_REALM}/groups?max=5000'
    groups = get_json(url)
    return groups

def get_roles():
    url = f'{settings.KEYCLOAK_URL}/admin/realms/{settings.KEYCLOAK_REALM}/clients/{settings.KEYCLOAK_CLIENT}/roles'
    roles = get_json(url)
    return roles
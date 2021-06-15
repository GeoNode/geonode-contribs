import os

from geonode.settings import *

KEYCLOAK_URL=os.getenv('KEYCLOAK_URL', None)
KEYCLOAK_CLIENT=os.getenv('KEYCLOAK_CLIENT', None)
KEYCLOAK_CLIENT_ID=os.getenv('KEYCLOAK_CLIENT_ID', None)
KEYCLOAK_CLIENT_SECRET=os.getenv('KEYCLOAK_CLIENT_SECRET', None)
KEYCLOAK_REALM=os.getenv('KEYCLOAK_REALM', None)
KEYCLOAK_USER=os.getenv('KEYCLOAK_USER', None)
KEYCLOAK_PASSWORD=os.getenv('KEYCLOAK_PASSWORD', None)
KEYCLOAK_USER_REALM=os.getenv('KEYCLOAK_USER_REALM', None)

INSTALLED_APPS += ('allauth.socialaccount.providers.keycloak',)

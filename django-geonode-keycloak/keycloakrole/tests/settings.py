from geonode.settings import *

keycloak_apps = (
    'keycloakrole',
    'geonode',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.keycloak',
)

INSTALLED_APPS = (
    *(app for app in INSTALLED_APPS if app not in keycloak_apps),
    *keycloak_apps
)

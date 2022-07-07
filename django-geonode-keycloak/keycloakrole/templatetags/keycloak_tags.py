import logging

from django import template
from django.conf import settings
from allauth.socialaccount.models import SocialApp
from keycloakrole.helpers import get_keycloak_socialapp


register = template.Library()
logger = logging.getLogger("geonode")


def get_keycloak_provider_config():
    providers = getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
    provider = providers.get("keycloak", {})

    return provider


@register.simple_tag
def keycloak_url():
    return get_keycloak_provider_config().get("KEYCLOAK_URL", None)


@register.simple_tag
def keycloak_realm():
    return get_keycloak_provider_config().get("KEYCLOAK_REALM", None)


@register.simple_tag
def keycloak_client():
    try:
        socialapp =  get_keycloak_socialapp()
    except SocialApp.DoesNotExist as e:
        logger.debug(e)
    else:
        return getattr(socialapp, "client_id", None)

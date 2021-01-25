from django import template
from django.conf import settings


register = template.Library()

@register.simple_tag
def get_base():
    return settings.KEYCLOAK_HOST_URL

@register.simple_tag
def get_realm():
    return settings.KEYCLOAK_REALM

@register.simple_tag
def get_client():
    return settings.KEYCLOAK_PUB_CLIENT

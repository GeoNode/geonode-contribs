from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


try:
    LDAP_GROUP_PROFILE_FILTERSTR = settings.GEONODE_LDAP_GROUP_PROFILE_FILTERSTR
except AttributeError:
    raise ImproperlyConfigured(
        "Please set the GEONODE_LDAP_GROUP_PROFILE_FILTERSTR variable")

LDAP_GROUP_NAME_ATTRIBUTE = getattr(
    settings,
    "GEONODE_LDAP_GROUP_NAME_ATTRIBUTE",
    "cn"
)

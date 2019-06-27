from django.conf import settings


LDAP_GROUP_PROFILE_FILTERSTR = getattr(
    settings,
    "GEONODE_LDAP_GROUP_PROFILE_FILTERSTR",
    "(objectClass=*)"
)

LDAP_GROUP_NAME_ATTRIBUTE = getattr(
    settings,
    "GEONODE_LDAP_GROUP_NAME_ATTRIBUTE",
    "cn"
)

from django.template.defaultfilters import slugify
from django_auth_ldap import config


class GeonodeNestedGroupOfNamesType(config.NestedGroupOfNamesType):
    """Reimplemented in order to truncate group names to 50 characters

    This is needed since geonode's ``groups.GroupProfile`` model mandates
    that the group's ``title`` and ``slug`` fields be at most 50 chars.

    """

    def group_name_from_info(self, group_info):
        name = super(GeonodeNestedGroupOfNamesType, self).group_name_from_info(
            group_info)
        safe_name = slugify(name)[:50]
        return safe_name

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import (
    BaseCommand,
)
from django.template.defaultfilters import slugify

from django_auth_ldap.backend import LDAPBackend
import ldap

from geonode.groups import models


class Command(BaseCommand):
    help = (
        "Checks for users marked as 'ldap' validity against the LDAP Tree."
        "Users no longer valid, will be disabled by the command."
    )

    def handle(self, *args, **options):
        backend = LDAPBackend()
        conn = ldap.initialize(backend.settings.SERVER_URI)
        conn.simple_bind_s(
            backend.settings.BIND_DN,
            backend.settings.BIND_PASSWORD
        )
        local_users = get_user_model().objects.filter(
            keywords__name__icontains='ldap'
        ).exclude(is_active=False)
        updated_users = self.update_users(
            conn,
            base_dn=backend.settings.USER_SEARCH.base_dn,
            filterstr=backend.settings.USER_SEARCH.filterstr,
            local_users=local_users
        )

    def update_users(
            self,
            ldap_connection,
            base_dn,
            filterstr,
            local_users
    ):
        """Sync geonode users with information on the LDAP server"""

        result = []
        for _u in local_users:
            cn_filter = filterstr.replace('%(user)s', _u.username)
            self.stdout.write("Processing user CN Filter: {!r}...".format(cn_filter))
            remote_users = ldap_connection.search_s(
                base=base_dn,
                scope=ldap.SCOPE_SUBTREE,
                filterstr=cn_filter
            )

            if not remote_users:
                result.append(_u)
                # Going to diable user since it hasn't any reference on LDAP tree
                _u.is_active = False
                _u.save()
            else:
                for cn, attributes in remote_users:
                    self.stdout.write("Processing user CN: {!r}...".format(cn))
                    self.stdout.write("%s" % attributes)

        return result


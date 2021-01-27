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
        "(Re)create geonode groups and group categories from the LDAP server "
        "used in authentication."
    )

    def handle(self, *args, **options):
        backend = LDAPBackend()
        conn = ldap.initialize(backend.settings.SERVER_URI)
        conn.simple_bind_s(
            backend.settings.BIND_DN,
            backend.settings.BIND_PASSWORD
        )
        if getattr(settings, "GEONODE_LDAP_GROUP_CATEGORY_FILTERSTR", None):
            updated_categories = self.update_categories(
                conn,
                base_dn=backend.settings.GROUP_SEARCH.base_dn,
                filterstr=settings.GEONODE_LDAP_GROUP_CATEGORY_FILTERSTR,
                category_name_attribute=settings.GEONODE_LDAP_GROUP_NAME_ATTRIBUTE
            )
        else:
            updated_categories = None
        updated_groups = self.update_groups(
            conn,
            base_dn=backend.settings.GROUP_SEARCH.base_dn,
            filterstr=settings.GEONODE_LDAP_GROUP_PROFILE_FILTERSTR,
            group_name_attribute=settings.GEONODE_LDAP_GROUP_NAME_ATTRIBUTE,
            category_memberships=updated_categories
        )
        managers = get_user_model().objects.filter(is_superuser=True)
        self.stdout.write("Updating managers...")
        self.update_group_managers(updated_groups, managers)

    def update_categories(
            self,
            ldap_connection,
            base_dn,
            filterstr,
            category_name_attribute
    ):
        """Sync geonode group categories with information on the LDAP server"""

        remote_categories = ldap_connection.search_s(
            base=base_dn,
            scope=ldap.SCOPE_SUBTREE,
            filterstr=filterstr
        )
        result = []
        for cn, attributes in remote_categories:
            self.stdout.write("Processing category CN: {!r}...".format(cn))
            category_name = " ".join(attributes[category_name_attribute])
            description = " ".join(attributes.get("description", category_name))
            category, created = models.GroupCategory.objects.get_or_create(
                name=category_name,
                defaults={
                    "description": description
                }
            )
            result.append((category, attributes["member"]))
            if created:
                self.stdout.write(
                    "Created new group category {!r}".format(category_name))
            category.description = description
            category.save()
        return result

    def update_groups(
            self,
            ldap_connection,
            base_dn,
            filterstr,
            group_name_attribute,
            category_memberships=None
    ):
        """Sync geonode groups with information on the LDAP server"""

        remote_groups = ldap_connection.search_s(
            base=base_dn,
            scope=ldap.SCOPE_SUBTREE,
            filterstr=filterstr
        )
        result = []
        for cn, attributes in remote_groups:
            self.stdout.write("Processing group CN: {!r}...".format(cn))
            group_name = b" ".join(
                attributes[group_name_attribute]).decode("utf-8")
            # group_name = slugify(" ".join(attributes[group_name_attribute]))
            description = b" ".join(
                attributes.get("description", group_name)).decode("utf-8")
            truncated_name = group_name[:50]
            if truncated_name != group_name:
                self.stdout.write(
                    "WARNING: group name is too long and has been "
                    "truncated to {!r}".format(truncated_name)
                )
            group, created = models.GroupProfile.objects.get_or_create(
                title=truncated_name,
                slug=slugify(truncated_name),
                defaults={
                    "description": description
                }
            )
            if created:
                self.stdout.write(
                    "Created new group {!r}, now handling category "
                    "memberships...".format(truncated_name)
                )
            group.description = description
            for group_category, members in category_memberships or []:
                if cn in members:
                    group.categories.add(group_category)
            group.save()
            result.append(group)
        return result

    def update_group_managers(self, groups, managers):
        for group in groups:
            for manager in managers:
                member, created = models.GroupMember.objects.get_or_create(
                    group=group,
                    user=manager
                )
                member.role = models.GroupMember.MANAGER
                member.save()

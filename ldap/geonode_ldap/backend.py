"""Custom auth backend that harmonizes ``django_auth_ldap`` and geonode

This module provides an authentication backend that can be used together with
``django_auth_ldap`` in order to provide group permissions based on LDAP groups

If you just want to connect with an LDAP server for creating users and managing
authentication (login and logout), then you don't need this and
``django_auth_ldap`` is enough, provided that you set the correct variables in
the geonode ``settings.py`` file.

If you want to extract group information from LDAP and map it to geonode
permissions you will need to use the auth backend supplied in this module
(or a similar solution).


Why this module exists
----------------------

``django_auth_ldap`` offers a very flexible and complete way to map groups
to LDAP and use the permissions defined in django - however, geonode has a
non-standard way of managing its groups and users, hence the need for this
custom auth backend class.

In a nutshell, geonode wants to manage group memberships using the
``django.contrib.auth.models.Group`` class (i.e. the usual django way) **and**
also with the ``geonode.groups.models.GroupMember`` class.

"""

import logging
import pprint

from django.db import transaction
from django_auth_ldap import backend
from geonode.groups.models import (
    GroupProfile,
    GroupMember,
)
import ldap

from . import utils

logger = logging.getLogger(__name__)


class GeonodeLdapBackend(backend.LDAPBackend):

    def authenticate_ldap_user(self, ldap_user, password):
        """Returns an authenticated Django user or None.

        Authenticates against the LDAP directory and returns the corresponding
        User object if successful. Returns None on failure.

        This method is called by this backend's ``authenticate()`` method, which
        is what django actually uses.

        This method is only reimplemented because we ultimately want
        django_auth_ldap to create instances of
        ``geonode.people.models.GroupProfile`` instead of vanilla django groups.

        Since the creation of groups is done deeper in
        ``django_auth_ldap.backend._LDAPUser._mirror_groups()``, for a lack of
        a better place to hook into, we need to start reimplementing at this
        level in order to be able to modify it.

        This current approach is certainly a hack. Unfortunately, as long as
        geonode holds group memberships in both
        ``django.contrib.auth.models.Group`` and
        ``geonode.groups.models.GroupMember`` there does not seem to be a clean
        way to map LDAP groups to geonode groups and still be able to use
        geonode's permissions.

        This method is reimplemented in order to provide support for custom
        management of geonode groups. The intent is to reuse code from
        ``django_auth_ldap`` as much as possible. As such, the _LDAPUser class
        is being re-used too. In django_auth_ldap this is the method that starts
        the user and group verification. We notoriously replace the following
        _LDAPUser methods with custom ones:

        * ``_LDAPUser._get_or_create_user()`` - we provide
          ``CustomLdapBackend._get_or_create_user()``, which does the same job
          but takes ``ldap_user`` as an input paremeter instead

        * ``LDAPUser._mirror_groups()`` - we provide
          ``CustomLdapBackend.mirror_groups()`` instead, which takes
          ``ldap_user`` as an input paremeter instead and also has custom logic

        """

        user = None

        try:
            ldap_user._authenticate_user_dn(password)
            ldap_user._check_requirements()
            self._get_or_create_user(ldap_user)

            user = ldap_user._user
        except ldap_user.AuthenticationFailed as e:
            logger.debug(
                "Authentication failed for {}: {}".format(
                    ldap_user._username, e)
            )
        except ldap.LDAPError as e:
            results = backend.ldap_error.send(
                ldap_user.backend.__class__,
                context='authenticate',
                user=ldap_user._user,
                exception=e
            )
            if len(results) == 0:
                logger.warning(
                    "Caught LDAPError while authenticating {}: {}".format(
                        ldap_user._username, pprint.pformat(e)
                    )
                )
        except Exception as e:
            logger.warning(
                "{} while authenticating {}".format(e, ldap_user._username)
            )
            raise

        return user

    def _get_or_create_user(self, ldap_user, force_populate=False):
        """Reimplemented based on django_auth_ldap _LDAPUser.get_or_create_user

        Loads the User model object from the database or creates it if it
        doesn't exist. Also populates the fields, subject to
        AUTH_LDAP_ALWAYS_UPDATE_USER.

        """

        save_user = False

        username = self.ldap_to_django_username(ldap_user._username)

        ldap_user._user, built = self.get_or_build_user(username, ldap_user)
        ldap_user._user.ldap_user = ldap_user
        ldap_user._user.ldap_username = ldap_user._username

        should_populate = (
                force_populate or self.settings.ALWAYS_UPDATE_USER or built)

        if built:
            ldap_user._user.set_unusable_password()
            save_user = True

        if should_populate:
            ldap_user._populate_user()
            save_user = True

            # Give the client a chance to finish populating the user just
            # before saving.
            backend.populate_user.send(
                self.__class__,
                user=ldap_user._user,
                ldap_user=ldap_user
            )

        if save_user:
            ldap_user._user.save()

        # This has to wait until we're sure the user has a pk.
        if self.settings.MIRROR_GROUPS or self.settings.MIRROR_GROUPS_EXCEPT:
            ldap_user._normalize_mirror_settings()
            self._mirror_groups(ldap_user)

    def _mirror_groups(self, ldap_user):
        """Reimplemented in order to generate ``people.GroupProfile`` instances

        Mirrors the user's LDAP groups in the Django database and updates the
        user's membership.

        """

        user = ldap_user._user
        slug_map = utils.get_ldap_groups_map(user)
        profile_slugs_set = frozenset(slug_map.keys())
        current_group_profile_slugs = frozenset(
            user.groups.values_list(
                "groupprofile__slug",
                flat=True
            ).filter(groupprofile__slug__isnull=False)
        )
        MIRROR_GROUPS_EXCEPT = self.settings.MIRROR_GROUPS_EXCEPT
        MIRROR_GROUPS = self.settings.MIRROR_GROUPS

        if isinstance(MIRROR_GROUPS_EXCEPT, (set, frozenset)):
            profile_slugs_set = (
                    (profile_slugs_set - MIRROR_GROUPS_EXCEPT) |
                    (current_group_profile_slugs & MIRROR_GROUPS_EXCEPT)
            )
        elif isinstance(MIRROR_GROUPS, (set, frozenset)):
            profile_slugs_set = (
                    (profile_slugs_set & MIRROR_GROUPS) |
                    (current_group_profile_slugs - MIRROR_GROUPS)
            )
        if profile_slugs_set != current_group_profile_slugs:
            existing_group_profiles = list(GroupProfile.objects.filter(
                slug__in=profile_slugs_set).iterator())
            existing_group_profile_slugs = frozenset(
                profile.slug for profile in existing_group_profiles)
            new_group_profiles = []
            for profile_slug in profile_slugs_set:
                if profile_slug not in existing_group_profile_slugs:
                    profile_names = slug_map.get(profile_slug, {})
                    group_profile, created = GroupProfile.objects.get_or_create(
                        title=profile_names.get("sanitized", profile_slug),
                        slug=profile_slug,
                        defaults={
                            "description": profile_names.get(
                                "original", profile_slug)
                        }
                    )
                    new_group_profiles.append(group_profile)
            replace_user_groups(
                user,
                existing_group_profiles + new_group_profiles
            )


@transaction.atomic
def replace_user_groups(user, group_profiles):
    """Set user group memberships based on the input group_profiles

    This function operates on both types of groups that currently exist in
    geonode:

    - regular ``django.contrib.auth.models.Group`` groups which are needed for
      checking permissions

    - geonode's custom ``geonode.groups.models.GroupProfile`` which are used as
      profiles but also store membership information

    All user memberships related with the ``GroupProfile`` class (which are
    being mediated by the ``GroupMember`` model) are first deleted. The
    companion ``Group`` memberships are also deleted.

    Then new memberships are created according to the profiles specified in the
    ``group_profiles`` parameter and the corresponding ``Group`` memberships
    are also created.

    """

    remove_user_memberships(user)
    for group in group_profiles:
        add_groups_to_user(
            user, group_profile=group, group=group.group)


def remove_user_memberships(user):
    """Remove user from all ``GroupMember`` instances and django groups

    """

    existing_group_profile_memberships = GroupMember.objects.filter(
        user=user).values_list("group__slug", flat=True)
    user.groups.filter(name__in=existing_group_profile_memberships).delete()
    GroupMember.objects.filter(user=user).delete()


def add_groups_to_user(user, group_profile, group):
    """Adds groups to a user.

    This will add both a `django.contrib.auth.models.Group` and a also a
    ``geonode.groups.models.GroupProfile``, by means of creating a
    ``geonode.groups.models.GroupMember``.

    """

    user.groups.add(group)
    GroupMember.objects.create(
        user=user, group=group_profile, role=GroupMember.MEMBER)

import logging

from .helpers import synchronise_user
from .models import KeycloakRole
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_delete
from allauth.account.signals import user_logged_in
from allauth.socialaccount.models import SocialAccount


logger = logging.getLogger("geonode")


@receiver(user_logged_in)
def keycloak_login_hook(request, user, **kwargs):
    """Sync a user's roles from Keycloak on login"""

    if not user:
        logger.warning(f"keycloak_login_hook was called with an invalid Profile: {repr(user)}")
        return

    try:
        social_account = SocialAccount.objects.get(user=user, provider__iexact="keycloak")
    except SocialAccount.DoesNotExist as e:
        logger.warning(f"Could not sync with Keycloak. Could not find SocialAccount matching the Profile {repr(user)}")
    else:
        synchronise_user(social_account.uid)


@receiver(post_delete, sender=KeycloakRole)
def keycloak_cleanup_roles(sender, **kwargs):
    """Delete associated group objects when a KeycloakRole is deleted"""
    role = kwargs.get("instance")

    if role and getattr(settings, "KEYCLOAKROLE_DELETE_GROUP_ENABLE", True):
        # Delete GroupProfile object that was created when the sender was created
        try:
            role.group.group.delete()
            logger.debug(
                f"{repr(role.group.group)}, {repr(role.group)}, and member bindings to those groups have been deleted as a result of {repr(role)} being deleted.")
        except Exception as e:
            logger.exception(e)
    else:
        logger.debug("Roles were not cleaned up as role couldn't be found or KEYCLOAKROLE_DELETE_GROUP_ENABLE is False")

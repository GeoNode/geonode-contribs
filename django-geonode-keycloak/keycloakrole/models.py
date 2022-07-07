import logging

from django.db import models
from geonode.people.models import Profile
from geonode.groups.models import GroupProfile, GroupMember
from keycloakrole.helpers import get_profile_from_user_id


logger = logging.getLogger("geonode")


# Model that defines keycloak role properties
class KeycloakRole(models.Model):

    uid = models.CharField(max_length=36, unique=True)
    name = models.CharField(max_length=50)
    description = models.TextField(null=True)
    group = models.OneToOneField(
        GroupProfile,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name

    def add_user_id(self, user_id):
        """Adds a specific user ID to this role and all associated groups and profiles"""
        self.add_profile(get_profile_from_user_id(user_id))

    def remove_user_id(self, user_id):
        """Remove a specific user ID from this role and all associated groups and profiles"""
        self.remove_profile(get_profile_from_user_id(user_id))

    def add_profile(self, profile):
        """Add a specific profile to this role and all associated groups and profiles"""
        if not profile:
            raise Profile.DoesNotExist(f"Specified profile {repr(profile)} does not exist")

        if self.group.group not in profile.groups.all():
            # Add user to related Group of this KeycloakRole
            profile.groups.add(self.group.group)
            profile.save()

        # Create a new GroupMember binding if one doesn't exist
        # must use try/except as the role field may have been changed by an admin
        try:
            GroupMember.objects.get(group=self.group, user=profile)
        except GroupMember.DoesNotExist as e:
            logger.debug(e)
            GroupMember.objects.create(
                group=self.group,
                user=profile,
                role=GroupMember.MEMBER)

    def remove_profile(self, profile):
        """Remove a specific profile from this role and all assoicated groups and profiles"""
        if profile and self.group in profile.groups.all():
            # Remove user from related Group of this KeycloakRole
            profile.groups.remove(self.group.group)
            profile.save()
        else:
            logger.debug(
                f"Profile {repr(profile)} was not unbound from the {self.name} role as it could not be found or does not have this role")

        # Attempt to delete any GroupMember binding if one exists
        try:
            GroupMember.objects.get(group=self.group, user=profile).delete()
        except GroupMember.DoesNotExist as e:
            logger.debug(e)

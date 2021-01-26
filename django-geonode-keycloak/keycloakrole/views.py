from django.shortcuts import redirect
from django.contrib.admin.views.decorators import staff_member_required

from geonode.groups.models import GroupProfile
from .helper import get_token, get_roles
from .models import KeycloakRole


# Synchronizes the keycloak roles with group profiles.
# Creates new instances of keycloak roles and assigns a profile group to each role.
# If the group does not exists new group will be created.
# If the  keycloak role already exists, it wont be created.
@staff_member_required
def synchronize_roles(request):
    token = get_token()  # Retrieves the token from keycloak.
    roles = get_roles(token)  # Retrieves the roles from keycloak.

    for role in roles:
        # Variable group is assigned a GroupProfile model. If a GroupProfile with the title,
        # slug and description does not exist then it is created otherwise retrieved.
        group, _ = GroupProfile.objects.get_or_create(
            title=role["name"], slug=role["name"], description=role.get("description", ""))

        # The try except statement is used to catch an error DoesNotExist.
        # Retriving a KeycloakRole with provided keycloak_id causes an error when the role with the id does not exists.
        # If the role exists it would continue past the except statement and onto the next role in the loop otherwise
        # if the role does not exist the error would be handled and a new KeycloakRole will be created.
        try:
            KeycloakRole.objects.get(keycloak_id=role["id"])
        except KeycloakRole.DoesNotExist:
            KeycloakRole.objects.create(keycloak_id=role["id"], name=role["name"], group=group)

    return redirect('admin:keycloak-role_keycloakrole_changelist')

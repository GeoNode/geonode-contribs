from django.shortcuts import redirect
from django.contrib.admin.views.decorators import staff_member_required

from .helpers import synchronise_all


@staff_member_required
def synchronize_roles(request):
    """Synchronises the Keycloak roles with GroupProfiles and creates new instances
    of KeycloakRole, assinging the GroupProfile to each KeycloakRole. Does not affect
    existing GroupProfile or KeycloakRole objects"""

    synchronise_all()

    return redirect('admin:keycloakrole_keycloakrole_changelist')

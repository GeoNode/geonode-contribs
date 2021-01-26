from django.contrib import admin

from .models import KeycloakRole


class KeycloakAdmin(admin.ModelAdmin):
    model = KeycloakRole
    change_list_template = 'admin/keycloak-role/keycloakrole/change_list.html'

admin.site.register(KeycloakRole, KeycloakAdmin)

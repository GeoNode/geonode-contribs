from django.apps import AppConfig


class KeycloakConfig(AppConfig):
    name = 'keycloakrole'
    label = 'keycloak-role'
    verbose_name = 'Keycloak'  # Sets the display name within django administration.

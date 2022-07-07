from django.apps import AppConfig


class KeycloakConfig(AppConfig):
    name = 'keycloakrole'
    label = 'keycloakrole'
    verbose_name = 'Keycloak'  # Sets the display name within django administration.

    def ready(self):
        # Load all signal receivers
        from . import receivers

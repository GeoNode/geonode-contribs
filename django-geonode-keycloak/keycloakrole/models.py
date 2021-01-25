from django.db import models

from geonode.groups.models import GroupProfile


# Model that defines keycloak role properties
class KeycloakRole(models.Model):

    keycloak_id = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=50)
    group = models.OneToOneField(
        GroupProfile,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name + ' role'

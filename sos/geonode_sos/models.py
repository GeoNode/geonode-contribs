from django.db import models
from django.utils.translation import ugettext as _

from geonode.layers.models import Layer


class FeatureOfInterest(models.Model):

    name = models.CharField(max_length=255, null=True)
    definition = models.CharField(max_length=2000, null=True)
    value = models.CharField(max_length=2000, null=True)

    resource = models.ForeignKey(
        Layer, null=False, blank=False, on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _("Feature of interest")
        verbose_name_plural = _("Features of interest")

    def __str__(self):
        return self.name


class Offerings(models.Model):

    name = models.CharField(max_length=255, null=True)
    definition = models.CharField(max_length=2000, null=True)
    value = models.CharField(max_length=2000, null=True)

    resource = models.ForeignKey(
        Layer, null=False, blank=False, on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _("Offering")
        verbose_name_plural = _("Offerings")

    def __str__(self):
        return self.name

#########################################################################
#
# Copyright (C) 2022 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################
from django.contrib.gis.db.models import PolygonField
from django.db import models
from django.utils.translation import ugettext as _
from geonode.layers.models import Layer


class FeatureOfInterest(models.Model):

    name = models.CharField(max_length=255, null=True)
    identifier = models.CharField(max_length=2000, null=True)
    codespace = models.CharField(max_length=2000, null=True)
    feature_type = models.CharField(max_length=2000, null=True)
    feature_id = models.CharField(max_length=2000, null=True)
    sampled_feature  = models.CharField(max_length=2000, null=True)
    geometry = PolygonField(null=True, blank=True)

    srs_name = models.CharField(max_length=255, null=True)
    description = models.TextField(
        max_length=2000,
        blank=True,
        null=True
    )
    shape_blob = models.TextField(
        max_length=2000,
        blank=True,
        null=True
    )

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

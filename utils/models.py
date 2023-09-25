from django.contrib.postgres.fields import ArrayField
from django.db import models


class BreadcrumbModel(models.Model):
    url = models.CharField(verbose_name='url',
                           max_length=255,
                           null=True,
                           blank=True)
    utility = ArrayField(models.CharField(
        max_length=255,
        null=True,
        blank=True), null=True, blank=True)

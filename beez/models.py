from django.db import models

from orders.models import Carrier


# Create your models here.
class BeezCarrier(Carrier):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username

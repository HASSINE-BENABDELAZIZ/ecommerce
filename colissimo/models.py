from django.db import models

from orders.models import Carrier


# Create your models here.
class ColissimoCarrier(Carrier):
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)

    def __str__(self):
        return self.username

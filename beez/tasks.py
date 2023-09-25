from celery import shared_task as task

from orders.models import Shipment
from .api import Beezit


@task(name='update_order')
def update_order():
    beez = Beezit()
    for shipment in Shipment.objects.all().exclude(
            order__status__in=["OS", 'D', 'F']):
        try:
            beez.tracking(shipment, shipment.carrier)
        except Exception:
            pass

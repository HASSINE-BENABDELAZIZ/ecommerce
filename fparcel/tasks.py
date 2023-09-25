from celery import shared_task as task, shared_task

from orders.models import Shipment
from .api import Fparcel


@task(name='update_order')
def update_order():
    fp = Fparcel()
    for shipment in Shipment.objects.all().filter(order__status="OS").exclude(
            order__status__in=['D', 'F']):
        try:
            fp.tracking(shipment)
        except Exception:
            pass

import logging

# from django.core.cache import cache
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from droppex.api import DroppexAPI
from utils.mongodb import mongo_db
from .models import Order, OrderItems, OrderExportFilters, OrderExportFiles
from .tasks import export_orders_files


@receiver(pre_save, sender=Order)
def model_pre_save(sender, instance, **kwargs):
    try:
        instance._pre_save_instance = Order.objects.get(id=instance.id)
    except Order.DoesNotExist:
        instance._pre_save_instance = instance


@receiver(signal=post_save, sender=Order)
def model_post_save(sender, instance, created, **kwargs):
    from datetime import datetime
    from django.forms.models import model_to_dict
    db = mongo_db()

    pre_save_instance = model_to_dict(instance._pre_save_instance)
    post_save_instance = model_to_dict(instance)
    dict_item = {"created_at": datetime.now(),
                 "order_status": instance.status,
                 "instance_id": instance.id}
    updates = {}
    for item_key, item_value in post_save_instance.items():

        if item_value != pre_save_instance[item_key]:
            updates.update(
                {item_key: {
                    "new": item_value,
                    "old": pre_save_instance[item_key]
                }})
    if updates and instance.origin == "shipstation":
        db.order_notes.insert_one({"order": instance.id,
                                   "user": None,
                                   "Note": "updated by Shipstation",
                                   "created_at": datetime.now(),
                                   })
    import inspect
    user = None
    try:
        for frame_record in inspect.stack():
            if frame_record[3] == 'get_response':
                request = frame_record[0].f_locals['request']
                user = request.user if request.user.is_authenticated else None
                break
    except Exception as e:
        logging.exception(e)
        pass
    dict_item.update({"updates": updates, "user": user.__str__()})
    if updates:
        pass
        # db.orders.insert_one(dict_item)
    instance.zipcode = instance.client_cite.zipcode if instance.client_cite else instance.zipcode
    if created:
        if user.marketplace:
            m = user.marketplace
            instance.marketplace = m
            instance.expiditeur_deligaiton = m.delegation
            instance.expiditeur_ville = m.ville
            instance.expiditeur_cite = m.cite
            instance.expiditeur_zipcode = m.code_postale

        if "admin" in [obj.name for obj in user.groups.all()]:
            if instance.marketplace:
                instance.order_number = f"{instance.marketplace.name}-{instance.id}"
            else:
                instance.order_number = f"StoreLinkers-{instance.id}"
        else:
            instance.order_number = f"StoreLinkers-{instance.id}"

        if instance.livreur and instance.livreur.name == 'droppex':
            DroppexAPI.ship(instance, instance.livreur)

        instance.save()


@receiver(pre_save, sender=OrderItems, weak=False)
def model_pre_save_OrderItems(sender, instance, **kwargs):
    try:
        instance._pre_save_instance = OrderItems.objects.get(id=instance.id)
    except OrderItems.DoesNotExist:
        instance._pre_save_instance = instance


@receiver(signal=post_save, sender=OrderItems, weak=False)
def post_save_items_link(sender, instance, **kwargs):
    from products.models import Product
    db = mongo_db()
    product = Product.objects.filter(id=instance.original_product_id).values_list("id", "sku")
    if product:
        if instance.sku in product[0]:
            instance.original_order_item_id = int(product[0][0])
            instance.original_product = Product.objects.get(id=int(product[0][0]))
    from datetime import datetime
    from django.forms.models import model_to_dict
    pre_save_instance = model_to_dict(instance._pre_save_instance)
    post_save_instance = model_to_dict(instance)
    dict_item = {"created_at": datetime.now(), "order_status": instance.order.status,
                 "instance_id": instance.order.id}
    updates = {}
    for item_key, item_value in post_save_instance.items():

        if item_value != pre_save_instance[item_key]:
            updates.update(
                {item_key: {
                    "new": item_value,
                    "old": pre_save_instance[item_key]
                }})

    import inspect
    user = None
    try:
        for frame_record in inspect.stack():
            if frame_record[3] == 'get_response':
                request = frame_record[0].f_locals['request']
                user = request.user if request.user.is_authenticated else None
                break
    except Exception as e:
        logging.exception(e)
        pass
    dict_item.update({"updates": updates, "user": user.__str__()})
    if updates:
        db.orders.insert_one(dict_item)


@receiver(signal=post_save, sender=OrderExportFilters, weak=False)
def post_save_export_order(sender, instance, **kwargs):
    import inspect
    user = None
    try:
        for frame_record in inspect.stack():
            if frame_record[3] == 'get_response':
                request = frame_record[0].f_locals['request']
                user = request.user if request.user.is_authenticated else None
                break
    except Exception as e:
        logging.exception(e)
        pass
    export = OrderExportFiles.objects.create(filters=instance, status="in queue", user=user)
    export_orders_files.delay(export_id=export.id)

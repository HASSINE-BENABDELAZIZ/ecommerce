import logging

# from django.core.cache import cache
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from orders.models import OrderItems
from utils.mongodb import mongo_db
from .models import Product


@receiver(pre_save, sender=Product)
def model_pre_save(sender, instance, **kwargs):
    try:
        instance._pre_save_instance = Product.objects.get(id=instance.id)
    except Product.DoesNotExist:
        instance._pre_save_instance = instance


@receiver(signal=post_save, sender=Product)
def model_post_save(sender, instance, created, **kwargs):
    queryset = OrderItems.objects.filter(sku=instance.sku)
    for item in queryset:
        item.original_order_item_id = instance.id
        item.original_product = instance
        item.save()
    from datetime import datetime
    from django.forms.models import model_to_dict
    pre_save_instance = model_to_dict(instance._pre_save_instance)
    post_save_instance = model_to_dict(instance)
    dict_item = {"created_at": datetime.now(), "instance_id": instance.id}
    updates = {}
    for item_key, value in post_save_instance.items():

        if value != pre_save_instance[item_key]:
            updates.update({item_key: {"new": value,
                                       "old": pre_save_instance[item_key]}})
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
    db = mongo_db()
    db.products.insert_one(dict_item)
    if created:
        if user.marketplace:
            instance.marketplace = user.marketplace

        instance.save()

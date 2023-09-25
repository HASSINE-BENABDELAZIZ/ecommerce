import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from utils.mongodb import mongo_db
from .models import User


@receiver(pre_save, sender=User)
def model_pre_save(sender, instance, **kwargs):
    try:
        instance._pre_save_instance = User.objects.get(id=instance.id)
    except User.DoesNotExist:
        instance._pre_save_instance = instance


@receiver(signal=post_save, sender=User)
def model_post_save(sender, instance, created, **kwargs):
    from datetime import datetime
    from django.forms.models import model_to_dict
    pre_save_instance = model_to_dict(instance._pre_save_instance)
    post_save_instance = model_to_dict(instance)
    dict_items = {
        "created_at": datetime.now(),
        "user_email": instance.email,
        "instance_id": instance.id}
    updates = {}
    for item_key, item_value in post_save_instance.items():

        if item_value != pre_save_instance[item_key]:
            if item_key == "avatar":
                try:
                    image1 = post_save_instance[item_key].url
                except Exception:
                    image1 = None
                try:
                    image = pre_save_instance[item_key].url
                except Exception:
                    image = None

                updates.update({"Image": {"new": image1, "old": image}})
            else:
                updates.update(
                    {item_key: {"new": item_value,
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
    dict_items.update({"updates": updates, "user": user.__str__()})
    db = mongo_db()
    db.test1.insert_one(dict_items)

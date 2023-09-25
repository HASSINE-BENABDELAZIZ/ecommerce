import logging
import os
from datetime import datetime

from bson.objectid import ObjectId
from celery import shared_task as task
from celery.utils.log import get_task_logger

from products.models import Product
from utils.mongodb import mongo_db, mongo_update

logger = get_task_logger(__name__)


@task(name='jms_products_api')
def jms_import_products_api(mon_insert_id):
    import requests
    time_now = datetime.now()
    db = mongo_db()
    id_code = None
    if not mon_insert_id:
        id_code = db.product_logs.insert_one(
            {"user": None, "status": "Processing",
             "created_at": time_now, })
    response_next = None
    page = 1
    status = "done"
    while response_next or page == 1:
        response_next = None
        token = os.environ.get('3JMSTOKEN', '')
        headers = {'Authorization': "Token " + token}
        response = requests.get(
            "https://staging3jms.com/api/v1/inventory/?page=" + str(page),
            headers=headers
        )

        try:
            response_next = response.json()['next']
        except Exception as e:
            logging.exception(e)
            response_next = None
        try:
            response_result = response.json()['results']
        except Exception as e:
            logging.exception(e)
            response_result = []
            if page == 1:
                status = "error"
        page += 1
        for i in response_result:
            result = i
            try:
                Product.objects.update_or_create(
                    sku=result["vws_product_sku"],
                    defaults={
                        'name': result["name"],
                        'brand': result["brand"],
                        'weight': result["weight"],
                        'year': result["year"],
                        'price': result["price"],
                        'currency': result["currency"],
                        'bottle_size': result["bottle_size"],
                        'image_url': result["image_url"],
                        'category': result["category"],
                        'subcategory': result["subcategory"],
                        'upc': result["upc"]})
            except Exception as e:
                logging.exception(e)
                pass
    finish_time = datetime.now()
    mongo_update("product_logs",
                 {"_id": ObjectId(
                     mon_insert_id) if mon_insert_id else id_code.inserted_id},
                 {
                     "$set": {
                         "finished_at": finish_time,
                         "duration": (finish_time - time_now).total_seconds(),
                         "status": status}
                 }
                 )

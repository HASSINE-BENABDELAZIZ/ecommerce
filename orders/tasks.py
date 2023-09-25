import logging
import os
from datetime import datetime

from asgiref.sync import async_to_sync
from celery import shared_task as task
from celery.utils.log import get_task_logger
from channels.layers import get_channel_layer
from django.db.models import Q
from xlsxwriter import Workbook

from accounts.models import User
from beez.api import Beezit
from colissimo.api import Colissimo
from gso.api import GSO
from orders.models import Order, OrderItems, OrderImports, OrderNotes, Shipment, OrderExportFiles, Carrier
from products.models import Product
from utils.mongodb import mongo_db, mongo_update, mongo_insert
# from time import sleep
# from django.contrib import messages
from utils.redis_lock import worker_lock_manager
from fparcel.api import Fparcel

logger = get_task_logger(__name__)


def finish_update():
    for order in OrderItems.objects.filter(order__substatus="OC"):
        order.save()


@task(name="update_shipment")
def update_shipment():
    try:
        with worker_lock_manager('update_shipment', 86400) as w_lock:
            if w_lock is False:
                return None
            try:
                carrier = Carrier.objects.get(id=int(os.environ.get("CARRIER_ID")))
            except Exception:
                print("error getting carrier")
            for shipment in Shipment.objects.filter(Q(order__status="OS")):
                try:
                    if shipment.carrier == "fp":
                        api = Fparcel()
                    elif shipment.carrier.carrier == "colissimo":
                        api = Colissimo()
                    elif shipment.carrier.carrier == "beezit":
                        api = Beezit()
                    api.tracking(shipment, carrier)
                except Exception:
                    print(f"error while looking for shipment of {shipment}")
    except Exception:
        pass


@task(name='update_order')
def update_order():
    try:
        with worker_lock_manager('update_order', 86400) as w_lock:
            if w_lock is False:
                return None
            for order in Order.objects.filter(Q(status="NO") | Q(status="AC")):
                order.items = OrderItems.objects.filter(order=int(order.id))
                errors = []

                for item in order.items:
                    if Product.objects. \
                            filter(id=item.original_order_item_id).count() > 0:
                        product = Product.objects.filter(
                            id=item.original_order_item_id)[0]
                        product.stock = product.stock if product.stock else 0
                        if product.stock > item.quantity and not errors:

                            status = "NO"
                            substatus = ""
                            note = "Order moved to new order restock "

                        else:

                            substatus = "OC"
                            errors.append(substatus)
                            status = "AC"
                            note = "Order moved because it's out of stock"
                    else:
                        substatus = "UC"
                        errors.append(substatus)
                        status = "AC"
                        break

                if order.substatus != substatus and \
                        order.status != status or \
                        ("UC" in errors and order.substatus != "UC"):

                    if "UC" in errors:
                        order.substatus = "UC"
                        order.status = "AC"
                        note = "Order have UC item(s)"
                        order.save()
                    else:
                        order.substatus = substatus
                        order.status = status
                        order.save()
                    OrderNotes.objects.create(order=order, note=note)
                    for item in order.items:
                        item.save()
                    for note in OrderNotes.objects.filter(order=order):
                        note.save()
    except Exception:
        pass


@task(name='shipstation_import_api')
def shipstation_import_api():
    try:
        import requests
        time_now = datetime.now()
        db = mongo_db()

        id_code = db.order_shipstation.insert_one({"user": None,
                                                   "status": "Processing",
                                                   "created_at": time_now,
                                                   })
        page = 1
        status = "done"
        response_next = 0
        while int(response_next) > page or page == 1:
            key = os.environ.get('SHIPSTATIONKEY', '')
            secret = os.environ.get('SHIPSTATIONSECRET', '')
            response = requests.get(
                "https://ssapi.shipstation.com/" +
                "orders?orderStatus=awaiting_shipment&page=" + str(page),
                auth=(key, secret),
                headers={'content-type': 'application/json'}
            )
            try:
                response_next = response.json()['pages']
            except Exception as e:
                logging.exception(e)
                response_next = None
            try:
                response_result = response.json()['orders']
            except Exception as e:
                logging.exception(e)
                response_result = []
                if page == 1:
                    status = "error"
            page += 1
            for order_number, order in enumerate(response_result):
                try:
                    result = order
                    order, created = Order.objects.update_or_create(
                        order_number=result["orderNumber"],
                        defaults={"customer_name": result["customerUsername"],
                                  "Street_1": result["shipTo"]["street1"],
                                  "Street_2": result["shipTo"]["street2"],
                                  "City": result["shipTo"]["city"],
                                  "State": result["shipTo"]["state"],
                                  "zip_code": result["shipTo"]["postalCode"][
                                              0:4],
                                  "Phone": result["shipTo"]["phone"],
                                  "status": result["orderStatus"],
                                  "Customer_email": result["customerEmail"],
                                  "origin": "shipstation"

                                  })
                    for item in result["items"]:
                        result = item
                        item1, created1 = OrderItems.objects.update_or_create(
                            order=order,
                            sku=result["sku"],
                            defaults={"name": result["name"],
                                      "quantity": int(
                                          result["quantity"], ),

                                      })

                except Exception as e:
                    logging.exception(e)
                    pass
        finish_time = datetime.now()

        mongo_update("order_shipstation",
                     {"_id": id_code.inserted_id},
                     {
                         "$set": {
                             "finished_at": finish_time,
                             "duration": (finish_time - time_now).total_seconds(),
                             "status": status}
                     })
    except Exception:
        pass


def line_is_valid(line, line_number, mongo_id):
    error_msgs = {}
    if not line[0]:
        error_msgs.update({"order_number": "Order number field is Empty "})
    if not line[1]:
        error_msgs.update({"customer_name": " Customer Name field is Empty "})
    if not line[2]:
        error_msgs.update({"address": " address field is Empty "})
    if not line[4]:
        error_msgs.update({"City": " City Name field is Empty "})
    if not line[5]:
        error_msgs.update({"State": " State field is Empty "})
    else:
        if len(line[5]) != 2:
            error_msgs.update({"State": " Statefield is invalid "})
    if not line[6]:
        error_msgs.update({"Zipcode": " Zipcode is Empty "})

    else:
        if (not line[6].isdigit()) and len(line[6]) > 5:
            error_msgs.update({"Zipcode": " Zipcode is invalid "})
    if not line[10]:
        error_msgs.update({"QTY": " Quantity field is Empty "})
    else:
        try:
            quantity = int(line[10])
        except Exception:
            quantity = 0
        if int(quantity) == 0:
            error_msgs.update({"QTY": " Quantity field is Invalid "})

    if not line[8]:
        error_msgs.update({"SKU": " Item Sku field is Empty "})
    if bool(error_msgs):
        result = {
            "line_number": line_number,
            "errors": error_msgs}

        mongo_update(
            "error_import_logs",
            {"_id": mongo_id},
            {"$push": {"lines": result}}

        )

    error_msgs.update({"bool_result": bool(error_msgs),
                       "line_number": line_number})

    return error_msgs


@task(name='import_orders_files')
def import_orders_files(file_id, user=None):
    user = User.objects.get(id=user)
    f1 = OrderImports.objects.get(id=file_id)
    f1.created_at = datetime.now()
    f1.save()
    errors = 0
    error_logs = mongo_insert("error_import_logs",
                              {"file_id": file_id,
                               "lines": []})
    import csv
    from django.core.files.storage import default_storage
    f = csv.reader(default_storage.open(f1.file.__str__(), 'r'))
    line_number = 0
    for line in f:
        if line_number > 0:
            line_number += 1
            if not line_is_valid(line,
                                 line_number,
                                 error_logs.inserted_id)["bool_result"]:
                order, created = Order.objects.update_or_create(
                    order_number=line[0],
                    defaults={"customer_name": line[1],
                              "Street_1": line[2],
                              "Street_2": line[3],
                              "City": line[4],
                              "State": line[5],
                              "zip_code": line[6],
                              "Phone": line[7],
                              "origin": "csv",
                              "user": user
                              })
                items, created1 = OrderItems.objects.update_or_create(
                    order=order,
                    sku=line[8],
                    defaults={"name": line[9],
                              "quantity": int(line[10]),
                              })
                items.save()
            else:
                errors += 1
        else:
            line_number += 1
    f1.finished_at = datetime.now()
    if errors:
        f1.status = f"Done with {errors} errors"
    else:
        f1.status = "Done"
    f1.save()


def create_xlsx_file(instance, headers: dict, items: list):
    from django.core.files.storage import default_storage
    ref = datetime.now()
    file = default_storage.open(f"export{ref}.xlsx", 'wb')

    with Workbook(file) as workbook:
        worksheet = workbook.add_worksheet()
        worksheet.write_row(row=0, col=0, data=headers.values())
        header_keys = list(headers.keys())
        for index, item in enumerate(items):
            row = map(lambda field_id: item.get(field_id, ''), header_keys)
            worksheet.write_row(row=index + 1, col=0, data=row)
    file.close()

    file = default_storage.open(f"export{ref}.xlsx", 'rb')
    instance.file.save(f"export{ref}.xlsx", file)


channel_layer = get_channel_layer()


@task(name='export_orders_files',
      retry_backoff=5,
      max_retries=7,
      acks_late=True,
      bind=True)
def export_orders_files(self, export_id=None, user=None, orders=None):
    if not export_id:
        instance = OrderExportFiles.objects.create(user=user)
    else:
        instance = OrderExportFiles.objects.get(id=export_id)
    instance.task_id = self.request.id
    instance.save()

    try:
        if not orders:
            orders = Order.objects.filter(Q(
                created_at__range=[instance.filters.creation_date_start, instance.filters.creation_date_finish])
            )
            if instance.filters.order_status:
                orders = orders.filter(Q(status=instance.filters.order_status))
            if instance.filters.state:
                orders = orders.filter(Q(state=instance.filters.order_status))
            if instance.filters.carrier:
                orders.filter(shipment__carrier=instance.filters.carrier)

        total = orders.count()
        instance.status = "processing"
        instance.started_at = datetime.now()
        headers = {
            "Order": "Order Number",
            "Tracking": "Tracking",
            "codeCustomer": "codeCustomer",
            "Name": "Name",
            "Company": "Company",
            "CustomerEmail": "CustomerEmail",
            "Phone": "Phone",
            "AddressLine1": "AddressLine1",
            "AddressLine2": "AddressLine2",
            "City": "City",
            "State": "State",
            "Zipcode": "Zipcode",
            "Extra": "Extra",
        }

        elements = instance.progress if instance.progress else []
        items_size = instance.line_number if instance.line_number else 0
        length_arrived = len(instance.progress) if instance.progress else 0
        for i, order in enumerate(orders[length_arrived::]):
            items = OrderItems.objects.filter(order=order)
            if items.count() > items_size:
                items_size = items.count()
            shipment = Shipment.objects.filter(order=order).last()
            if not shipment:
                shipment = Shipment()
            instance.percentage = (1 - (total - (i + 1 + length_arrived)) / total) * 100
            elements.append(
                {
                    "Order": order.order_number if order.customer_name else "",
                    "Tracking": shipment.tracking_code if shipment.tracking_code else "",
                    "Name": order.customer_name if order.customer_name else "",
                    "Company": order.company if order.company else "",
                    "CustomerEmail": order.customer_email if order.customer_email else "",
                    "Phone": order.phone if order.phone else "",
                    "AddressLine1": order.street_1 if order.street_1 else "",
                    "AddressLine2": order.street_2 if order.street_2 else "",
                    "City": order.city if order.city else "",
                    "State": order.state if order.state else "",
                    "Zipcode": order.zip_code if order.zip_code else "",
                })
            if items:
                for count_item, item in enumerate(items):
                    elements[i].update({
                        f"Item sku #{count_item + 1}": item.sku,
                        f"Item name  #{count_item + 1}": item.name,
                        f"Item quantity  #{count_item + 1}": item.quantity,

                    })

            if i % 100 == 0:
                instance.progress = elements
                instance.line_number = items_size
                instance.save()
                async_to_sync(channel_layer.group_send)("export_order", {"type": 'update_export',
                                                                         'text': {"id": instance.id,
                                                                                  "percentage": instance.percentage,
                                                                                  "status": instance.status,
                                                                                  }
                                                                         })
        for count_item in range(instance.line_number):
            headers.update({
                f"Item sku #{count_item + 1}": f"Item sku #{count_item + 1}",
                f"Item name  #{count_item + 1}": f"Item name  #{count_item + 1}",
                f"Item quantity  #{count_item + 1}": f"Item quantity  #{count_item + 1}",

            })
        create_xlsx_file(instance, headers, elements)

        instance.finished_at = datetime.now()
        instance.status = "completed"
        instance.progress = []
        instance.save()
        async_to_sync(channel_layer.group_send)("export_order",
                                                {"type": 'update_export',
                                                 'text': {"id": instance.id,
                                                          "percentage": instance.percentage,
                                                          "status": instance.status,
                                                          "finished_at": instance.finished_at.strftime(
                                                              "%b. %-d   , %Y, %-I:%M %p."),
                                                          "duration": instance.duration,
                                                          "url": instance.file_url
                                                          }
                                                 })
    except Exception:
        instance.status = "failed"
        instance.save()
        pass

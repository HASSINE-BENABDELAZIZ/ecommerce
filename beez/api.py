import datetime

import requests
from django.core.cache import cache
from django.db.models import Sum
from django.template.context_processors import media
from django.templatetags.static import static

from beez.views import render_to_pdf
from orders.models import Shipment, OrderItems


class Beezit(object):
    BASE_URL = "https://api.beezit.pro/api/v1"

    def mount_order_data(self, order, carrier):

        weight = 1
        carrier_service = "livraison"
        order.items = OrderItems.objects.filter(order=order.id).values("original_product_id", "name", "sku", "quantity")
        cod = order.items.aggregate(Sum("original_product__price"))

        data = {
            "fournisseur": 1,
            "client_name": order.customer_name,
            "client_prenom": order.customer_name,
            "client_telephone_1": order.phone,
            "client_email": order.customer_email.strip() if order.customer_email else "default@mail.com",
            "client_address": order.street_1,
            "client_zipcode": order.zip_code,
            "volume": weight,
            "prix": cod['original_product__price__sum'],
            "product_name": order.items.first()["name"],
            "livreur": order.user.marketplace.delivery_man_id if order and order.user and order.user.marketplace else 3,
            "service": carrier_service,
        }

        return data

    def get_access_token(self, carrier):

        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            "username": carrier.username,
            "password": carrier.password
        }

        key = f'carrier:{carrier.id}:get_access_token'
        token = cache.get(key)

        try:
            response = requests.post(f'{self.BASE_URL}/auth/login/', data=data)
            if response.status_code == 200:
                token = response.json()["access"]
                cache.set(key, token, 300)
                return token
        except Exception as e:
            print(e)
        return None

    def ship(self, order, carrier=None):
        data = self.mount_order_data(order, carrier)

        if not carrier:
            return {"error": "Something wrong with GSO integration"}

        token = self.get_access_token(carrier)
        if not token:
            return {"error": "Failed to establish a new connection: [Errno 111] Connection refused"}

        headers = {
            'Authorization': f"JWT {token}",
        }

        if not data.get("client_address"):
            return {"error": "Street address are missing."}

        response = requests.post(f'{self.BASE_URL}/colis/', headers=headers, data=data)

        beez_data = response.json()

        if response.status_code == 201:
            beez_data = response.json()
            context = {
                "data": beez_data,
            }
            shipment = Shipment()
            shipment.label = render_to_pdf("pdf/beez.html", context_dict=context)
            shipment.tracking_code = beez_data["tracking_code"]
            shipment.order = order
            shipment.carrier = carrier
            shipment.save()

            return beez_data

        elif beez_data.get("error"):
            try:
                beez_data = response.json()

                return {"error": beez_data.get("ErrorDetail")[0].get("ErrorDescription")}
            except Exception:
                return {
                    "error": response.content if
                    response.content else
                    "Unable to connect to the BEEZ servers, please wait some time and try again."}

        return {
            "error": response.content if
            response.content else
            "Unable to connect to the BEEZ servers, please wait some time and try again."}

    def tracking(self, shipment, carrier):
        global activity_type
        token = self.get_access_token(carrier)
        if not token:
            return {"error": "Failed to establish a new connection: [Errno 111] Connection refused"}
        headers = {
            'Authorization': f"JWT {token}",
        }
        response = requests.get(
            f'{self.BASE_URL}/tracking/?colis_id={shipment.tracking_code}',
            headers=headers)
        response = response.json()
        from orders.models import TrackingActivities
        from orders.views import update_elasticsearch_order
        for note in response.get("results"):
            format = '%Y-%m-%d %H:%M'
            happened_at = note.get('happened_at')
            happened_at = happened_at.split(' ')
            happened_at = happened_at[0] + " " + happened_at[2]
            happened_at = datetime.datetime.strptime(happened_at, format)
            activity_type = "delivery" if "delivery" in note.get("activity_type") else "in_transit"
            if not TrackingActivities.objects.filter(
                    description=note.get("description"),
                    location=note.get("location"),
                    order=shipment.order,
                    activity_type=activity_type):
                TrackingActivities.objects.get_or_create(
                    happened_at=happened_at,
                    description=note.get("description"),
                    location=note.get("location"),
                    order=shipment.order,
                    activity_type=activity_type)
        if activity_type == "delivery":
            shipment.order.status = "D"
            Shipment.order.substatus = ""
            shipment.order.save()
            update_elasticsearch_order(shipment.order)
        elif activity_type == "in_transit":
            shipment.order.status = "OS"
            shipment.order.substatus = "IT"
            shipment.order.save()
            update_elasticsearch_order(shipment.order)
        else:
            shipment.order.status = "F"
            shipment.order.substatus = ""
            shipment.order.save()
            update_elasticsearch_order(shipment.order)

        return response.get("results")

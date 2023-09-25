import base64
import datetime
from uuid import uuid1

import requests
from django.conf import settings
from django.core.cache import cache

from orders.models import Shipment


class GSO(object):
    BASE_URL = "https://api.gso.com/Rest/v1"

    def mount_order_data(self, order, carrier):

        weight = 1

        from_addr = {
            "ShipperCompany": order.company,
            "PickupAddress1": order.street_1[:50],
            "PickupAddress2": order.street_2[
                              :50] if order.street_2 else None,
            "PickupCity": order.city[:50],
            "PickupState": order.state[:2],
            "PickupZip": order.zip_code[:10],
        }

        to_addr = {
            "ShipToCompany": order.company[:50] if order.company else order.customer_name,
            "ShipToAttention": order.customer_name,
            "ShipToPhone": order.phone[:20] if order.phone else None,
            "ShipToEmail": order.customer_email.strip()[
                           :50] if order.customer_email else "default@mail.com",
            "DeliveryAddress1": order.street_1[:50],
            "DeliveryAddress2": order.street_2[:50] if order.street_2 else None,
            "DeliveryCity": order.city[:50],
            "DeliveryState": order.state[:2],
            "DeliveryZip": order.zip_code[:10],
        }

        carrier_service = "Ground"
        dimensions = {"Length": 15, "Width": 15,
                      "Height": 15}

        return {"weight": weight, "from_addr": from_addr, "to_addr": to_addr, "carrier": carrier,
                "carrier_service": carrier_service, "dimensions": dimensions}

    def get_access_token(self, carrier):

        headers = {
            'Content-Type': 'application/json',
            "username": carrier.username,
            "password": carrier.password
        }

        key = f'carrier:{carrier.id}:get_access_token'
        token = cache.get(key)

        try:
            response = requests.get(f'{self.BASE_URL}/token', headers=headers)
            if response.status_code == 200:
                token = response.headers._store.get("token")[1]
                cache.set(key, token, 300)
                return token
        except Exception:
            pass
        return None

    def ship(self, order, carrier=None):
        data = self.mount_order_data(order, carrier)

        if not carrier:
            return {"error": "Something wrong with GSO integration"}

        token = self.get_access_token(carrier)
        if not token:
            return {"error": "Failed to establish a new connection: [Errno 111] Connection refused"}

        headers = {
            'Token': f"{token}",
            'Content-Type': 'application/json',
        }
        service = order.service

        if not data.get("to_addr", {}).get("DeliveryAddress1"):
            return {"error": "Street address are missing."}

        from orders.models import Shipment
        tracking_number = f"{Shipment.objects.filter(order_id=order.pk).count()}W" \
                          f"{'DEBUG' if settings.DEBUG else ''}{order.pk}".upper()

        shipment_data = {
            "TrackingNumber": tracking_number,
            "ShipmentLabelType": "PAPER_LABEL",
            "SignatureCode": "ADULT_SIG_REQD",
            "Weight": data.get("weight"),
            "ServiceCode": service,
        }

        shipment_data.update(data.get("from_addr"))
        shipment_data.update(data.get("to_addr"))

        gso_data = {
            "AccountNumber": carrier.account_number,
            "Shipment": shipment_data,
        }

        response = requests.post(f'{self.BASE_URL}/Shipment', headers=headers, json=gso_data)

        if response.status_code == 200:
            gso_data = response.json()

            cryped_file_name = uuid1()

            filename = "labels/{}/{}.png".format(
                uuid1(), cryped_file_name
            )
            shipment = Shipment()
            from django.core.files.base import ContentFile

            base64string = gso_data.get("PaperLabel")
            shipment.label = ContentFile(base64.b64decode(base64string), name=filename)
            shipment.tracking_code = gso_data.get("TrackingNumber")
            shipment.order = order
            shipment.carrier = carrier
            shipment.save()

            self.void(carrier, shipment.tracking_code)

            return {"label": filename}

        elif gso_data.get("ErrorDetail"):
            try:
                gso_data = response.json()

                return {"error": gso_data.get("ErrorDetail")[0].get("ErrorDescription")}
            except Exception:
                return {
                    "error": response.content if
                    response.content else
                    "Unable to connect to the GSO servers, please wait some time and try again."}

        return {
            "error": response.content if
            response.content else
            "Unable to connect to the GSO servers, please wait some time and try again."}

    def void(self, carrier, tracking_number):
        token = self.get_access_token(carrier)
        if not token:
            return {"error": "Failed to establish a new connection: [Errno 111] Connection refused"}

        headers = {
            'Token': f"{token}",
            'Content-Type': 'application/json',
        }
        response = requests.get(f'{self.BASE_URL}/Shipment',
                                headers=headers,
                                json={"AccountNumber": carrier.account_number,
                                      "TrackingNumber": tracking_number})
        return response.json()

    def tracking(self, shipment, carrier):
        token = self.get_access_token(carrier)
        if not token:
            return {"error": "Failed to establish a new connection: [Errno 111] Connection refused"}
        headers = {
            'Token': f"{token}",
            'Content-Type': 'application/json',
        }
        response = requests.get(
            f'{self.BASE_URL}/TrackShipment?AccountNumber={carrier.account_number}'
            f'&TrackingNumber={shipment.tracking_code}',
            headers=headers)
        response = response.json()
        from orders.models import TrackingActivities
        from orders.views import update_elasticsearch_order
        for note in response.get("ShipmentInfo")[0].get("TransitNotes"):
            format = '%m/%d/%Y %I:%M:%S %p'
            happened_at = datetime.datetime.strptime(note.get("EventDate"), format)
            activity_type = "delivery" if "SHIPMENT DELIVERED" in note.get("Comments") else "in_transit"
            if note.get("Comments").startswith("DEL ") or note.get("Comments").startswith(
                    "RTS ") or note.get("Comments").startswith("SET FOR RTS"):
                activity_type = "exception"
            if not TrackingActivities.objects.filter(
                    description=note.get("Comments"),
                    location=note.get("Location"),
                    order=shipment.order,
                    activity_type=activity_type):
                TrackingActivities.objects.get_or_create(
                    happened_at=happened_at,
                    description=note.get("Comments"),
                    location=note.get("Location"),
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

        return response

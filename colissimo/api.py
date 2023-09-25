import datetime
import json

from django.db.models import Sum

from orders.models import Shipment, OrderItems


class Colissimo(object):
    BASE_URL = "http://delivery.colissimo.tn/wsColissimoGo/wsColissimoGo.asmx?wsdl"

    def mount_order_data(self, order):
        order.items = OrderItems.objects.filter(order=order.id).values("original_product_id", "name", "sku", "quantity")
        cod = order.items.aggregate(Sum("original_product__price"))

        colis = {
            'adresse': order.street_1,
            'client': order.customer_name,
            'commentaire': '',
            'designation': 'articletest',
            'echange': 0,
            'gouvernorat': order.state,
            'nb_pieces': order.items.count(),
            'prix': cod['original_product__price__sum'],
            'reference': order.order_number,
            'tel1': order.phone,
            'type': 'VO',
            'ville': order.city,
        }

        return colis

    def get_access_token(self, carrier):
        client = Client(f'{self.BASE_URL}')
        AuthHeader = client.factory.create('AuthHeader')
        AuthHeader.Uilisateur = carrier.username,
        AuthHeader.Pass = carrier.password
        client.set_options(soapheaders=AuthHeader)

        return client

    def ship(self, order, carrier=None):
        data = self.mount_order_data(order)

        if not carrier:
            return {"error": "Something wrong with Colissimo integration"}

        client = self.get_access_token(carrier)
        if not client:
            return {"error": "Failed to establish a new connection: [Errno 111] Connection refused"}

        if not data.get("adresse"):
            return {"error": "Street address are missing."}

        response = client.service.AjouterColis(pic=json.dumps(data))

        colissimo_data = json.loads(response)

        if colissimo_data["result_type"] == "success":
            shipment = Shipment()
            shipment.tracking_code = colissimo_data['result_content']
            shipment.order = order
            shipment.carrier = carrier
            shipment.save()

            return colissimo_data

        elif colissimo_data["result_type"] == "erreur":
            try:
                colissimo_data = response

                return {"error": colissimo_data["result_code"]}
            except Exception:
                return {
                    "error": response.result_code if
                    response.result_code else
                    "Unable to connect to the Colissimo servers, please wait some time and try again."}

        return {
            "error": response.result_code if
            response.result_code else
            "Unable to connect to the Colissimo servers, please wait some time and try again."}

    def tracking(self, shipment, carrier):
        client = self.get_access_token(carrier)
        if not client:
            return {"error": "Failed to establish a new connection: [Errno 111] Connection refused"}
        response = client.service.GetColis(code_barre=shipment.tracking_code)
        return response
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

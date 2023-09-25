import datetime

import requests
from django.conf import settings
from django.core.cache import cache
from django.db.models import Sum

from orders.models import Shipment, TrackingActivities, OrderItems, Order, Carrier
from products.models import Product

LABEL_PARCEL = [
    {
        "EVENT_ID": 1,
        "EVENT_CODE": "PIK01",
        "EVENT_LIBELLE": "Création étiquette position",
        "EVENT_LIBELLE_ANG": "Creating label"
    },
    {
        "EVENT_ID": 2,
        "EVENT_CODE": "PIK02",
        "EVENT_LIBELLE": "Planification enlevement",
        "EVENT_LIBELLE_ANG": "Planning pickup"
    },
    {
        "EVENT_ID": 3,
        "EVENT_CODE": "PIK03",
        "EVENT_LIBELLE": "Enlevement en cours de tournée",
        "EVENT_LIBELLE_ANG": "Pickup in progress"
    },
    {
        "EVENT_ID": 4,
        "EVENT_CODE": "PUP",
        "EVENT_LIBELLE": "Colis enlevé",
        "EVENT_LIBELLE_ANG": "Parcel collected"
    },
    {
        "EVENT_ID": 5,
        "EVENT_CODE": "PUX",
        "EVENT_LIBELLE": "Anomalie enlevement",
        "EVENT_LIBELLE_ANG": "Pickup anomaly"
    },
    {
        "EVENT_ID": 6,
        "EVENT_CODE": "PIK06",
        "EVENT_LIBELLE": "Tentative enlevement",
        "EVENT_LIBELLE_ANG": "Pickup attempt"
    },
    {
        "EVENT_ID": 7,
        "EVENT_CODE": "PIK07",
        "EVENT_LIBELLE": "Enlevement annulé",
        "EVENT_LIBELLE_ANG": "Pickup canceled"
    },
    {
        "EVENT_ID": 11,
        "EVENT_CODE": "MAG03",
        "EVENT_LIBELLE": "Réception HUB",
        "EVENT_LIBELLE_ANG": "Receipt in stock"
    },
    {
        "EVENT_ID": 13,
        "EVENT_CODE": "MAG05",
        "EVENT_LIBELLE": "Scan Inventaire",
        "EVENT_LIBELLE_ANG": "Scan in inventory "
    },
    {
        "EVENT_ID": 14,
        "EVENT_CODE": "MAG06",
        "EVENT_LIBELLE": "Anomalie réception",
        "EVENT_LIBELLE_ANG": "Reception anomaly"
    },
    {
        "EVENT_ID": 15,
        "EVENT_CODE": "MAG07",
        "EVENT_LIBELLE": "Commentaire",
        "EVENT_LIBELLE_ANG": "Comment"
    },
    {
        "EVENT_ID": 16,
        "EVENT_CODE": "MAG08",
        "EVENT_LIBELLE": "Clôture position",
        "EVENT_LIBELLE_ANG": "Shipment closure"
    },
    {
        "EVENT_ID": 17,
        "EVENT_CODE": "DEL01",
        "EVENT_LIBELLE": "Planification Livraison",
        "EVENT_LIBELLE_ANG": "Planning delivery"
    },
    {
        "EVENT_ID": 18,
        "EVENT_CODE": "VANS",
        "EVENT_LIBELLE": "Livraison planifiée en cours de tournée",
        "EVENT_LIBELLE_ANG": "Delivery in progress"
    },
    {
        "EVENT_ID": 19,
        "EVENT_CODE": "DEL03",
        "EVENT_LIBELLE": "Tentative de livraison",
        "EVENT_LIBELLE_ANG": "Delivery attempt"
    },
    {
        "EVENT_ID": 20,
        "EVENT_CODE": "DEX",
        "EVENT_LIBELLE": "Anomalie livraison",
        "EVENT_LIBELLE_ANG": "Delivery anomaly"
    },
    {
        "EVENT_ID": 22,
        "EVENT_CODE": "PUX16",
        "EVENT_LIBELLE": "Montant collecté",
        "EVENT_LIBELLE_ANG": "COD collected"
    },
    {
        "EVENT_ID": 23,
        "EVENT_CODE": "DEL07",
        "EVENT_LIBELLE": "Livraison annulée",
        "EVENT_LIBELLE_ANG": "Delivery canceled"
    },
    {
        "EVENT_ID": 25,
        "EVENT_CODE": "POD",
        "EVENT_LIBELLE": "Colis livré",
        "EVENT_LIBELLE_ANG": "Parcel delivred"
    },
    {
        "EVENT_ID": 26,
        "EVENT_CODE": "MAG09",
        "EVENT_LIBELLE": "Colis validé",
        "EVENT_LIBELLE_ANG": "Parcel validated"
    },
    {
        "EVENT_ID": 27,
        "EVENT_CODE": "PIK09",
        "EVENT_LIBELLE": "Planification enlevement annulée",
        "EVENT_LIBELLE_ANG": "Pickup planning canceled"
    },
    {
        "EVENT_ID": 28,
        "EVENT_CODE": "MAG09",
        "EVENT_LIBELLE": "Planification livraison annulée",
        "EVENT_LIBELLE_ANG": "Delivery planning canceled"
    },
    {
        "EVENT_ID": 29,
        "EVENT_CODE": "RTN01",
        "EVENT_LIBELLE": "Création étiquette position de retour",
        "EVENT_LIBELLE_ANG": "Creating return label"
    },
    {
        "EVENT_ID": 30,
        "EVENT_CODE": "RTN02",
        "EVENT_LIBELLE": "Cloture pour retour",
        "EVENT_LIBELLE_ANG": "Closing for return"
    },
    {
        "EVENT_ID": 31,
        "EVENT_CODE": "RTN03",
        "EVENT_LIBELLE": "Planification retour",
        "EVENT_LIBELLE_ANG": "Planning return"
    },
    {
        "EVENT_ID": 32,
        "EVENT_CODE": "RTN04",
        "EVENT_LIBELLE": "Retour planifié en cours de tournée",
        "EVENT_LIBELLE_ANG": "Return in progress"
    },
    {
        "EVENT_ID": 33,
        "EVENT_CODE": "RTN05",
        "EVENT_LIBELLE": "Position de retour livrée",
        "EVENT_LIBELLE_ANG": "Return delivred"
    },
    {
        "EVENT_ID": 34,
        "EVENT_CODE": "RTN06",
        "EVENT_LIBELLE": "Anomalie de retour",
        "EVENT_LIBELLE_ANG": "Return anomaly"
    },
    {
        "EVENT_ID": 35,
        "EVENT_CODE": "RTN07",
        "EVENT_LIBELLE": "Tentative de retour",
        "EVENT_LIBELLE_ANG": "Return attempt"
    },
    {
        "EVENT_ID": 36,
        "EVENT_CODE": "RTRN01",
        "EVENT_LIBELLE": "Création étiquette position d'échange",
        "EVENT_LIBELLE_ANG": "Creating exchange label"
    },
    {
        "EVENT_ID": 37,
        "EVENT_CODE": "RTRN02",
        "EVENT_LIBELLE": "Echange planifié en cours de tournée",
        "EVENT_LIBELLE_ANG": "Exchange in progress"
    },
    {
        "EVENT_ID": 38,
        "EVENT_CODE": "RTRN03",
        "EVENT_LIBELLE": "Tentative d'échange",
        "EVENT_LIBELLE_ANG": "Exchange attempt"
    },
    {
        "EVENT_ID": 39,
        "EVENT_CODE": "RTRN04",
        "EVENT_LIBELLE": "Position d'échange livrée",
        "EVENT_LIBELLE_ANG": "Exchange delivred"
    },
    {
        "EVENT_ID": 40,
        "EVENT_CODE": "RTRN05",
        "EVENT_LIBELLE": "Anomalie d'échange",
        "EVENT_LIBELLE_ANG": "Exchange anomaly"
    }
]
PAYMENT_PARCEL = [
    {
        "MR_CODE": "ESP",
        "MR_INTITULE": "ESPECES"
    },
    {
        "MR_CODE": "CHQ",
        "MR_INTITULE": "CHEQUE"
    }
]


class Fparcel(object):
    TEST = "http://fparcel.net:59/WebServiceExterne/"
    PROD = "https://admin.fparcel.net/WebServiceExterne/"

    @property
    def BASE_URL(self):
        if settings.DEBUG:
            return self.TEST
        else:
            return self.PROD

    def mount_order_data(self, order, carrier):

        weight = 1

        from_addr = {
            "ENL_CONTACT_NOM": order.marketplace.name if order and order.marketplace and order.marketplace.name else "storelinkers",
            "ENL_CONTACT_PRENOM": order.marketplace.name if order and order.marketplace and order.marketplace.name else "storelinkers",
            "ENL_PORTABLE": order.marketplace.phone if order and order.marketplace and order.marketplace.phone else "25770277",
            "ENL_MAIL": order.marketplace.email if order and order.marketplace and order.marketplace.email else "mail@mail.com",
            "ENL_ADRESSE": order.marketplace.address if order and order.marketplace and order.marketplace.address else order.client_address,
            "ENL_CODE_POSTAL": order.marketplace.code_postale if order and order.marketplace and order.marketplace.code_postale else order.expiditeur_zipcode,
        }

        to_addr = {
            "LIV_CONTACT_NOM": order.customer_name,
            "LIV_CONTACT_PRENOM": order.customer_name,
            "LIV_PORTABLE": order.phone,
            "LIV_MAIL": order.customer_email.strip() if order.customer_email else "default@mail.com",
            "LIV_ADRESSE": order.client_address,
            "LIV_CODE_POSTAL": order.client_zipcode
        }

        carrier_service = "Ground"
        dimensions = {"Length": 15, "Width": 15,
                      "Height": 15}

        return {"weight": weight, "from_addr": from_addr, "to_addr": to_addr, "carrier": carrier,
                "carrier_service": carrier_service, "dimensions": dimensions}

    def get_access_token(self, carrier):

        json = {
            "username": carrier.username,
            "password": carrier.password
        }

        key = f'carrier:{carrier.id}:get_access_token'
        token = cache.get(key)
        if token:
            return token

        try:
            response = requests.get(f'{self.PROD}/get_token', json=json)
            if response.status_code == 200:
                token = response.json()
                print(token)
                cache.set(key, token, 300)
                return token
        except Exception:
            pass
        return None

    def ship(self, order, carrier=None):
        data = self.mount_order_data(order, carrier)

        if not carrier:
            return {"error": "Something wrong with Fast parcel integration"}

        token = self.get_access_token(carrier)
        if not token:
            return {"error": "Failed to establish a new connection: [Errno 111] Connection refused"}

        headers = {
            'Content-Type': 'application/json',
        }

        if not data.get("to_addr", {}).get("LIV_ADRESSE"):
            return {"error": "Street address is missing."}

        tracking_number = f"{order.pk}storelinkers" \
                          f"{'DEBUG' if settings.DEBUG else ''}{order.pk}".upper()

        shipment_data = {}

        order.items = OrderItems.objects.filter(order=order.id).values("original_product_id", "name", "sku", "quantity")
        cod = order.total_price + order.shipment_cost

        shipment_data.update({
            "TOKEN": token,
            "REFERENCE": tracking_number,
            "ORDER_NUMBER": order.id,
            "POIDS": order.total_weight,
            'VALEUR': cod,
            'COD': cod,
            'RTRNCONTENU': list(order.items),
            'POSNBPIECE': 1,
            'DATE_ENLEVEMENT': datetime.datetime.now().strftime("%d/%m/%Y"),
            'POSITION_TIME_LIV_DISPO_FROM': '08',
            'POSITION_TIME_LIV_DISPO_TO': '18',
            'POS_VALID': 1,
            'MR_CODE': 'ESP',
        })

        shipment_data.update(data.get("from_addr"))
        shipment_data.update(data.get("to_addr"))

        fparcel_data = shipment_data
        response = requests.post(f'{self.PROD}/pos_create', json=fparcel_data)

        if response.status_code == 200:
            fparcel_response_data = response.json()
            if fparcel_response_data.isnumeric():
                Shipment.objects.create(tracking_code=fparcel_response_data, carrier=carrier, order=order)
                return fparcel_data
            else:
                Shipment.objects.create(tracking_code=fparcel_response_data if
                fparcel_response_data else "error de connection.", carrier=carrier, order=order)
                return {
                    "error": fparcel_response_data if
                    fparcel_response_data else
                    "Unable to connect to the Fast Parcel servers, please wait some time and try again."}

    def tracking(self, shipment):
        if shipment:
            token = self.get_access_token(shipment.carrier.fpcarrier)
            if not token:
                return {"error": "Failed to establish a new connection: [Errno 111] Connection refused"}

            headers = {
                'Content-Type': 'application/json',
            }
            fparcel_data = {
                "TOKEN": token,
                "POSBARCODE": shipment.tracking_code
            }
            response = requests.get(f'{self.PROD}/get_pos_details', json=fparcel_data)
            resp = response.json()
            if type(resp) is dict:
                event_list = resp.get("POS_EVENT_LIST", [])
                for event in event_list[::-1]:
                    datefield = event.get("EV_DATE")
                    num = ""
                    for c in datefield:
                        if c.isdigit():
                            num = num + c
                    date = datetime.datetime.fromtimestamp(int(num) / 1000)
                    created = False
                    tracking_query = TrackingActivities.objects.filter(
                        event_id=event.get("EVENTID"),
                        manual=False,
                        shipment=shipment,
                        timestamp=date
                    )
                    if tracking_query.count() > 1:
                        tracking_query.delete()
                    if TrackingActivities.objects.filter(
                            event_id=event.get("EVENTID"),
                            manual=False,
                            shipment=shipment,
                            timestamp=date
                    ).exists():

                        track = TrackingActivities.objects.filter(
                            event_id=event.get("EVENTID"),
                            manual=False,
                            shipment=shipment,
                        ).first()
                    else:
                        created = True
                        track = TrackingActivities.objects.create(
                            event_id=event.get("EVENTID"),
                            description=event.get("EV_INTITULE"),
                            manual=False,
                            shipment=shipment,
                            timestamp=date
                        )

                    if created:
                        order = shipment.order
                        if track.event_id in [22, 25, 39]:
                            order.status = "D"
                        if track.event_id in [4, 11, 13, 17, 26]:
                            order.status = "OS"
                            order.substatus = "PT"
                        if track.event_id in [18, 19, 38, 40]:
                            order.status = "OS"
                            order.substatus = "PT"
                        if track.event_id in [3, 6, 7]:
                            order.status = "OS"
                            order.substatus = "PT"
                        if track.event_id in [5, 14, 23, 27, 28, 34]:
                            order.status = "F"
                            track.problem_description = resp.get("POS_MOTIF_ANO")
                            track.save()
                        if track.event_id in [17, 18, 38, 37]:
                            order.status = "OS"
                            order.substatus = "IT"
                        if track.event_id in [29, 30, 31, 32, 33, 35]:
                            order.status = "retour"
                        order.save()
                return resp

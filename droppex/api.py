import requests

from orders.models import OrderItems, Shipment, Order

from django.db.models import Sum


class DroppexAPI:

    def get_order_data(self, order):
        try:
            sum_qt = OrderItems.objects.filter(order=order).aggregate(Sum('quantity'))
            return {
                'tel_l': order.phone,
                'nom_client': order.customer_name,
                'gov_l': order.client_deligaiton,
                'cod': order.total,
                'libelle': str(order),
                'nb_piece': sum_qt.quantity__sum,
                'adresse_l': order.client_address,
                'tel2_l': '25770277',
                'service': order.t_service
            }
        except KeyError as e:
            return {'message_error': f'Champs manquant: {e}'}

    def ship(self, order, carrier):
        url = carrier.base_url
        payload = self.get_order_data(order)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        if payload.get('message_error'):
            order.status = 'AC'
            order.note = payload['message_error']
        else:
            payload.update({
                'code_api': carrier.code_api,
                'cle_api': carrier.key_api,
                'action': 'add'
            })

            response = requests.post(url, headers=headers, data=payload)
            status_code = response.status_code
            response = response.json()

            if status_code == 200:
                Shipment.objects.create(tracking_code=response.reference, carrier=carrier, order=order)
            else:
                order.status = 'AC'
                order.note = response.get('message')

    def tracking(self, tracking_number, carrier):
        url = carrier.base_url
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        payload = {
            'code_api': carrier.code_api,
            'cle_api': carrier.key_api,
            'action': 'get',
            'code_barre': tracking_number
        }
        response = requests.post(url, headers=headers, data=payload).json()
        order = Order.objects.get(tracking_number=tracking_number)
        order.note = response.get('dernier_etat')


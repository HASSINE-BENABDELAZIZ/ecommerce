from django.urls import reverse

from .test_setup import SimpleTestSetup
from ..models import Shipment
from ..serializers import ShipmentSerializer


class ShipmentGETPermissions(SimpleTestSetup):
    def test_shipment_list_view_not_authentification(self):
        res = self.client.get(reverse('shipment-list'))
        self.assertEqual(res.status_code, 403)
        self.login_no()
        res = self.client.get(reverse('shipment-list'))
        self.assertEqual(res.status_code, 403)

    def test_shipment_list_view_authentificated(self):
        self.login()
        res = self.client.get(reverse('shipment-list'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual("next" in res.json(), True)
        self.assertEqual("previous" in res.json(), True)

    def test_shipment_element_view_not_found(self):
        self.login()
        res = self.client.get(reverse('shipment-detail', kwargs={"pk": 0}))
        self.assertEqual(res.status_code, 404)

    def test_shipment_element_view_authentificated(self):
        self.login()
        order, created = Shipment.objects.get_or_create(tracking_code="test")
        res = self.client.get(reverse('shipment-detail', kwargs={"pk": order.id}))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), ShipmentSerializer(instance=order).data)

    def test_shipment_element_view_not_authentificated(self):
        order = Shipment.objects.get(tracking_code="test")
        res = self.client.get(reverse('shipment-detail', kwargs={"pk": order.id}))
        self.assertEqual(res.status_code, 403)
        self.login_no()
        res = self.client.get(reverse('shipment-detail', kwargs={"pk": order.id}))
        self.assertEqual(res.status_code, 403)


class ShipmentCreatePermissions(SimpleTestSetup):
    def test_shipment_create_no_perms(self):
        res = self.client.post(reverse('shipment-list'), data={
            "tracking_code": "",
            "label": "",
            "order": "",
            "carrier": ""
        })
        self.assertEqual(res.status_code, 403)
        self.login_no()
        res = self.client.post(reverse('shipment-list'), data={
            "tracking_code": "",
            "label": "",
            "order": "",
            "carrier": ""
        })
        self.assertEqual(res.status_code, 403)

    def test_shipment_create_valid_data(self):
        self.login()
        res = self.client.post(reverse('shipment-list'), data={
            "tracking_code": "atb1.0",
            "label": None,
            "order": None,
            "carrier": None
        }, format="json")

        self.assertEqual(res.status_code, 201)


class ShipmentDeletePermissions(SimpleTestSetup):
    def test_order_delete_no_perms(self):
        order, created = Shipment.objects.get_or_create(tracking_code="test")
        res = self.client.delete(reverse('shipment-detail', kwargs={"pk": order.id}))
        self.assertEqual(res.status_code, 403)

    def test_order_delete_perms(self):
        self.login()
        order, created = Shipment.objects.get_or_create(tracking_code="test")
        res = self.client.delete(reverse('shipment-detail', kwargs={"pk": order.id}))
        print(res.data)
        self.assertEqual(res.status_code, 204)

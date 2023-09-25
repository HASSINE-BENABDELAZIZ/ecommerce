from django.urls import reverse

from .test_setup import SimpleTestSetup
from ..models import Carrier, Address
from ..serializers import CarrierSerializer


class CarrierGETPermissions(SimpleTestSetup):
    def test_carrier_list_view_not_authentification(self):
        res = self.client.get(reverse('carrier-list'))
        self.assertEqual(res.status_code, 403)
        self.login_no()
        res = self.client.get(reverse('carrier-list'))
        self.assertEqual(res.status_code, 403)

    def test_carrier_list_view_authentificated(self):
        self.login()
        res = self.client.get(reverse('carrier-list'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual("next" in res.json(), True)
        self.assertEqual("previous" in res.json(), True)

    def test_carrier_element_view_not_found(self):
        self.login()
        res = self.client.get(reverse('carrier-detail', kwargs={"pk": 0}))
        self.assertEqual(res.status_code, 404)

    def test_carrier_element_view_authentificated(self):
        self.login()
        adress, created = Address.objects.get_or_create(state="test", city="test", zipcode="test",
                                                        street_address="test")
        order, created = Carrier.objects.get_or_create(carrier="gso", sender_address=adress, name="test")
        res = self.client.get(reverse('carrier-detail', kwargs={"pk": order.id}))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), CarrierSerializer(instance=order).data)
        self.login_no()
        res = self.client.get(reverse('carrier-detail', kwargs={"pk": order.id}))
        self.assertEqual(res.status_code, 403)

    def test_carrier_element_view_not_authentificated(self):
        adress, created = Address.objects.get_or_create(state="test", city="test", zipcode="test",
                                                        street_address="test")
        order, created = Carrier.objects.get_or_create(carrier="gso", sender_address=adress, name="test")
        res = self.client.get(reverse('carrier-detail', kwargs={"pk": order.id}))
        self.assertEqual(res.status_code, 403)


class CarrierCreatePermissions(SimpleTestSetup):
    def test_carrier_create_no_perms(self):
        res = self.client.post(reverse('carrier-list'), data={
            "carrier": "gso",
            "name": "test",
            "account_number": "test",
            "active": False,
            "sender_address": ""
        }, format="json")
        self.assertEqual(res.status_code, 403)

    def test_carrier_create_valid_data(self):
        self.login()
        adress, created = Address.objects.get_or_create(state="test", city="test", zipcode="test",
                                                        street_address="test")
        data = {
            "carrier": "gso",
            "name": "test",
            "account_number": "test",
            "active": False,
            "sender_address": adress.id
        }
        res = self.client.post(reverse('carrier-list'), data=data, format="json")
        self.assertEqual(res.status_code, 201)
        data["carrier"] = None
        res = self.client.post(reverse('carrier-list'), data=data, format="json")
        self.assertEqual(res.status_code, 400)
        data["carrier"] = "gso"
        data["name"] = ""
        res = self.client.post(reverse('carrier-list'), data=data, format="json")
        self.assertEqual(res.status_code, 400)
        data["name"] = "test"
        data["account_number"] = ""
        res = self.client.post(reverse('carrier-list'), data=data, format="json")
        self.assertEqual(res.status_code, 400)
        data["account_number"] = "test"
        data["sender_address"] = ""
        res = self.client.post(reverse('carrier-list'), data=data, format="json")
        self.assertEqual(res.status_code, 400)


class CarrierDeletePermissions(SimpleTestSetup):
    def test_carrier_delete_no_perms(self):
        adress, created = Address.objects.get_or_create(state="test", city="test", zipcode="test",
                                                        street_address="test")
        order, created = Carrier.objects.get_or_create(carrier="gso", sender_address=adress, name="test")
        res = self.client.delete(reverse('carrier-detail', kwargs={"pk": order.id}))
        self.assertEqual(res.status_code, 403)
        self.login_no()
        res = self.client.delete(reverse('carrier-detail', kwargs={"pk": order.id}))
        self.assertEqual(res.status_code, 403)

    def test_carrier_delete_perms(self):
        self.login()
        adress, created = Address.objects.get_or_create(state="test", city="test", zipcode="test",
                                                        street_address="test")
        order, created = Carrier.objects.get_or_create(carrier="gso", sender_address=adress, name="test")
        res = self.client.delete(reverse('carrier-detail', kwargs={"pk": order.id}))
        print(res.data)
        self.assertEqual(res.status_code, 204)

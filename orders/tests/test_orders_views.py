from django.urls import reverse

from .test_setup import SimpleTestSetup
from ..models import Order
from ..serializers import OrderSerializer


class OrderGETPermissions(SimpleTestSetup):
    def test_order_list_view_not_authentification(self):
        res = self.client.get(reverse('order-list'))
        self.assertEqual(res.status_code, 403)
        self.login_no()
        res = self.client.get(reverse('order-list'))
        self.assertEqual(res.status_code, 403)

    def test_order_list_view_authentificated(self):
        self.login()
        res = self.client.get(reverse('order-list'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual("next" in res.json(), True)
        self.assertEqual("previous" in res.json(), True)

    def test_order_element_view_not_found(self):
        self.login()
        res = self.client.get(reverse('order-detail', kwargs={"pk": 0}))
        self.assertEqual(res.status_code, 404)

    def test_order_element_view_authentificated(self):
        self.login()
        order, created = Order.objects.get_or_create(order_number="test")
        res = self.client.get(reverse('order-detail', kwargs={"pk": order.id}))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), OrderSerializer(instance=order).data)

    def test_order_element_view_not_authentificated(self):
        order = Order.objects.get(order_number="test")
        res = self.client.get(reverse('order-detail', kwargs={"pk": order.id}))
        self.assertEqual(res.status_code, 403)
        self.login_no()
        res = self.client.get(reverse('order-list'))
        self.assertEqual(res.status_code, 403)


class OrderPatchPermissions(SimpleTestSetup):
    def test_order_update_no_perms(self):
        order, created = Order.objects.get_or_create(order_number="test")
        res = self.client.patch(reverse('order-detail', kwargs={"pk": order.id}))
        self.assertEqual(res.status_code, 403)

    def test_order_update_perms(self):
        self.login()
        order, created = Order.objects.get_or_create(order_number="test")
        res = self.client.patch(reverse('order-detail', kwargs={"pk": order.id}))
        self.assertEqual(res.status_code, 200)


class OrderDeletePermissions(SimpleTestSetup):
    def test_order_delete_no_perms(self):
        order, created = Order.objects.get_or_create(order_number="test")
        res = self.client.delete(reverse('order-detail', kwargs={"pk": order.id}))
        self.assertEqual(res.status_code, 403)

    def test_order_delete_perms(self):
        self.login()
        order, created = Order.objects.get_or_create(order_number="test")
        res = self.client.delete(reverse('order-detail', kwargs={"pk": order.id}))
        self.assertEqual(res.status_code, 204)


class OrderCreatePermissions(SimpleTestSetup):
    def test_order_create_no_perms(self):
        data = {
            "city": "",
            "company": "",
            "customer_name": "",
            "customer_email": "",
            "order_number": "test1",
            "zip_code": "",
            "origin": "",
            "phone": "",
            "state": "",
            "status": "",
            "street_1": "",
            "street_2": "",
            "substatus": ""
        }
        res = self.client.post(reverse('order-list'), data=data)
        self.assertEqual(res.status_code, 403)
        self.login_no()
        res = self.client.post(reverse('order-list'), data=data)
        self.assertEqual(res.status_code, 403)

    def test_order_create_invalid_data(self):
        self.login()
        data = {
            "city": "",
            "company": "",
            "customer_name": "",
            "customer_email": "",
            "order_number": "",
            "zip_code": "",
            "origin": "",
            "phone": "",
            "state": "",
            "status": "",
            "street_1": "",
            "street_2": "",
            "substatus": ""
        }
        res = self.client.post(reverse('order-list'), data=data)

        self.assertEqual(res.status_code, 400)
        data = {"city": "test",
                "company": "test",
                "customer_name": "test",
                "customer_email": "",
                "order_number": "test1",
                "zip_code": "120001",
                "origin": "",
                "phone": "121",
                "state": "te",
                "status": "",
                "street_1": "test",
                "street_2": "",
                "substatus": ""
                }

        res = self.client.post(reverse('order-list'), data=data)
        self.assertEqual(res.status_code, 400)
        data["zip_code"] = '1200T'
        res = self.client.post(reverse('order-list'), data=data)
        self.assertEqual(res.status_code, 400)
        data["zip_code"] = '12000'
        data["customer_name"] = ""
        res = self.client.post(reverse('order-list'), data=data, format="json")
        self.assertEqual(res.status_code, 400)
        data["customer_name"] = "test"
        data["street_1"] = ""
        res = self.client.post(reverse('order-list'), data=data, format="json")
        self.assertEqual(res.status_code, 400)
        data["city"] = ""
        data["street_1"] = "test"
        res = self.client.post(reverse('order-list'), data=data, format="json")
        self.assertEqual(res.status_code, 400)

    def test_order_create_valid_data(self):
        self.login_no()
        data = {
            "city": "test",
            "company": "test",
            "customer_name": "test",
            "customer_email": "",
            "order_number": "test1ee",
            "zip_code": "12000",
            "origin": "",
            "phone": "121",
            "state": "te",
            "status": "",
            "street_1": "test",
            "street_2": "",
            "substatus": ""
        }
        res = self.client.post(reverse('order-list'), data=data)
        self.assertEqual(res.status_code, 403)
        self.login()
        res = self.client.post(reverse('order-list'), data=data)
        self.assertEqual(res.status_code, 201)

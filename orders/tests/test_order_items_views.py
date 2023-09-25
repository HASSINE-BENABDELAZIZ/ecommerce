from django.urls import reverse

from .test_setup import SimpleTestSetup
from ..models import OrderItems, Order
from ..serializers import OrderItemsSerializer


class OrderItemsGETPermissions(SimpleTestSetup):
    def test_orderitems_list_view_not_authentification(self):
        res = self.client.get(reverse('orderitems-list'))
        self.assertEqual(res.status_code, 403)
        self.login_no()
        res = self.client.get(reverse('orderitems-list'))
        self.assertEqual(res.status_code, 403)

    def test_orderitems_list_view_authentificated(self):
        self.login()
        res = self.client.get(reverse('orderitems-list'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual("next" in res.json(), True)
        self.assertEqual("previous" in res.json(), True)

    def test_orderitems_element_view_not_found(self):
        self.login()
        res = self.client.get(reverse('orderitems-detail', kwargs={"pk": 0}))
        self.assertEqual(res.status_code, 404)

    def test_orderitems_element_view_authentificated(self):
        self.login()
        rder, created = Order.objects.get_or_create(order_number="test")
        order, created = OrderItems.objects.get_or_create(sku="test", name="test", order=rder)
        res = self.client.get(reverse('orderitems-detail', kwargs={"pk": order.id}))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), OrderItemsSerializer(instance=order).data)

    def test_orderitems_element_view_not_authentificated(self):
        rder, created = Order.objects.get_or_create(order_number="test")
        order, created = OrderItems.objects.get_or_create(sku="test", name="test", order=rder)
        res = self.client.get(reverse('orderitems-detail', kwargs={"pk": order.id}))
        self.assertEqual(res.status_code, 403)
        self.login_no()
        res = self.client.get(reverse('orderitems-detail', kwargs={"pk": order.id}))
        self.assertEqual(res.status_code, 403)


class OrderItemsCreatePermissions(SimpleTestSetup):
    def test_orderitems_create_no_perms(self):
        res = self.client.post(reverse('orderitems-list'), data={
            "sku": "",
            "name": "",
            "quantity": "",
        })
        self.assertEqual(res.status_code, 403)
        self.login_no()
        self.assertEqual(res.status_code, 403)

    def test_orderitems_create_valid_data(self):
        self.login()
        order, created = Order.objects.get_or_create(order_number="test")
        res = self.client.post(reverse('orderitems-list'), data={
            "sku": "test2",
            "name": "test",
            "quantity": 1,
            "order": order.id
        }, format="json")

        self.assertEqual(res.status_code, 201)


class OrderItemsDeletePermissions(SimpleTestSetup):
    def test_orderitems_delete_no_perms(self):
        rder, created = Order.objects.get_or_create(order_number="test")
        order, created = OrderItems.objects.get_or_create(sku="test", name="test", order=rder)
        res = self.client.delete(reverse('orderitems-detail', kwargs={"pk": order.id}))
        self.assertEqual(res.status_code, 403)
        self.login_no()
        res = self.client.delete(reverse('orderitems-detail', kwargs={"pk": order.id}))
        self.assertEqual(res.status_code, 403)

    def test_orderitems_delete_perms(self):
        self.login()
        rder, created = Order.objects.get_or_create(order_number="test")
        order, created = OrderItems.objects.get_or_create(sku="test", name="test", order=rder)
        res = self.client.delete(reverse('orderitems-detail', kwargs={"pk": order.id}))
        self.assertEqual(res.status_code, 204)

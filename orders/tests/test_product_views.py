from django.urls import reverse

from products.models import Product
from products.serializers import ProductSerializer
from .test_setup import SimpleTestSetup


class ProductGETPermissions(SimpleTestSetup):
    def test_product_list_view_not_authentification(self):
        res = self.client.get(reverse('product-list'))
        self.assertEqual(res.status_code, 403)
        self.login_no()
        res = self.client.get(reverse('product-list'))
        self.assertEqual(res.status_code, 403)

    def test_product_list_view_authentificated(self):
        self.login()
        res = self.client.get(reverse('product-list'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual("next" in res.json(), True)
        self.assertEqual("previous" in res.json(), True)

    def test_product_element_view_not_found(self):
        self.login()
        res = self.client.get(reverse('product-detail', kwargs={"pk": 0}))
        self.assertEqual(res.status_code, 404)

    def test_product_element_view_authentificated(self):
        self.login()
        order, created = Product.objects.get_or_create(sku="test")
        res = self.client.get(reverse('product-detail', kwargs={"pk": order.id}))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), ProductSerializer(instance=order).data)

    def test_product_element_view_not_authentificated(self):
        order = Product.objects.get(sku="test")
        res = self.client.get(reverse('product-detail', kwargs={"pk": order.id}))
        self.assertEqual(res.status_code, 403)
        self.login_no()
        res = self.client.get(reverse('product-detail', kwargs={"pk": order.id}))
        self.assertEqual(res.status_code, 403)


class ProductCreatePermissions(SimpleTestSetup):
    def test_product_create_no_perms(self):
        data = {
            "sku": "test2",
            "name": "",
            "brand": "",
            "weight": None,
            "year": None,
            "price": None,
            "currency": "dollar",
            "bottle_size": "",
            "stock": None,
            "image_url": "",
            "upc": "",
            "status": False,
            "category": "",
            "subcategory": ""
        }
        res = self.client.post(reverse('product-list'), data=data, format="json")
        self.assertEqual(res.status_code, 403)
        self.login_no()
        res = self.client.post(reverse('product-list'), data=data, format="json")
        self.assertEqual(res.status_code, 403)

    def test_product_create_valid_data(self):
        self.login()
        data = {
            "sku": "test2",
            "name": "",
            "brand": "",
            "weight": None,
            "year": None,
            "price": None,
            "currency": "dollar",
            "bottle_size": "",
            "stock": None,
            "image_url": "",
            "upc": "",
            "status": False,
            "abv": "",
            "category": "",
            "subcategory": ""
        }
        res = self.client.post(reverse('product-list'), data=data, format="json")
        self.assertEqual(res.status_code, 201)
        data["sku"] = ""
        res = self.client.post(reverse('product-list'), data=data, format="json")
        self.assertEqual(res.status_code, 400)


class ProductDeletePermissions(SimpleTestSetup):
    def test_product_delete_no_perms(self):
        order, created = Product.objects.get_or_create(sku="test")
        res = self.client.delete(reverse('product-detail', kwargs={"pk": order.id}))
        self.assertEqual(res.status_code, 403)
        self.login_no()
        res = self.client.delete(reverse('product-detail', kwargs={"pk": order.id}))
        self.assertEqual(res.status_code, 403)

    def test_product_delete_perms(self):
        self.login()
        order, created = Product.objects.get_or_create(sku="test")
        res = self.client.delete(reverse('product-detail', kwargs={"pk": order.id}))
        print(res.data)
        self.assertEqual(res.status_code, 204)

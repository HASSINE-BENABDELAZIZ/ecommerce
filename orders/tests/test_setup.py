from rest_framework.test import APITestCase, APISimpleTestCase

from accounts.models import User


class SimpleTestSetup(APISimpleTestCase):
    databases = '__all__'

    def login(self):
        user, created = User.objects.get_or_create(username="test@test.com", is_superuser=True, is_staff=True)
        user.set_password("test")
        user.save()
        self.client.login(username=user.username, password="test")

    def login_no(self):
        user, created = User.objects.get_or_create(username="tes1t@test.com", is_superuser=False, is_staff=False)
        user.set_password("test")
        user.save()
        self.client.login(username=user.username, password="test")


class TestSetup(APITestCase):
    pass

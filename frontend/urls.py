from django.urls import path

from .views import index

app_name = 'front'

urlpatterns = [
    path('', index.as_view(), name="order_list"),
]

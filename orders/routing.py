from django.urls import path

from orders.consumers import UpdateExport

ws_urlpatterns = [
    path('export_status/', UpdateExport.as_asgi())

]

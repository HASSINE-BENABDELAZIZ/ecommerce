from django.urls import path

from . import api_views as views

urlpatterns = [
    path('orders/',
         views.OrderList.as_view(),
         name='order-list'),
    path('orders/<int:pk>/',
         views.OrderDetail.as_view(),
         name='order-detail'),
    path('orders_items/',
         views.OrderItemsList.as_view(),
         name='orderitems-list'),
    path('orders_items/<int:pk>/',
         views.OrderItemsDetail.as_view(),
         name='orderitems-detail'),
    path('shipments/',
         views.ShipmentList.as_view(),
         name='shipment-list'),
    path('shipments/<int:pk>/',
         views.ShipmentDetail.as_view(),
         name='shipment-detail'),
    path('carriers/',
         views.CarrierList.as_view(),
         name='carrier-list'),
    path('carriers/<int:pk>/',
         views.CarrierDetail.as_view(),
         name='carrier-detail'),

]

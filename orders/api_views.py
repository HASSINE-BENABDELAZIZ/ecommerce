from rest_framework import filters
from rest_framework import generics

from orders.models import Order, Shipment, OrderItems, Carrier
from utils.permissions import CanViewOrder, CanViewOrderItems, CanEditOrderItems, \
    CanEditShipment, CanViewShipment, CanEditOrder
from .serializers import OrderSerializer, ShipmentSerializer, OrderItemsSerializer, CarrierSerializer


class OrderList(generics.ListCreateAPIView):
    permission_classes = [CanViewOrder]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["city", "company", "customer_name", "customer_email",
                     "id", "order_number", "created_at",
                     "origin", "phone", "state", "status", "street_1", "street_2",
                     "substatus", "children__name", "children__sku"
                     ]

    def get_queryset(self):
        orders = super().get_queryset()
        if self.request.GET.get("status"):
            orders = orders.filter(status=self.request.GET.get("status"))
        if self.request.GET.get("substatus"):
            orders = orders.filter(substatus=self.request.GET.get("substatus"))
        return orders


class OrderDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [CanEditOrder]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


# -----------------------------------------------
class ShipmentList(generics.ListCreateAPIView):
    permission_classes = [CanViewShipment]
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer


class ShipmentDetail(generics.RetrieveDestroyAPIView):
    permission_classes = [CanEditShipment]
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer


# -----------------------------------------------
class CarrierList(generics.ListCreateAPIView):
    permission_classes = [CanViewShipment]
    queryset = Carrier.objects.all()
    serializer_class = CarrierSerializer


class CarrierDetail(generics.RetrieveDestroyAPIView):
    permission_classes = [CanEditShipment]
    queryset = Carrier.objects.all()
    serializer_class = CarrierSerializer


# ---------------------------------------------------
class OrderItemsList(generics.ListCreateAPIView):
    permission_classes = [CanViewOrderItems]
    queryset = OrderItems.objects.all()
    serializer_class = OrderItemsSerializer
    filterset_fields = ["order__id"]


class OrderItemsDetail(generics.RetrieveDestroyAPIView):
    permission_classes = [CanEditOrderItems]
    queryset = OrderItems.objects.all()
    serializer_class = OrderItemsSerializer

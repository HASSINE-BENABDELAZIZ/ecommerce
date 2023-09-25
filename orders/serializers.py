from rest_framework import serializers

from accounts.models import User
from orders.models import Order, OrderItems, Shipment, Carrier


class OrderSerializerUsername(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'id')


class OrderItemsNestedSerializer(serializers.ModelSerializer):
    parent_id = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all(), source='order.id')

    class Meta:
        model = OrderItems
        fields = ("sku", "quantity", "name", "parent_id", 'original_order_item_id', 'original_product')
        depth = 1

    def create(self, validated_data):
        item = OrderItems.objects.create(parent=validated_data['order']['id'],
                                         sku=validated_data['sku'],
                                         name=validated_data['name'],
                                         quantity=validated_data['quantity'])

        return item


class OrderSerializer(serializers.ModelSerializer):
    user = OrderSerializerUsername(read_only=True)
    children = OrderItemsNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["city", "company", "customer_name", "customer_email",
                  "id", "order_number", "created_at", "zip_code",
                  "origin", "phone", "state", "status", "street_1", "street_2",
                  "substatus", "user", "children"
                  ]


class CarrierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrier
        fields = '__all__'


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class OrderItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItems
        fields = '__all__'


class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = '__all__'

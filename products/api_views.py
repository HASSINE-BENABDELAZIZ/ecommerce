from rest_framework import generics
from products.models import Product
from utils.permissions import CanEditProduct, CanViewProduct
from .serializers import ProductSerializer


class ProductList(generics.ListCreateAPIView):
    permission_classes = [CanViewProduct]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductDetail(generics.RetrieveDestroyAPIView):
    permission_classes = [CanEditProduct]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

from django.urls import path

from products import api_views

urlpatterns = [
    path('',
         api_views.ProductList.as_view(),
         name='product-list'),
    path('<int:pk>/',
         api_views.ProductDetail.as_view(),
         name='product-detail'),

]

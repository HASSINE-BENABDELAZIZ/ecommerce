from django.urls import path

from .views import *

urlpatterns = [
    path('',
         Dashboard.as_view(),
         name='dashboard'),
    path('today', Today.as_view(), name="today"),
    path('completed', Completed.as_view(), name="completed"),
    path('shipped', Shipped.as_view(), name="shipped"),
    path('status', Status.as_view(), name="status"),
    path('total', Total.as_view(), name="total"),
    path('day',
         Daily.as_view(),
         name='daily'),
    path('week',
         Weekly.as_view(),
         name='weekly'),
    path('year',
         Yearly.as_view(),
         name='yearly'),
    path('month/',
         Monthly.as_view(),
         name='monthly'),
]

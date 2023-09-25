
from django.urls import path

from .views import MarketList, MarketCreate, MarketChange, MarketDeleteView

app_name = "marketplace"

urlpatterns = [
    path('', MarketList.as_view(), name="market_list"),
    path('new/', MarketCreate.as_view(), name="market_create"),
    path('<int:pk>/', MarketChange.as_view(), name="market_update"),
    path("<int:pk>/delete/", MarketDeleteView.as_view(), name="market_delete"),
]

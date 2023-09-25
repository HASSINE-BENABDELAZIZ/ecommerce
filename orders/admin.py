from django.contrib import admin

from .models import Order, OrderItems, \
    OrderImports, Address, \
    Carrier, Shipment, TrackingActivities, OrderExportFilters, OrderExportFiles, FPCarrier, Cite, Ville, Delegation

admin.site.register(Shipment)
admin.site.register(TrackingActivities)

admin.site.register(Order)
admin.site.register(OrderItems)
admin.site.register(OrderImports)
admin.site.register(FPCarrier)
admin.site.register(Address)
admin.site.register(Carrier)
admin.site.register(OrderExportFilters)
admin.site.register(OrderExportFiles)
admin.site.register(Cite)
admin.site.register(Ville)
admin.site.register(Delegation)
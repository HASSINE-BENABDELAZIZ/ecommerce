from django.urls import path

from .views import OrderList, OrderCreate1, OrderLogs, \
    OrderChange, OrderDeleteView, ImportFiles, \
    import_shipstation, gocode_google, save_internal_note, \
    OrderBulkDeleteView, CarrierCreate, CarrierChange, \
    CarrierList, CarrierDeleteView, AddressCreate, AddressChange, \
    AddressList, OrderBulkShip, ShipmentDeleteView, ExportOrder, OrderBulkExportView, orderBL, \
    ResumeExport, ExportPDF, AddressDeleteView, load_order_data, load_delegation_data, load_ville_data, load_zip_code

app_name = 'orders'

urlpatterns = [
    path('bl', orderBL.as_view(), name="order_bl"),
    path("export_pdf/", ExportPDF.as_view(), name="export_pdf"),
    path("resume_export/", ResumeExport.as_view(), name="resume_export"),
    path('', OrderList.as_view(), name="order_list"),
    path('details/<pk>/', OrderChange.as_view(), name="change_list"),
    path('shipment/delete/<pk>', ShipmentDeleteView.as_view(), name="shipment_delete"),
    path('create/', OrderCreate1.as_view(), name="order_create"),
    path('logs/', OrderLogs.as_view(), name="order_logs"),
    path("delete/<pk>/", OrderDeleteView.as_view(), name="order_delete"),
    path('import_files/', ImportFiles.as_view(), name="import_files"),
    path("delete_bulk/", OrderBulkDeleteView.as_view(), name="delete_bulk"),
    path("move_to_ship/", OrderBulkShip.as_view(), name="move_to_ship"),
    path("import_shipstation/", import_shipstation, name="import_shipstation"),
    path("import_zipcode/", gocode_google, name="import_zipcode"),
    path("save_internal_note/", save_internal_note, name="save_internal_note"),
    path("export/", ExportOrder.as_view(), name="export"),
    path("carriercreate/", CarrierCreate.as_view(), name="CarrierCreate"),
    path('carrier/<pk>/', CarrierChange.as_view(), name="change_carrier"),
    path('carrier/', CarrierList.as_view(), name="carrier_list"),
    path("carrier/<pk>/delete/",
         CarrierDeleteView.as_view(), name="carrier_delete"),
    path("orders/export_bulk", OrderBulkExportView.as_view(), name="export_bulk"),
    path("addresscreate/",
         AddressCreate.as_view(), name="AddressCreate"),
    path('address/<pk>/',
         AddressChange.as_view(), name="change_address"),
    path('address/',
         AddressList.as_view(), name="address_list"),
    path("address/<pk>/delete/",
         AddressDeleteView.as_view(), name="address_delete"),

    path('ajax/load-order-data/', load_order_data, name='ajax_load_order_data'),
    path('ajax/load-delegation-data/', load_delegation_data, name='ajax_load_delegation_data'),
    path('ajax/load-ville-data/', load_ville_data, name='ajax_load_ville_data'),
    path('ajax/load-zipcode-data/', load_zip_code, name='ajax_load_zip_code'),
]

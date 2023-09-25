from django.urls import path
from .views import ProductList, ProductChange, ProductCreate, \
    DownloadProducts, ProductLogs, ProductDeleteView, GetStock, ProductSearch, CategoryCreate, \
    SubCategoryCreate, ajax_load_sub_category_data

app_name = 'products'

urlpatterns = [

    path('', ProductList.as_view(), name="product_list"),
    path('details/<pk>/', ProductChange.as_view(), name="change_list"),
    path('create/', ProductCreate.as_view(), name="product_create"),
    path('category/create/', CategoryCreate.as_view(), name="category_create"),
    path('subcategory/create/', SubCategoryCreate.as_view(), name="subcategory_create"),
    path('download/', DownloadProducts.as_view(), name="download_product"),
    path('logs/', ProductLogs.as_view(), name="product_logs"),
    # path('subcat/', SubCategoryView.as_view(), name="subcat"),
    path('search/', ProductSearch.as_view(), name="product_search"),
    path("details/<pk>/delete/", ProductDeleteView.as_view(), name="product_delete"),
    path("get_stock/<pk>/", GetStock.as_view()),

    path('ajax/load-sub-category-data/', ajax_load_sub_category_data, name='ajax_load_sub_category_data'),

]

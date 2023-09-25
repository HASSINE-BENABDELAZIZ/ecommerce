from datetime import datetime
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from rest_framework import generics
from utils.mongodb import mongo_db
from .forms import ProductForm, CategoryForm, SubCategoryForm
from .models import Product, SubCategory, Category
from django.http import HttpResponse
from io import BytesIO
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa

class ProductList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Product
    paginate_by = 100
    template_name = 'product/product_list.html'
    permission_required = 'products.view_product'

    def get_context_data(self, **kwargs):
        context = super(ProductList, self).get_context_data()
        context.update({"category_form": CategoryForm, "subcategory_form": SubCategoryForm})
        return context

    def get_template_names(self):
        return "include/product_tr.html" if self.request.is_ajax() else self.template_name

    def get_queryset(self):
        search = self.request.GET.get("search")
        if search:
            queryset = Product.objects.filter(
                Q(name__icontains=search) |
                Q(sku__icontains=search) |
                Q(brand__icontains=search)
                | Q(category__name__icontains=search) |
                Q(price__icontains=search))
        else:
            queryset = Product.objects.all()

        if not self.request.user.is_superuser or not self.request.user.is_staff:
            queryset = queryset.filter(marketplace_id=self.request.user.marketplace_id)

        return queryset


class ProductChange(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/create_product.html'
    success_url = reverse_lazy('products:product_list')
    permission_required = ('products.change_product',)

    def get_initial(self):
        initial = super(ProductChange, self).get_initial()
        initial["subcategory"] = SubCategory.objects.filter(category_id=self.object.category_id)
        return initial

    def get_context_data(self, **kwargs):
        context = super(ProductChange, self).get_context_data()
        context['edit'] = 1
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Produit mis à jour avec succès.')
        return super(ProductChange, self).form_valid(form)


class ProductCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/create_product.html'
    permission_required = 'products.add_product'

    def get_success_url(self):
        if 'save_data' in self.request.POST:
            return reverse_lazy("products:product_list")
        elif 'save_edit' in self.request.POST:
            return reverse_lazy('products:change_list', kwargs={'pk': self.object.id})
        else:
            return reverse_lazy("products:product_create")

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Produit créé avec succès.')
        return super(ProductCreate, self).form_valid(form)


class ProductDeleteView(PermissionRequiredMixin, DeleteView):
    model = Product
    permission_required = ('products.delete_product',)
    success_url = reverse_lazy("products:product_list")


class ProductLogs(LoginRequiredMixin, PermissionRequiredMixin, View):
    paginate_by = 50
    template_name = 'user/user_logs.html'
    permission_required = ('products.view_product',)

    def get(self, request, *args, **kwargs):
        db = mongo_db()
        search = self.request.GET.get("search", "")
        order_id = request.GET.get("id", "")
        data = [
            {
                "$or": [
                    {
                        'updates': {"$regex": f".*{search}.*"}
                    }, {
                        'user': {"$regex": f".*{search}.*"}
                    },
                ]
            },

        ]
        if order_id:
            data.append({'instance_id': int(order_id)})
        data = {"$and": data}
        query = db.products.find(data).sort('created_at', -1)
        page = request.GET.get('page', 1)
        if not page:
            page = 1
        items = [r for r in query]

        from utils.pagination_controller import pagination
        current_page = pagination(items, len(items), self.paginate_by, int(page))

        if request.is_ajax():
            return render(request, "user/user_logs_tr.html", current_page)
        else:
            return render(request, self.template_name, current_page)


class ProductSearch(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        if request.GET.get('action') == 'post':
            search_string = str(request.GET.get('ss'))

            if search_string is not None:
                search_string = Product.objects.filter(
                    Q(name__icontains=search_string) |
                    Q(sku__icontains=search_string) |
                    Q(brand__icontains=search_string) |
                    Q(price__icontains=search_string))[:5]

                data = serializers.serialize('json', list(
                    search_string), fields=('id', 'name', 'sku', 'category', 'brand', 'price', 'image_url'))

                return JsonResponse({'search_string': data})


def download_items_from_3jms(mon_insert_id=None):
    from .tasks import jms_import_products_api
    jms_import_products_api.delay(mon_insert_id)


class DownloadProducts(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = reverse_lazy('login')
    redirect_field_name = 'redirect_to'
    template_name = 'update_items.html'
    permission_required = ('products.add_product',)

    def get(self, request, *args, **kwargs):
        page_size = 30
        db = mongo_db()
        search = self.request.GET.get("search", "")
        data = [{
            'user': {"$regex": f".*{search}.*"}
        }, {
            'duration': {"$regex": f".*{search}.*"}
        }, {
            'status': {"$regex": f".*{search}.*"}
        }]

        data = {"$or": data}
        query = db.product_logs.find(data).sort('created_at', -1)
        total = query.count()
        page = request.GET.get('page', 1)
        if not page:
            page = 1
        items = [r for r in query]
        paginator = Paginator(items, page_size)
        try:
            items = paginator.page(page)

        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)
        if total % 30 == 0:
            items.paginator.num_pages = total // page_size
        else:
            items.paginator.num_pages = total // page_size + 1
        items.number = int(page)
        return render(request, self.template_name,
                      {"data": items,
                       "total": total,
                       'is_paginated': items.paginator.num_pages})

    def post(self, request, *args, **kwargs):
        time_now = datetime.now()
        db = mongo_db()
        id_code = db.product_logs.insert_one(
            {"user": request.user.email if request.user.email else "",
             "status": "Processing",
             "created_at": time_now,
             })
        from .tasks import jms_import_products_api
        jms_import_products_api.delay(str(id_code.inserted_id))
        return redirect("products:download_product")


class GetStock(View):
    def get(self, *args, **kwargs):
        if kwargs.get("pk") != "null":
            return JsonResponse({"stock": Product.objects.get(id=kwargs.get("pk")).stock})
        return JsonResponse({"stock": "UC"})


class CategoryCreate(CreateView):
    model = Category
    fields = "__all__"
    success_url = reverse_lazy("products:product_list")

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Catégorie ajoutée avec succès.')
        return super(CategoryCreate, self).form_valid(form)


class SubCategoryCreate(CreateView):
    model = SubCategory
    fields = "__all__"
    success_url = reverse_lazy("products:product_list")

    def form_valid(self, form):
        print(form)
        messages.add_message(self.request, messages.SUCCESS, 'Sous-Catégorie ajoutée avec succès.')
        return super(SubCategoryCreate, self).form_valid(form)


def ajax_load_sub_category_data(request):
    category_id = request.GET.get('category_id')
    data = {'sub_categories': list(SubCategory.objects.filter(category_id=category_id).values())}
    return JsonResponse(data, safe=False)

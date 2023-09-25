import os
import requests
from datetime import datetime

from django.contrib import messages
from barcode.writer import ImageWriter
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, \
    PermissionRequiredMixin
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, RedirectView
from xhtml2pdf import pisa

from beez.api import Beezit
from beez.forms import BeezCarrierForm
from beez.models import BeezCarrier
from colissimo.forms import ColissimoCarrierForm
from fparcel.api import Fparcel
from marketplace.models import Marketplace
from products.models import Product
from utils.breadcrumb import BreadCrumbMixin
from utils.mongodb import mongo_insert, mongo_db
from utils.pagination_controller import pagination_mongo, pagination
from .forms import OrderForm, OrderItemsFormset, OrderItemsFormset1, \
    OrderImportsForm, ExportFileForm, FPCarrierForm, DroppexCarrierForm
from .helpers import get_notes
from .models import OrderImports, OrderNotes, \
    OrderItems, Carrier, Address, Shipment, TrackingActivities, Order, OrderExportFiles, FPCarrier, Delegation, Ville, \
    Cite
from .tasks import shipstation_import_api, import_orders_files, export_orders_files

from django.shortcuts import render
from django.http import HttpResponse
from io import BytesIO
from django.template.loader import get_template
from django.views import View
from reportlab.pdfgen import canvas

from xhtml2pdf import pisa
from django.shortcuts import render
import barcode
from barcode.writer import ImageWriter
from barcode.codex import Code128
from orders.models import Order
from django.conf import settings
# Create your views here.
"""def generate_barcode(request , order_number):
    # Choose the barcode type, for example, CODE128
    barcode_type = barcode.CODE128()

    # Create the barcode object with the unordered number
    barcode_value = str(order_number)
    barcode_image = barcode.generate(barcode_type, barcode_value)

    # Save the barcode image to a file
    filename = f"barcode_{order_number}.png"
    barcode_image.save(filename)

    # Return the path or URL of the generated barcode image
    return filename"""



def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    data = { }
    context_dict.update(data)
    html = template.render(context_dict)

    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859_1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
class orderBL(View):
    def get(self,request, *args, **kwargs):
        pk_list = request.GET.getlist("pk")
        orders = Order.objects.filter(id__in=pk_list)
        for order in orders:
            barcode_value = order.code_partenaire
            ean = Code128(barcode_value, writer=ImageWriter())
            barcode_filename = ean.save('barcode')
            order.barcode_filename = barcode_filename
            order.save()  # Save the updated order
        context = {'orders': orders}
        pdf = render_to_pdf('include/orders_pdf.html', context_dict=context)
        return HttpResponse(pdf, content_type='application/pdf')


def update_elasticsearch_order(order):
    items = OrderItems.objects.filter(order=order)
    notes = OrderNotes.objects.filter(order=order)
    for item in items:
        item.save()
    for note in notes:
        note.save()


class ShipmentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    # specify the model you want to use
    model = Shipment
    permission_required = ('orders.delete_shipment',)

    # can specify success url
    # url to redirect after successfully
    # deleting object
    success_url = reverse_lazy('orders:order_list')

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL.
        """
        self.object = self.get_object()
        order = self.object.order
        order.status = "NO"
        order.substatus = ""
        order.save()

        for item in OrderItems.objects.filter(order=order):
            item.save()
            product = Product.objects.get(id=item.original_order_item_id)
            product.stock = product.stock + item.quantity
            product.save()
        success_url = self.get_success_url()
        self.object.delete()
        update_elasticsearch_order(order)
        return HttpResponseRedirect(success_url)


class OrderBulkExportView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ('orders.delete_order',)

    def post(self, request, *args, **kwargs):
        orders = request.POST.getlist("order_list[]")
        orders = [int(order) for order in orders]
        orders = Order.objects.filter(id__in=orders)
        file = OrderExportFiles.objects.create(user=request.user)
        export_orders_files(orders=orders, export_id=file.id)
        file = OrderExportFiles.objects.get(id=file.id)
        return JsonResponse({"Success": True, "file": file.file_url})


class OrderBulkDeleteView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ('orders.delete_order',)

    def post(self, request, *args, **kwargs):
        orders = request.POST.getlist("order_list[]")
        orders = [int(order) for order in orders]
        Order.objects.filter(id__in=orders).delete()
        return JsonResponse({"Success": True})


class OrderBulkShip(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ('orders.change_order',)

    def post(self, request, *args, **kwargs):
        orders = request.POST.getlist("order_list[]")
        carrier_id = request.POST.get("carrier_id")
        orders = [int(order) for order in orders]
        error = False

        for order in Order.objects.filter(id__in=orders):
            order.status = "NO"
            order.substatus = ""
            for item in OrderItems.objects.filter(order=order):
                if Product.objects.filter(id=item.original_product_id):
                    product = Product.objects.get(id=item.original_product_id)
                    product.stock = product.stock - item.quantity if product.stock else 0 - item.quantity
                    if product.stock < 0:
                        error = True
                        note = "out of stock"
                else:
                    note = "there is an UC item"
                    error = True
            if not error:

                note = f"{request.user} shipped this order"
                carrier = Carrier.objects.get(id=carrier_id)
                if carrier.carrier == "beezit":
                    result = Beezit().ship(order, BeezCarrier.objects.get(id=int(carrier_id)))
                else:
                    result = Fparcel().ship(order, FPCarrier.objects.get(id=int(carrier_id)))
                if result.get("error"):
                    note = f"{result}"
                    error = True
                else:
                    order.status = "OS"
                    order.substatus = "PT"
                    order.save()
                    for item in OrderItems.objects.filter(order=order):
                        item.save()
                        product = Product.objects.get(id=item.original_product_id)
                        product.stock = product.stock - item.quantity
                        product.save()

            OrderNotes.objects.create(note=note,
                                      user=request.user,
                                      created_at=datetime.now(),
                                      order=order)
            order.save()
            update_elasticsearch_order(order)
            if error:
                messages.add_message(request,
                                     messages.ERROR,
                                     f'Order {order.order_number} {note}.',
                                     extra_tags='order_tr')

            else:

                messages.add_message(request,
                                     messages.INFO,
                                     f'Order {order.order_number} {note}.',
                                     extra_tags='order_tr')

        return JsonResponse({"Success": True})


@login_required()
def save_internal_note(request):
    from datetime import datetime
    OrderNotes.objects.create(note=request.GET.get("note", ""),
                              user=request.user,
                              created_at=datetime.now(),
                              order=Order.objects.get(
                                  id=int(
                                      request.GET.get(
                                          "pk",
                                          "None"))))
    return JsonResponse({"order": int(request.GET.get("pk", "None")),
                         "user": request.user.username,
                         "Note": request.GET.get("note", ""),
                         "created_at": datetime.now().
                        strftime("%b. %-d   , %Y, %-I:%M %p.")
                        .replace("AM", "a.m").replace("PM", "p.m"),
                         })


@login_required()
def gocode_google(request, zipcode):
    db = mongo_db()
    zipcode = request.GET.get("zipcode", '')
    country = "Tunisia"
    key = os.environ.get('GOOGLE_API_GL', '')

    if not db.google_api.count_documents({"zipcode": zipcode}):
        try:
            response = requests.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params={
                    "components": f"postal_code:{zipcode}|country:{country}",
                    "key": key
                },
                headers={'content-type': 'application/json'}
            )
            response.raise_for_status()  # Raise an exception for non-2xx responses

            data = response.json()
            if data.get("status") == "OK":
                address = data["results"][0]["formatted_address"].split(",")
                city = address[0]
                state = address[1].split(" ")[1]
                mongo_insert("google_api", {
                    "zipcode": zipcode,
                    "country": country,
                    "city": city,
                    "state": state,
                    "address": data["results"][0]["formatted_address"],
                    "results": data
                })
        except (requests.RequestException, KeyError) as e:
            # Handle the exception or log the error
            print(f"Error occurred: {str(e)}")

    query = db.google_api.find({"zipcode": zipcode})
    result = [i for i in query]

    if result:
        json_result = {
            "country": result[0].get("country"),
            "city": result[0].get("city"),
            "state": result[0].get("state"),
            "address": result[0].get("address")
        }
    else:
        json_result = {}

    return json_result


@login_required()
def import_shipstation(request):
    shipstation_import_api.delay()

    return redirect("orders:order_list")


class ImportFiles(BreadCrumbMixin,
                  LoginRequiredMixin,
                  PermissionRequiredMixin,
                  ListView):
    template_name = 'order/import.html'
    paginate_by = 50
    model = OrderImports
    permission_required = ('orders.add_orderimports',)

    def get(self, request, *args, **kwargs):

        form = OrderImportsForm(request.POST or None, request.FILES or None)
        search = request.GET.get("search", '')
        page = request.GET.get("page", 1)
        if not page:
            page = 1
        files = OrderImports.objects.filter(
            user__username__icontains=search,
            status__icontains=search).order_by("-id")
        from utils.pagination_controller import pagination
        current_page = pagination(files,
                                  OrderImports.objects.count(),
                                  self.paginate_by, page)
        db = mongo_db()

        for file in current_page["page_obj"]:
            file.logs = (db.error_import_logs.find_one({"file_id": file.id}))

        current_page.update({"form": form})
        current_page.update(self.get_breadcrumb())

        if request.is_ajax():
            return render(request,
                          "include/order_import_tr.html",
                          current_page)
        else:

            return render(request, self.template_name, current_page)

    def post(self, request, *args, **kwargs):
        form = OrderImportsForm(request.POST, request.FILES)
        f1 = form.save()
        f1.status = "Processing"
        f1.user = request.user
        f1.save()
        import_orders_files.delay(f1.id, request.user.id)

        search = request.GET.get("search", '')
        page = request.GET.get("page", 1)
        if not page:
            page = 1
        files = OrderImports.objects.filter(
            user__username__icontains=search,
            status__icontains=search).order_by("-id")
        from utils.pagination_controller import pagination
        current_page = pagination(files, OrderImports.objects.all().count(),
                                  self.paginate_by,
                                  page)
        current_page.update({"form": form})
        current_page.update(self.get_breadcrumb())

        db = mongo_db()
        for file in current_page["page_obj"]:
            file.logs = (db.error_import_logs.find_one({"file_id": file.id}))

        if request.is_ajax():
            return render(request,
                          "include/order_import_tr.html",
                          current_page)
        else:

            return render(request,
                          self.template_name,
                          current_page)


class RedirectTolist(RedirectView):
    url = reverse_lazy("orders:order_list")


class OrderDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    # specify the model you want to use
    model = Order
    permission_required = ('orders.delete_order',)

    # can specify success url
    #  to redirect after successfully
    # deleting object
    success_url = reverse_lazy('orders:order_list')


class OrderList(BreadCrumbMixin, LoginRequiredMixin, PermissionRequiredMixin, ListView):
    login_url = reverse_lazy('login')
    redirect_field_name = 'redirect_to'
    template_name = 'order/product_list.html'
    context_object_name = 'order_list'
    paginate_by = 100
    model = Order
    permission_required = ('orders.view_order',)

    def get_template_names(self):
        if self.request.is_ajax():
            return "include/order_tr.html"
        return self.template_name

    def get_queryset(self):
        query = super(OrderList, self).get_queryset()
        search = self.request.GET.get("search", '')
        status = self.request.GET.get("status", "")
        substatus = self.request.GET.get("substatus", "")
        sort_value = self.request.GET.get("sort_value", "-created_at")
        sort_type = "asc"
        sort_name = sort_value
        if sort_value[0] == "-":
            sort_type = "desc"
            sort_name = sort_value[1:]
        if self.request.GET.get("search"):
            query = query.filter(
                Q(order_number__icontains=search) |
                Q(customer_name__icontains=search) |
                Q(customer_email__icontains=search) |
                Q(company__icontains=search) |
                Q(street_1__icontains=search) |
                Q(street_2__icontains=search) |
                Q(zip_code__icontains=search) |
                Q(state__icontains=search) |
                Q(cite__icontains=search) |
                Q(phone__icontains=search) |
                Q(status__icontains=search) |
                Q(substatus__icontains=search) |
                Q(tracking_code__icontains=search) |
                Q(origin__icontains=search) |
                Q(user__username__icontains=search)
            )
        if self.request.GET.get("status"):
            query = query.filter(status=status)
        if self.request.GET.get("substatus"):
            query = query.filter(substatus=substatus)
        if not self.request.user.is_superuser or not self.request.user.is_staff:
            query = query.filter(marketplace_id=self.request.user.marketplace_id)

        return query.order_by(sort_value)

    def get_context_data(self, **kwargs):
        context = super(OrderList, self).get_context_data()
        sort_value = self.request.GET.get("sort_value", "-created_at")
        context.update(self.get_breadcrumb())
        context.update({"sort_value": sort_value})
        context.update({"carrier": Carrier.objects.all()})
        orders = context.get("page_obj", "")
        id_orders = []
        for order in orders:
            if not int(order.id) in id_orders:
                id_orders.append(int(order.id))
                order.shipment = Shipment.objects.filter(order__id=order.id).last()
                order.activity = TrackingActivities.objects.filter(order__id=order.id).last()
                order.items = OrderItems.objects.filter(
                    order=int(order.id))
                for item in order.items:
                    if Product.objects.filter(
                            id=item.original_product_id).count() > 0:
                        item.linked_item = Product.objects.filter(
                            id=item.original_product_id)[0]

        return context


class OrderCreate1(BreadCrumbMixin, PermissionRequiredMixin, CreateView):
    permission_required = ('orders.add_order',)
    form_class = OrderForm
    template_name = 'order/create_product.html'

    def get_context_data(self, **kwargs):
        context = super(OrderCreate1, self).get_context_data(**kwargs)
        context['order_items_formset'] = OrderItemsFormset(user=self.request.user)
        context['order_items_formset1'] = OrderItemsFormset1(user=self.request.user)
        context['product'] = Product.objects.all()[:4]
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        product_meta_formset = OrderItemsFormset(self.request.POST, user=self.request.user)
        if form.is_valid() and product_meta_formset.is_valid():

            messages.add_message(request,
                                 messages.INFO,
                                 'Order Successfully created.')
            return self.form_valid(form, product_meta_formset)
        else:
            return self.form_invalid(form, product_meta_formset)

    def form_valid(self, form, order_items_formset):
        order = self.object = form.save(commit=False)
        order.user = self.request.user

        # Retrieve geolocation data based on the client_zipcode
        zipcode = form.cleaned_data['client_zipcode']
        response = gocode_google(request=self.request, zipcode=zipcode)  # Pass the request argument
        if response.get('city'):
            order.expiditeur_ville = response['city']
        if response.get('state'):
            order.expiditeur_deligaiton = response['state']
        if response.get('address'):
            order.client_address = response['address']

        self.object.save()
        # saving ProductMeta Instances
        product_metas = order_items_formset.save(commit=False)
        for meta in product_metas:
            meta.order = order
            meta.save()
        if self.request.POST.get("save_data"):
            return redirect("orders:order_list")
        elif self.request.POST.get("save_edit"):
            return redirect("orders:change_list", str(Order.objects.get(id=order.id).id))
        else:
            return redirect("orders:order_create")

    def form_invalid(self, form, order_items_formset):
        return self.render_to_response(
            self.get_context_data(form=form, order_items_formset=order_items_formset)
        )


class OrderChange(BreadCrumbMixin,
                  LoginRequiredMixin,
                  PermissionRequiredMixin,
                  UpdateView):
    permission_required = ('orders.change_order',)

    fields = ["username", "email", "password"]
    login_url = reverse_lazy('login')
    redirect_field_name = 'redirect_to'
    template_name = 'order/product_change.html'
    context_object_name = 'order'

    def get(self, request, *args, **kwargs):
        form = OrderForm(instance=Order.objects.get(id=kwargs.get("pk", None)))
        formset = OrderItemsFormset1(
            instance=Order.objects.get(
                id=kwargs.get("pk", None)
            ),
            user=self.request.user
        )

        current_page = {
            "order_items_formset": formset,
            "form": form,
            "order": Order.objects.get(
                id=kwargs.get("pk",
                              None)
            ),
            "notes": get_notes(kwargs.get("pk", None)),
        }
        current_page.update({"shipment": Shipment.objects.filter(order__id=kwargs.get("pk")).last()})
        current_page.update(
            {"activities": TrackingActivities.objects.filter(order__id=kwargs.get("pk")).order_by("-happened_at")})
        current_page.update(self.get_breadcrumb())
        return render(request, self.template_name, current_page)

    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None,
                         instance=Order.objects.get(
                             id=kwargs.get("pk", "")))
        formset = OrderItemsFormset1(request.POST or None,
                                     instance=Order.objects.get(
                                         id=kwargs.get("pk", "")))
        if form.is_valid() and formset.is_valid():
            order = form.save()
            order.save()
            formset.save()
            update_elasticsearch_order(order)
            messages.add_message(request,
                                 messages.INFO,
                                 'Order Successfully updated.')
        else:
            current_page = {
                "order_items_formset": formset,
                "form": form,
                "order": Order.objects.get(
                    id=kwargs.get("pk",
                                  None)
                )}
            current_page.update(self.get_breadcrumb())
            return render(request,
                          self.template_name,
                          current_page)
        return redirect(reverse("orders:order_list"))


class OrderLogs(BreadCrumbMixin,
                LoginRequiredMixin,
                PermissionRequiredMixin,
                View):
    permission_required = ('orders.view_order',)

    login_url = reverse_lazy('login')
    redirect_field_name = 'redirect_to'
    template_name = 'user/user_logs.html'
    paginate_by = 50

    def get(self, request, *args, **kwargs):

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
        page = request.GET.get('page', 1)

        if not page:
            page = 1

        current_page = pagination_mongo("orders",
                                        data,
                                        self.paginate_by,
                                        int(page))
        current_page.update(self.get_breadcrumb())

        if request.is_ajax():
            return render(request, "user/user_logs_tr.html",
                          current_page)
        else:
            return render(request,
                          self.template_name,
                          current_page)


class ExportOrder(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    redirect_field_name = 'redirect_to'
    form_class = ExportFileForm
    success_url = reverse_lazy("orders:export")
    template_name = 'order/export.html'
    paginate_by = 50
    permission_required = ('exportorderfiles.export_order',)

    def get_template_names(self):
        if self.request.is_ajax():
            return "include/order_export_tr.html"
        return self.template_name

    def get_context_data(self, **kwargs):
        search = self.request.GET.get("search", "")
        from django.db.models import Q
        kwargs.update(pagination(OrderExportFiles.objects.filter(Q(user__username__icontains=search) |
                                                                 Q(status__icontains=search)).order_by('-id'),
                                 OrderExportFiles.objects.count(),
                                 self.paginate_by, self.request.GET.get("page", 1)))
        return super(ExportOrder, self).get_context_data(**kwargs)


class CarrierCreate(BreadCrumbMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Carrier
    fields = "__all__"
    success_url = reverse_lazy("orders:carrier_list")
    permission_required = ('orders.add_carrier',)
    template_name = 'carrier/group_form.html'

    def get_template_names(self):
        return "carrier/form_choice.html" if self.request.is_ajax() else super().get_template_names()

    def get_form_class(self):
        if self.request.GET.get("carrier") == "FP":
            return FPCarrierForm
        elif self.request.GET.get("carrier") == "BEEZIT":
            return BeezCarrierForm
        elif self.request.GET.get("carrier") == "COLISSIMO":
            return ColissimoCarrierForm
        elif self.request.GET.get("carrier") == "DROPPEX":
            return DroppexCarrierForm
        else:
            return super().get_form_class()

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Transporteur créé avec succès.')
        return super().form_valid(form)


class CarrierDeleteView(PermissionRequiredMixin, DeleteView):
    # specify the model you want to use
    model = Carrier
    permission_required = "orders.delete_carrier"
    # can specify success url
    # url to redirect after successfully
    # deleting object
    success_url = reverse_lazy('orders:carrier_list')


class CarrierList(PermissionRequiredMixin, ListView):
    model = Carrier
    paginate_by = 10
    template_name = 'carrier/group_list.html'
    permission_required = ('orders.view_carrier',)

    def get_template_names(self):
        return "include/carrier_tr.html" if self.request.is_ajax() else self.template_name

    def get_queryset(self):
        search = self.request.GET.get("search")
        if search:
            queryset = Carrier.objects.filter(
                Q(carrier__icontains=search)
                | Q(name__icontains=search)
                | Q(account_number__icontains=search)).distinct()
        else:
            queryset = Carrier.objects.all().distinct()

        return queryset


class CarrierChange(BreadCrumbMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Carrier
    fields = "__all__"
    success_url = reverse_lazy("orders:carrier_list")
    permission_required = ('orders.change_carrier',)
    template_name = 'carrier/form_update.html'

    def get_template_names(self):
        return "carrier/form_choice.html" if self.request.is_ajax() else super().get_template_names()

    def get_form_class(self):
        if self.request.GET.get("carrier") == "FP":
            return FPCarrierForm
        elif self.request.GET.get("carrier") == "BEEZIT":
            return BeezCarrierForm
        elif self.request.GET.get("carrier") == "COLISSIMO":
            return ColissimoCarrierForm
        elif self.request.GET.get("carrier") == "DROPPEX":
            return DroppexCarrierForm
        else:
            return super().get_form_class()

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Transporteur mis à jour avec succès.')
        return super().form_valid(form)


class AddressCreate(BreadCrumbMixin,
                    LoginRequiredMixin,
                    PermissionRequiredMixin,
                    CreateView):
    model = Address
    fields = "__all__"
    success_url = reverse_lazy("orders:address_list")
    permission_required = ('orders.add_address',)
    template_name = 'address/group_form.html'

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        messages.add_message(self.request,
                             messages.INFO,
                             'Address Successfully added.')
        return super().form_valid(form)


class AddressDeleteView(PermissionRequiredMixin, DeleteView):
    # specify the model you want to use
    model = Address
    permission_required = "orders.delete_address"
    # can specify success url
    # url to redirect after successfully
    # deleting object
    success_url = reverse_lazy('orders:address_list')


class AddressList(BreadCrumbMixin, PermissionRequiredMixin, ListView):
    login_url = reverse_lazy('login')
    template_name = 'address/group_list.html'
    context_object_name = 'user'
    model = Address
    paginate_by = 10
    permission_required = ('orders.view_address',)
    redirect_field_name = reverse_lazy('index')

    def get_template_names(self):
        if self.request.is_ajax():
            return "include/market_tr.html"
        else:
            return self.template_name

    def get_queryset(self):
        from django.db.models import Q
        search = self.request.GET.get("search", '')
        queryset = Address.objects.filter(
            Q(address__icontains=search)
            | Q(zipcode__icontains=search)

        ).distinct()
        return queryset


class AddressChange(BreadCrumbMixin,
                    LoginRequiredMixin,
                    PermissionRequiredMixin,
                    UpdateView):
    model = Address
    fields = "__all__"
    success_url = reverse_lazy("orders:address_list")
    permission_required = ('orders.change_address',)
    template_name = 'address/form_update.html'

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)  # Get the form as usual

        return form

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        messages.add_message(self.request,
                             messages.INFO,
                             'Address Successfully updated.')
        return super().form_valid(form)


class ResumeExport(LoginRequiredMixin,
                   PermissionRequiredMixin,
                   View):
    success_url = reverse_lazy("orders:address_list")
    permission_required = ('orders.add_carrier',)

    def post(self, request, *args, **kwargs):
        id = request.POST.get("id")
        status = request.POST.get("status")
        instance = OrderExportFiles.objects.get(id=id)
        if status == "pause":
            from celery import current_app

            current_app.control.revoke(instance.task_id, terminate=True)

            instance.status = "paused"
            instance.save()
        elif status == "resume":
            instance.status = "in queue"
            instance.save()
            export_orders_files(export_id=instance.id)

        return JsonResponse({"Success": True, "id": instance.task_id, "status": status})


class ExportPDF(LoginRequiredMixin,
                PermissionRequiredMixin,
                View):
    success_url = reverse_lazy("orders:address_list")
    permission_required = ('orders.add_order',)

    def post(self, request, *args, **kwargs):
        orders = request.POST.getlist("order_list[]")
        status = request.POST.get("status")
        orders = [int(order) for order in orders]
        if status == "OS":
            result = Shipment.objects.filter(order__id__in=orders)
        else:
            items = OrderItems.objects.filter(order__id__in=orders)
            item_unique = []
            for item in items:
                if item.sku not in item_unique:
                    item_unique.append(item.sku)
            result = []
            for sku in item_unique:
                product = Product.objects.filter(sku=sku).last()
                result.append({"sku": sku,
                               "quantity": sum([item.quantity for items in items.filter(sku=sku)]),
                               "name": items.filter(sku=sku).last(),
                               "stock": product.stock if product else "UC"

                               })

        return render_to_pdf("pdf/items_export.html", context_dict={"status": status, "list": result})


def render_to_pdf(template_src, context_dict=None, return_str_content=False):
    if context_dict is None:
        context_dict = {}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_src)
    html = template.render(context_dict)

    from xhtml2pdf.config.httpconfig import httpConfig
    httpConfig.save_keys('nosslcheck', True)
    pisaStatus = pisa.CreatePDF(
        html,
        dest=response)

    if pisaStatus.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')

    if return_str_content:
        return response.getvalue()
    else:
        return response


def load_order_data(request):
    fournisseur_id = request.GET.get('fournisseur_id')
    data = {
        'fournisseur': Marketplace.objects.filter(pk=fournisseur_id).values()[0],
        'produit_fournisseur': list(Product.objects.filter(marketplace_id=fournisseur_id).values())
    }

    return JsonResponse(data, safe=False)


def load_delegation_data(request):
    delegation_id = request.GET.get('delegation_id')
    data = {
        'villes': list(Ville.objects.filter(country_id=delegation_id).values()),
    }

    return JsonResponse(data, safe=False)


def load_ville_data(request):
    ville_id = request.GET.get('ville_id')
    data = {
        'cites': list(Cite.objects.filter(ville_id=ville_id).values()),
    }

    return JsonResponse(data, safe=False)


def load_zip_code(request):
    cite_id = request.GET.get('cite_id')
    data = {
        'zip_code': Cite.objects.filter(pk=cite_id).values()[0],
    }

    return JsonResponse(data, safe=False)

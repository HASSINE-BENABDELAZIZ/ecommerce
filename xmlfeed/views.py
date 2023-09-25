import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, PasswordContextMixin
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import generic
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView, ListView, DetailView, FormView

from marketplace.models import Marketplace
from orders.models import Order, Shipment, TrackingActivities, OrderItems, Carrier
from products.models import Product
from products.tasks import jms_import_products_api
from stats.views import Dashboard
from utils.mongodb import mongo_db
from xmlfeed.forms import ShipmentForm


class PasswordResetView(PasswordContextMixin, generic.FormView):
    email_template_name = 'registration/password_reset_email.html'
    extra_email_context = None
    form_class = PasswordResetForm
    from_email = "info@boujarrait.com"
    html_email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    template_name = 'registration/password_reset_form.html'
    title = _('Password reset')
    token_generator = default_token_generator

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        opts = {
            'use_https': self.request.is_secure(),
            'token_generator': self.token_generator,
            'from_email': self.from_email,
            'email_template_name': self.email_template_name,
            'subject_template_name': self.subject_template_name,
            'request': self.request,
            'html_email_template_name': self.html_email_template_name,
            'extra_email_context': self.extra_email_context,
        }
        form.save(**opts)
        return super().form_valid(form)


class IndexView(TemplateView, LoginView):
    template_name = 'index.html'

    def get_template_names(self):
        if self.request.is_ajax():
            return "include/index_tr.html"
        else:
            return self.template_name

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data()
        if self.request.user.is_authenticated:
            products = Product.objects.all().annotate(order_count=Count('orderitems')).order_by('-order_count')[:3]
            total_revenue = 0
            total_orders = Order.objects.filter(user=self.request.user).count()
            for product in products:
                orders = OrderItems.objects.filter(original_product=product)
                order_count = orders.count()
                try:
                    revenue = sum([order.quantity * order.original_product.price for order in orders])
                except Exception:
                    revenue = 0
                product.revenue = revenue
                try:
                    product.perc = round(order_count / total_orders * 100, 2)
                except ZeroDivisionError:
                    product.perc = 0
                total_revenue += revenue
            context["products"] = products
            context["total_revenue"] = total_revenue

            markets = Marketplace.objects.all()
            for marketplace in markets:
                users = marketplace.user_set.all()
                marketplace.perc = 0
                for user in users:
                    marketplace.perc += round(user.order_set.count() * 100 / Order.objects.all().count())

            context.update({
                "markets": markets[:3],
                "count": markets.count()
            })

        return context

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')

        else:
            messages.add_message(request,
                                 messages.INFO,
                                 "email or password doesn't exist.")
            return redirect("login")


# def index_view(request):
#     try:
#         data = reverse('dashboard')
#         return render(request, "index.html", {
#             'data': data,
#         })
#     except Exception as e:
#         print(e)
#         return render(request, "index.html")


class LoginPage(LoginView):
    template_name = 'signin.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("index")
        else:
            return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('orders:order_list')

        else:
            messages.add_message(request,
                                 messages.INFO,
                                 "email or password doesn't exist.")
            return redirect("login")


def logout_view(request):
    logout(request)
    return redirect("index")


@login_required()
def generate_xml(request):
    from datetime import datetime
    time_now = datetime.now()
    db = mongo_db()
    id_code = db.product_logs.insert_one(
        {"user": request.user.email if request.user.email else "",
         "status": "Processing",
         "created_at": time_now,
         })

    jms_import_products_api.delay(str(id_code.inserted_id))

    return render(request, "product/xmlfeed.xml",
                  {"data": Product.objects.all()}, content_type='text/xml')


class TrackList(FormView):
    form_class = ShipmentForm
    template_name = "track/track.html"

    def get_context_data(self, **kwargs):
        context = super(TrackList, self).get_context_data()

        return context

    def get_success_url(self):
        return reverse("track_detail", kwargs={"slug": self.request.POST['tracking_code']})


class TrackDetail(DetailView):
    model = Shipment
    slug_field = "tracking_code"
    template_name = "track/track_detail.html"

    def get_context_data(self, **kwargs):
        context = super(TrackDetail, self).get_context_data()
        shipment = context.get("shipment")
        tracking = TrackingActivities.objects.filter(order=shipment.order)

        context.update({
            "tracking": tracking
        })

        return context

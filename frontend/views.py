from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render
# Create your views here.
from django.urls import reverse_lazy
from django.views import View

from orders.models import Carrier
from utils.breadcrumb import BreadCrumbMixin


class index(BreadCrumbMixin,
            LoginRequiredMixin,
            PermissionRequiredMixin,
            View):
    success_url = reverse_lazy("accounts:group_list")
    permission_required = ('auth.add_group',)

    def get(self, *args, **kwargs):
        context = {"carrier": Carrier.objects.all()}
        return render(self.request, 'frontend/index.html', context)

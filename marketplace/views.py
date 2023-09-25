from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView

from marketplace.models import Marketplace

from utils.breadcrumb import BreadCrumbMixin


# Create your views here.
class MarketCreate(BreadCrumbMixin,
                   LoginRequiredMixin,
                   PermissionRequiredMixin,
                   CreateView):
    model = Marketplace

    fields = "__all__"
    success_url = reverse_lazy("marketplace:market_list")
    permission_required = ('orders.add_marketplace',)
    template_name = 'market/marketplace_form.html'

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        messages.add_message(self.request,
                             messages.INFO,
                             'Marketplace Successfully added.')
        return super().form_valid(form)


class MarketList(BreadCrumbMixin, PermissionRequiredMixin, ListView):
    model = Marketplace

    login_url = reverse_lazy('login')
    template_name = "market/list.html"
    context_object_name = 'marketplace'
    paginate_by = 10
    permission_required = ('orders.view_marketplace',)
    redirect_field_name = reverse_lazy('index')

    def get_template_names(self):
        if self.request.is_ajax():
            return "include/market_tr.html"
        else:
            return self.template_name

    def get_queryset(self):
        from django.db.models import Q
        search = self.request.GET.get("search", '')
        queryset = Marketplace\
            .objects.filter(
            Q(name__icontains=search)
            | Q(phone__icontains=search)

        ).distinct()
        return queryset


class MarketChange(BreadCrumbMixin,
                   LoginRequiredMixin,
                   PermissionRequiredMixin,
                   UpdateView):
    model = Marketplace

    fields = "__all__"
    success_url = reverse_lazy("marketplace:market_list")
    permission_required = ('orders.change_marketplace',)
    template_name = 'market/form_update.html'

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)  # Get the form as usual

        return form

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        messages.add_message(self.request,
                             messages.INFO,
                             'Address Successfully updated.')
        return super().form_valid(form)


class MarketDeleteView(PermissionRequiredMixin, DeleteView):
    # specify the model you want to use
    model = Marketplace
    permission_required = "orders.delete_marketplace"
    # can specify success url
    #  to redirect after successfully
    # deleting object
    success_url = reverse_lazy('marketplace:market_list')

    def get_success_url(self):
        messages.success(self.request, "Marketplace successfully Deleted.")
        return super().get_success_url()

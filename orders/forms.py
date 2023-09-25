from django.contrib.auth import get_user
from django.forms import ModelForm, inlineformset_factory, Form, Select, BaseInlineFormSet

from products.models import Product
from .models import Order, OrderItems, OrderImports, OrderExportFilters, FPCarrier, DroppexCarrier
from django import forms


class OrderImportsForm(ModelForm):
    class Meta:
        model = OrderImports
        fields = ["file"]


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = "__all__"
        exclude = ("origin",)


class FPCarrierForm(ModelForm):
    class Meta:
        model = FPCarrier
        fields = "__all__"


class DroppexCarrierForm(ModelForm):
    class Meta:
        model = DroppexCarrier
        fields = "__all__"



class OrderItemsForm(ModelForm):
    class Meta:
        model = OrderItems
        fields = ["original_product", "quantity"]


class CustomOrderItemsFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # get the user from kwargs
        super().__init__(*args, **kwargs)
        if user is not None:
            self.user = user
            if "admin" not in [obj.name for obj in user.groups.all()] or not user.is_superuser:
                for form in self.forms:
                    if user.marketplace_id:
                        form.fields['original_product'].queryset = form.fields['original_product'].queryset.filter(
                            marketplace_id=user.marketplace_id
                        )

    def add_fields(self, form, index):
        super().add_fields(form, index)
        if not form.instance.pk:
            if self.user:
                if self.user.marketplace_id:
                    form.fields['original_product'].queryset = Product.objects.filter(
                        marketplace_id=self.user.marketplace_id
                    )


OrderItemsFormset = inlineformset_factory(Order,
                                          OrderItems,
                                          form=OrderItemsForm,
                                          extra=1,
                                          formset=CustomOrderItemsFormSet,
                                          can_delete=True)
OrderItemsFormset1 = inlineformset_factory(Order,
                                           OrderItems,
                                           form=OrderItemsForm,
                                           extra=0,
                                           formset=CustomOrderItemsFormSet,
                                           can_delete=True)


class DateInput(forms.DateInput):
    input_type = 'date'


class ExportFileForm(forms.ModelForm):
    class Meta:
        model = OrderExportFilters
        fields = '__all__'
        widgets = {
            'creation_date_start': DateInput(),
            'creation_date_finish': DateInput()
        }

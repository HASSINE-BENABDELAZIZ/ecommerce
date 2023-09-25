from django import forms
from django.forms import ModelForm, Form

from orders.models import OrderItems
from .models import Product, Category, SubCategory


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subcategory'].queryset = SubCategory.objects.none()


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = "__all__"


class SubCategoryForm(ModelForm):
    class Meta:
        model = SubCategory
        fields = "__all__"

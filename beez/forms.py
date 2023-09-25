from django.forms import ModelForm

from .models import BeezCarrier


class BeezCarrierForm(ModelForm):
    class Meta:
        model = BeezCarrier
        fields = "__all__"

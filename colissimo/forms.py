from django.forms import ModelForm

from .models import ColissimoCarrier


class ColissimoCarrierForm(ModelForm):
    class Meta:
        model = ColissimoCarrier
        fields = "__all__"

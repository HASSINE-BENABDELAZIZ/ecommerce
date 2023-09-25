from django import forms

from orders.models import Shipment


class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = ["tracking_code"]

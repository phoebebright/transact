#python

#libs
from django import forms

#local
from web.models import QUALITIES, ProductType


class BasicRequestForm(forms.Form):
    call = forms.CharField(widget=forms.HiddenInput())
    token = forms.CharField(widget=forms.HiddenInput())
    test_mode = forms.CharField(widget=forms.HiddenInput())


class PriceCheck(BasicRequestForm):
    quantity = forms.DecimalField(max_value=1000, min_value=0.2)
    type = forms.ModelChoiceField(queryset=ProductType.objects.all())
    quality = forms.ChoiceField(choices=QUALITIES)
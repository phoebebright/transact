#python

#libs
from django import forms

#local
from web.models import QUALITIES, ProductType, CURRENCIES


FORM_QUALITIES = [("", "---------")]
FORM_QUALITIES.extend(QUALITIES)

class BasicRequestForm(forms.Form):
    call = forms.CharField(widget=forms.HiddenInput())
    token = forms.CharField(widget=forms.HiddenInput())
    test_mode = forms.CharField(widget=forms.HiddenInput())


class PriceCheck(BasicRequestForm):
    quantity = forms.DecimalField(max_value=1000, min_value=0.2)
    type = forms.ModelChoiceField(queryset=ProductType.objects.all(), required=False)
    quality = forms.ChoiceField(choices=FORM_QUALITIES, required=False)


class TransAct(PriceCheck):
    currency = forms.ChoiceField(choices=CURRENCIES)
    

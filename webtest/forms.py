#python

#libs
from django import forms

#local
from web.models import Pool, CURRENCIES



class BasicRequestForm(forms.Form):
    call = forms.CharField(widget=forms.HiddenInput())
    token = forms.CharField(widget=forms.HiddenInput())
    test_mode = forms.CharField(widget=forms.HiddenInput())


class PriceCheck(BasicRequestForm):
    quantity = forms.DecimalField(max_value=1000, min_value=0.2)
    #quality = forms.ChoiceField(choices = Pool.LISTQUALITIES('Any'), initial='', required=False)
    #type = forms.ChoiceField(choices=Pool.LISTTYPES('Any'), initial='', required=False)
    quality = forms.ChoiceField(initial='', required=False)
    type = forms.ChoiceField(initial='', required=False)

class TransAct(PriceCheck):
    currency = forms.ChoiceField(choices=CURRENCIES)
    

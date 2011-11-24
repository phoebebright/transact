from web.models import Transaction, ProductType, Pool

from django.forms import ModelForm
from django import forms
from django.utils.translation import ugettext_lazy as _

import config
from livesettings import config_value




class TransactForm(forms.Form):
    # list of qualities from models
    

    qty = forms.DecimalField(max_value=config_value('web','MAX_QUANTITY'), min_value=config_value('web','MIN_QUANTITY'), decimal_places=3)
    quality = forms.ChoiceField(choices = Pool.LISTQUALITIES('Any'), initial='', required=False)
    type = forms.ChoiceField(choices=Pool.LISTTYPES('Any'), initial='', required=False)
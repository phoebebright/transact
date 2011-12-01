#django

from django.template import Library
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.cache import cache
from livesettings import config_value
import uuid
from web.models import Transaction, Client

register = Library()

@register.simple_tag
def token():
    """
    return login token
    """
    
    user = authenticate(username=settings.DEMO_USERNAME, password=settings.DEMO_PASSWORD)
    if user and user.is_active:
        token = uuid.uuid4().hex
        expires = int(config_value('api','TOKEN_EXPIRY'))
        cache.set(token, user.username, expires)
        return token
        

    
    

@register.simple_tag
def transid():
    """
    return login token
    """
    
    testclient = Client.objects.get(name='test')
    trans = Transaction.new(testclient, 1)
    return trans.uuid


    

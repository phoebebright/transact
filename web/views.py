#app
from web.forms import TransactForm
from web.models import Pool, Transaction, Client

#django
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required, user_passes_test


#python


@login_required
def client_portal(request):

    profile = request.user.profile
    
    client = profile.client

    
    transactions = Transaction.objects.filter(client=client)
    

    return render_to_response('client_portal.html',{
        'client': client,
        'transactions': transactions,
       },context_instance=RequestContext(request))         
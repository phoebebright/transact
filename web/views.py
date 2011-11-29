#app
from web.forms import TransactForm
from web.models import Pool, Transaction, Client

#django
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required, user_passes_test


#python






def transaction(request):

    item = None
    if request.user.is_authenticated():
        profile = request.user.get_profile()
        client = profile.client
    else:
        client, created = Client.objects.get_or_create(name='test')
    
    if request.method == "POST":
        form = TransactForm(data = request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            item = Transaction.new(client, cd['qty'], type=cd['type'], quality=cd['quality'])
            form = TransactForm()
            
            
            
            
    else:
        form = TransactForm()
        
    pool = Pool.objects.all().order_by('-added')
    transactions = Transaction.objects.all().order_by('-id')[:10]
    
    return render_to_response('transaction.html',{
        'form': form,
        'item': item,
        'pool': pool,
        'transactions': transactions,
       },context_instance=RequestContext(request))        
 
@login_required
def client_portal(request):

    profile = request.user.get_profile()
    
    client = profile.client

    
    transactions = Transaction.objects.filter(client=client)
    

    return render_to_response('client_portal.html',{
        'client': client,
        'transactions': transactions,
       },context_instance=RequestContext(request))         
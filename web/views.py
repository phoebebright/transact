from django.shortcuts import render_to_response

from web.forms import TransactForm
from django.template.context import RequestContext

from web.models import Pool, Transaction, Client


def transaction(request):

    item = None
    
    client = Client.objects.get_or_create(name='test')
    
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
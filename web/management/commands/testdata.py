"""
Create some test data
"""


#python
from datetime import date, datetime, timedelta

#django
from django.core.management.base import NoArgsCommand, CommandError


#app

from web.models import *


TODAY = date.today()
YESTERDAY = date.today() - timedelta(days = 1)
TOMORROW = date.today() + timedelta(days = 1)
LASTWEEK = date.today() - timedelta(days = 7)
NEXTWEEK = date.today() + timedelta(days = 7)
NOW = datetime.now() + timedelta(minutes=1)
TODAY_STARTS = NOW.replace(hour=0,minute=0,second=0)
TODAY_ENDS = NOW.replace(hour=23,minute=59,second=59)


class Command(NoArgsCommand):
    """Add test data
    """
    
    def handle_noargs(self, **options):
         
         
        # Client A
        
        try:
            clienta =Client.objects.create(name='Client A')
        except:
            assert False, "Need to clear out all web data "

        clienta.recharge(100)
        
        try:
            user = User.objects.get(username='test')
            user.delete()
            user = User.objects.get(username='testb')
            user.delete()
        except:
            pass

        user1= User.objects.create_user('test','test@transactcarbon.com','silicon')
        profile = user1.get_profile()
        profile.client = clienta
        profile.save()

        clientb =Client.objects.create(name='Client B')        
        userb= User.objects.create_user('testb','testb@transactcarbon.com','silicon')
        profile = userb.get_profile()
        profile.client = clientb
        profile.save()

        clientb.recharge(100)
                
        """
        Should already be added as fixtures
        #  add product types
        ProductType.objects.create(code='WIND', name='Wind')
        ProductType.objects.create(code='HYDR', name='Hydro')
        ProductType.objects.create(code='BIOM', name='Biomass')
        """
        
        # add products to the pool
        
        
        trade = Trade.objects.create(name = 'Water Waves', 
            purchfrom = 'EXCH',
            total = '10000.00',
            currency = 'EUR',
            tonnes = '2500',
            ref='test 1',
            )        
        product = Product.objects.get(trade=trade)
        product.quality = 'G'
        product.type=ProductType.objects.get(code='HYDR')
        product.save()
        product.move2pool()      
        
        # add products to the pool
        trade = Trade.objects.create(name = 'Micro-Hydro', 
            purchfrom = 'EXCH',
            total = '1532.22',
            currency = 'EUR',
            tonnes = '3221',
            ref='test 2',
            )        
        product = Product.objects.get(trade=trade)
        product.quality = 'P'
        product.type=ProductType.objects.get(code='HYDR')
        product.save()
        product.move2pool()          
        
        # add products to the pool
        trade = Trade.objects.create(name = 'Windy Ridge', 
            purchfrom = 'MEX',
            total = '800',
            currency = 'EUR',
            tonnes = '200',
            ref='test 3',
            )        
        product = Product.objects.get(trade=trade)
        product.quality = 'P'
        product.type=ProductType.objects.get(code='WIND')
        product.save()
        product.move2pool()          
        
        
        # CREATE SOME TRANSACTIONS
        
        trans = Transaction.new(clienta, 2.55)
        trans.pay('PAYREF 1')
        
        trans = Transaction.new(clienta, 1.2)
        trans.pay('PAYREF 2')        
        
        trans = Transaction.new(clienta, 2)
        trans.pay('PAYREF 3')        
        
        trans = Transaction.new(clientb, 5)
        trans.pay('PAYREF 1')        
        
        trans = Transaction.new(clientb, 1)
        trans.pay('PAYREF 2')                
#python
from datetime import date, datetime, timedelta

#django
from django import template
from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.core.urlresolvers import reverse
from django.db.models import get_model
from django.test import Client
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

#app

from web.models import *
from web.exceptions import *


TODAY = date.today()
YESTERDAY = date.today() - timedelta(days = 1)
TOMORROW = date.today() + timedelta(days = 1)
LASTWEEK = date.today() - timedelta(days = 7)
NEXTWEEK = date.today() + timedelta(days = 7)
NOW = datetime.now() + timedelta(minutes=1)
TODAY_STARTS = NOW.replace(hour=0,minute=0,second=0)
TODAY_ENDS = NOW.replace(hour=23,minute=59,second=59)

def list_pool():
        print "POOL"
        for p in Pool.objects.all():
            print "%30s | %s | %s | %i | %s | %.2f | %s" % (p.product, p.quality, p.type, p.quantity, p.currency, p.price, p.added)


def list_transactions():

        for t in Transaction.objects.all():
            print t.__dict__

def list_products():

        for t in Product.objects.all():
            print t.__dict__

class BaseTest(TestCase):
    """
    setup data
    """

    def setUp(self):
        """ running setup """
      
        self.client1=Client.objects.create(name='Client 1')
        self.client2=Client.objects.create(name='Client 2')

        self.custA=Customer.objects.create(name='Customer A of Client 1')
        Relationship.objects.create(client=self.client1, customer=self.custA)
        
        
        # create users
        self.system_user = User.objects.create_user('system','system@trialflight.com','pass')
        
        '''
        # client 1 has two users
        u= User.objects.create_user('uclient1a','ucient1a@trialflight.com','pass')
        profile = u.get_profile()
        profile.client = self.client1
        profile.save()
        
        u= User.objects.create_user('uclient1b','ucient1b@trialflight.com','pass')
        profile = self.u.get_profile()
        profile.client = self.client1
        profile.save()
        
        
        # client 2 has two users
        u= User.objects.create_user('uclient2a','ucient2a@trialflight.com','pass')
        profile = self.u.get_profile()
        profile.client = self.client2
        profile.save()

        '''
        
        #  add product types
        ProductType.objects.create(code='WIND', name='Wind')
        ProductType.objects.create(code='HYDR', name='Hydro')
        ProductType.objects.create(code='BIOM', name='Biomass')

class BaseTestMoreData(BaseTest):
    """
    setup data
    """

    def setUp(self):
    
        super(BaseTestMoreData, self).setUp()
        

        # add products to the pool
        trade = Trade.objects.create(name = 'Carbon Credit 1', 
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
        trade = Trade.objects.create(name = 'Carbon Credit 2', 
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
        
        
class BasicTests(TestCase):
    """
    simple tests 
    """

    def test_create_client(self):
        "create client test"
        
        client=Client.objects.create(name='Client 1')
        # has the anonymous customer for this client been added
        self.assertEqual(Customer.objects.count(), 1)

         
        cust = Customer.objects.get(id=1)
        self.assertTrue(cust.anonymous)
        self.assertEqual(cust.clients.all().count(), 1)
        cust1 = Customer.objects.get(id=1)
        self.assertEqual(client.customers.all()[0], cust1)
        

        rel = Relationship.objects.get(id=1)
        self.assertEqual(rel.client, client)        
        self.assertEqual(rel.customer, cust) 
        


    def test_create_customer(self):
        "create stand-alone customer test"

        # can create a customer that is not linked to a client
        cust = Customer.objects.create(name="customer 1")      
        self.assertEqual(Relationship.objects.count(), 0)

        
        # add a customer to a client entity
        client=Client.objects.create(name='Client A')
        custA = Customer.objects.create(name="customer A")      
        Relationship.objects.create(client=client, customer=custA)

        # this client now have two customers, three customers in total
            
        self.assertEqual(Customer.objects.count(), 3)
        client1 = Client.objects.get(id=1)
        self.assertEqual(client1.customers.all().count(), 2)
        
class UpstreamTests(BaseTest):
    """
    check upstream tasks - purchase credits, create products, add to pool
    """
        
    def test_trade2pool(self):
       
        # trade creates a new product
        trade = Trade.objects.create(name = 'Carbon Credit 1', 
            purchfrom = 'EXCH',
            total = '10000.00',
            currency = 'EUR',
            tonnes = '2500',
            ref='test 1',
            )
            
        # check product created
        
        product = Product.objects.get(trade=trade)
        product.quality = 'G'
        product.type=ProductType.objects.get(code='HYDR')
        product.save()
       
        p=Product.objects.get(id=1)

        self.assertEqual(p.quantity_purchased, Decimal('2500'))
        self.assertEqual(p.price, Decimal('4.40'))
        
        # now put in pool and check correctly created
        p.move2pool()
        
        pool = Pool.objects.get(id=1)
        self.assertEqual(pool.product,p)
        self.assertEqual(pool.quantity,p.quantity2pool)
        self.assertEqual(pool.quality,p.quality)
        self.assertEqual(pool.type,p.type)
        self.assertEqual(pool.price,p.price)
        
class DownstreamTests(BaseTestMoreData):
    """
    check downstream tasks - price check, transaction, payment
    """
                
        
    def test_pricecheck(self):

        # add products to the pool
        trade = Trade.objects.create(name = 'Wind P', 
            purchfrom = 'EXCH',
            total = '100.00',
            currency = 'EUR',
            tonnes = '25',
            ref='windp',
            )        
        product = Product.objects.get(trade=trade)
        product.quality = 'P'
        product.type=ProductType.objects.get(code='WIND')
        product.save()
        product.move2pool()  
        poolitem = Pool.objects.get(product=product)
    

        # add products to the pool
        trade = Trade.objects.create(name = 'Yesterday', 
            purchfrom = 'EXCH',
            total = '10000.00',
            currency = 'EUR',
            tonnes = '101',
            ref='yesterday',
            )        
        product = Product.objects.get(trade=trade)
        product.quality = 'G'
        product.type=ProductType.objects.get(code='HYDR')
        product.save()
        product.move2pool()  
        poolitem = Pool.objects.get(product=product)
        poolitem.added=YESTERDAY
        poolitem.save()


        # check earliest is being picked 
        earliestpoolitem = Pool.objects.get(product__name ='Yesterday')
        item = Pool.price_check(10.1)
        self.assertEqual(item, earliestpoolitem)
        
        
        # but if quality is specified, now choose a that one
        platinumpoolitem = Pool.objects.get(quality='P', type__code='HYDR')
        item = Pool.price_check(10, quality='P')
        self.assertEqual(item, platinumpoolitem)
        
        # look for items that have no match in the pool
        
        #quantity too high
        self.assertRaises(AboveMaxQuantity,  Pool.price_check, 10000)

        #quantity too low
        self.assertRaises(BelowMinQuantity,  Pool.price_check, 0.1)

        #no quality of type S
        self.assertRaises(NoMatchInPoolException,  Pool.price_check, 10, quality='S')

        #no type 'XXX'
        self.assertRaises(NoMatchInPoolException,  Pool.price_check, 10, type='XXX')
        
        #no quality G, type 'XXX'
        self.assertRaises(NoMatchInPoolException,  Pool.price_check, 10, quality='G', type='XXX')
        
        
        #test for matches
        #quantity = available
        item = Pool.price_check(101)
        self.assertEqual(item, earliestpoolitem)
        item = Pool.price_check(101, quality='G')
        self.assertEqual(item, earliestpoolitem)
        item = Pool.price_check(101, type='HYDR' )
        self.assertEqual(item, earliestpoolitem)
        item = Pool.price_check(101, type='HYDR' , quality='G')
        self.assertEqual(item, earliestpoolitem)


    def test_transaction(self):

        # price check
        item = Pool.price_check(10.55)
        
        trans = Transaction.new(self.client1, 10.55)
        
        self.assertEqual(item.product, trans.product)
        self.assertTrue(trans.is_open)
        self.assertFalse(trans.is_closed)
        self.assertEqual(trans.quantity, Decimal('10.55'))
        
        # now pay this Transaction
        p = trans.pay('PAYREF')
        
        self.assertTrue(p.ref, 'PAYREF')
        
        self.assertEqual(trans.status, 'P')
        self.assertFalse(trans.is_open)
        self.assertTrue(trans.is_closed)

        #DO NEXT
        #cancel, expire, refund, pay
        
class ListTests(BaseTestMoreData):
    """
    check some basic API calls to the model
    """
                
        
    def test_listtype(self):
    
        types = ProductType.LISTTYPES()
        self.assertEqual(types.count(),3)
        
        ProductType.objects.create(code='TST', name='Tests')
        types = ProductType.LISTTYPES()
        self.assertEqual(types.count(),4)
        
        
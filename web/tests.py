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
            print "%30s | %s | %s | %.2f | %s | %.2f | %s" % (p.product, p.quality, p.type, p.quantity, p.currency, p.price, p.added)


def list_transactions():
        print "TRANSACTIONS"
        for p in Transaction.objects.all():
            print "%s |%30s | %s | %s | %.2f | %s | %.2f | %s" % (p.status, p.product, p.pool, p.fee, p.quantity, p.currency, p.price, p.expire_at)

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
        p=ProductType.objects.create(code='WIND', name='Wind')
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
        
        # add products to the pool
        trade = Trade.objects.create(name = 'Carbon Credit 3', 
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
        item = Pool.PRICECHECK(10.1)
        self.assertEqual(item, earliestpoolitem)
        
        
        # but if quality is specified, now choose a that one
        platinumpoolitem = Pool.objects.get(quality='P', type__code='HYDR')
        item = Pool.PRICECHECK(10, quality='P')
        self.assertEqual(item, platinumpoolitem)
        
        # look for items that have no match in the pool
        
        #quantity too high
        self.assertRaises(AboveMaxQuantity,  Pool.PRICECHECK, 10000)

        #quantity too low
        self.assertRaises(BelowMinQuantity,  Pool.PRICECHECK, 0.1)

        #no quality of type S
        self.assertRaises(NoMatchInPoolException,  Pool.PRICECHECK, 10, quality='S')

        #no type 'XXX'
        self.assertRaises(InvalidProductType,  Pool.PRICECHECK, 10, type='XXX')
        
        #no quality G, type 'XXX'
        self.assertRaises(NoMatchInPoolException,  Pool.PRICECHECK, 10, quality='G', type='BIOM')
        
        
        #test for matches
        #quantity = available
        item = Pool.PRICECHECK(101)
        self.assertEqual(item, earliestpoolitem)
        item = Pool.PRICECHECK(101, quality='G')
        self.assertEqual(item, earliestpoolitem)
        item = Pool.PRICECHECK(101, type='HYDR' )
        self.assertEqual(item, earliestpoolitem)
        item = Pool.PRICECHECK(101, type='HYDR' , quality='G')
        self.assertEqual(item, earliestpoolitem)

        # set default for client 1 only
        self.client1.quality='G'  
        self.client1.type = ProductType.objects.get(code='WIND')
        self.client1.save()


        # use client defaults if quality/type not specified
        # test for defaults not being in pool
        self.assertRaises(NoMatchInPoolClientException,  Pool.PRICECHECK, 10, client=self.client1)

        # change so there is a match in the pool
        self.client1.quality='P'  
        self.client1.type = ProductType.objects.get(code='HYDR')
        self.client1.save()

        item = Pool.PRICECHECK(101, client=self.client1)
        self.assertEqual(item.product.name, 'Carbon Credit 2')

        # Any Hydro
        self.client1.quality=None  
        self.client1.save()

        item = Pool.PRICECHECK(101, client=self.client1)
        self.assertEqual(item.product.name, 'Yesterday')

        # Any Platinum - change a date to yesterday to be able to ensure this one is picked
        self.client1.quality='P'  
        self.client1.type = None
        self.client1.save()
        item = Pool.objects.get(product__name = 'Carbon Credit 3')
        item.added=YESTERDAY
        item.save()

        item = Pool.PRICECHECK(101, client=self.client1)
        self.assertEqual(item.product.name, 'Carbon Credit 3')
        
        
    def test_transaction(self):

        # get item that matches 10.55 units
        item = Pool.PRICECHECK(10.55)
        before_qty = item.quantity
        
        # create a transaction
        trans = Transaction.new(self.client1, 10.55)
        
        self.assertEqual(item.product, trans.product)
        self.assertTrue(trans.is_open)
        self.assertFalse(trans.is_closed)
        self.assertEqual(trans.quantity, Decimal('10.55'))
        
        # check this amount now removed from pool
        item = Pool.objects.get(id=item.id)
        self.assertEqual(item.quantity, before_qty - Decimal('10.55'))
        
        
        # now pay this Transaction
        p = trans.pay('PAYREF')
        
        self.assertTrue(p.ref, 'PAYREF')
        
        self.assertEqual(trans.status, 'P')
        self.assertFalse(trans.is_open)
        self.assertTrue(trans.is_closed)

        #DO NEXT
        #cancel, expire, refund, pay
        

    def test_expire_transactions(self):
    
        # create some open transactions
        t1 = Transaction.new(self.client1, 1)
        t2 = Transaction.new(self.client1, 2)
        t3 = Transaction.new(self.client2, 3)
        t4 = Transaction.new(self.client2, 4)

        c = Transaction.objects.open().count()
        
        self.assertEqual(c,4)
        
        # now expire one
        t1=Transaction.objects.get(id=t1.id)
        t1.expire_at = datetime.now() - timedelta(seconds=60)
        t1.save()        
        
        n = Transaction.expire_all()
        
        # one item expired
        self.assertEqual(Transaction.objects.open().count(),3)
        

    def test_pool(self):
        """
        misc tests on pool
        """
        
        p = Pool.objects.get(id=1)
        self.assertEqual(p.quantity, 2500)
        
        # remove 100 whole units from a pool item
        p.remove_quantity(100)
        p = Pool.objects.get(id=1)
        self.assertEqual(p.quantity, 2400)
        
        # remove decimal amount
        p.remove_quantity(0.3)
        p = Pool.objects.get(id=1)
        self.assertEqual(p.quantity, Decimal('2399.7'))

        # trying putting products in the pool without quality or type
        # add products to the pool
        trade = Trade.objects.create(name = 'Test not Quality', 
            purchfrom = 'EXCH',
            total = '10.00',
            currency = 'EUR',
            tonnes = '101',
            ref='test',
            )        
        product = Product.objects.get(trade=trade)
        self.assertRaises(ProductQualityRequired, product.move2pool  )

        product.quality = 'G'
        product.save()
        
        self.assertRaises(ProductTypeRequired, product.move2pool  )
        
        product.type=ProductType.objects.get(code='HYDR')
        product.save()
        
        product.move2pool()
        

    def test_poollevel(self):
        """
        test whether low pool level is identified
        """
        
        self.assertEqual(Pool.level(), Decimal(5921))
        self.assertEqual(Pool.level(quality='P'), Decimal(3421))
        self.assertEqual(Pool.level(quality='G'), Decimal(2500))
        self.assertEqual(Pool.level(type='HYDR'), Decimal(5721))       

        # poollevel items created automatically when products were added to pool
        self.assertEqual(PoolLevel.objects.count(),3)       
        
        # remove a small amount
        p = Pool.objects.get(id=1)
        p.remove_quantity(3)
        
        self.assertEqual(config_value('web','DEFAULT_MIN_POOL_LEVEL'),Decimal('100'))

        self.assertTrue(PoolLevel.check_level_ok(quality=p.quality, type=p.type))

        
        # remove a big amount so level below minlevel of 100
        p.remove_quantity(2400)    
        self.assertFalse(PoolLevel.check_level_ok(quality=p.quality, type=p.type))
        self.assertEqual(p.quantity, Decimal('97'))

        # create a transaction
        trans = Transaction.new(self.client1, 100, type='WIND')
        self.assertFalse(PoolLevel.check_level_ok(quality=p.quality, type=p.type))

        
class ListTests(BaseTestMoreData):
    """
    check some basic API calls to the model
    """
                
        
    def test_listtype(self):
        """
        check both LISTTYPE calls
        """
        
        # get list of all possible product types
        types = ProductType.LISTTYPES()
        self.assertEqual(types.count(),3)
        
        ProductType.objects.create(code='TST', name='Tests')
        types = ProductType.LISTTYPES()
        self.assertEqual(types.count(),4)

        # get list of all product types in the pool
        types = Pool.LISTTYPES()
        self.assertEqual(len(types),2)

        # get list of all product types in the pool with optional first blank param
        types = Pool.LISTTYPES('Any')
        self.assertEqual(len(types),3)
        self.assertEqual(types[0][0],'')
        self.assertEqual(types[0][1],'Any')

        
    def test_qualities(self):
        
        q = LISTQUALITIES()       
        self.assertEqual(len(q),4)
        
         # get list of all product qualities in the pool
        qualities = Pool.LISTQUALITIES()
        self.assertEqual(len(qualities),2)
       

        # get list of all product qualities in the pool with optional first blank param
        qualities = Pool.LISTQUALITIES('Any')
        self.assertEqual(len(qualities),3)
        self.assertEqual(qualities[0][0],'')
        self.assertEqual(qualities[0][1],'Any')

  
    def test_listproducts(self):
    
        products = Pool.LISTPRODUCTS()
        self.assertEqual(products.count(),3)
        
        # if quantity is below minimum then won't be counted
        p = Pool.objects.get(id=1)
        self.assertEqual(p.quantity, 2500)
        p.remove_quantity(2499.9)

        products = Pool.LISTPRODUCTS()
        self.assertEqual(products.count(),2)
        
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import json
from django.contrib.auth.models import User
from django.core.cache import cache

from django.test import TestCase
from web.models import *
from api.calls import base
from api.exceptions import ValidationDecimalException, DispatcherException

# used for debugging only
def list_pool():
        print "POOL"
        for p in Pool.objects.all():
            print "%30s | %s | %s | %.2f | %s | %.2f | %s" % (p.product, p.quality, p.type, p.quantity, p.currency, p.price, p.added)


def list_transactions():
        print "TRANSACTIONS ",Transaction.objects.count()
        for p in Transaction.objects.all():
            print "%s | %s |%30s | %s | %s | %s | %s | %.2f | %.2f | %s" % (p.id, p.status, p.product, p.client, p.pool, p.quantity, p.currency, p.fee, p.total, p.expire_at)

def list_payments():
        print "PAYMENTS",Payment.objects.count()
        for p in Payment.objects.all():
            if p.trans:
                tid = p.trans.id
            else:
                tid =0
            print "%s |%s | %s | %.2f |" % (tid, p.client, p.ref, p.amount)

class ApiTestCase(TestCase):

    def _api_call(self, call_data):
        json_data = json.dumps(call_data)
        response = self.client.post('/api/',json_data,content_type='application/json')
        self.assertEquals(response.status_code, 200)
        content = response.content
        try:
            json_content = json.loads(content)
            return json_content
        except ValueError:
            self.fail("no json in response\nWe got\n%s" % content)

    def setUp(self):
        self.system_user = User.objects.create_user('system', 'system@trialflight.com', 'pass')
        self.cleanup_objects = [self.system_user]

    def tearDown(self):
        for obj in self.cleanup_objects:
            obj.delete()

    def _auth(self, name="system", password="pass"):
        auth_call = {
            "call": "LOGIN",
            "username": name,
            "password": password
        }
        data = self._api_call(auth_call)
        self.token = data.get('token')
        return self.token
    
class ApiWithDataTestCase(ApiTestCase):

    def setUp(self):
        super(ApiWithDataTestCase, self).setUp()
        
        cleanup_objects = self.cleanup_objects
        self.client1 = Client.objects.create(name='Client 1')
        self.client1.recharge(1000)
        self.client2 = Client.objects.create(name='Client 2')
        cleanup_objects.append(self.client1)
        cleanup_objects.append(self.client2)
        self.custA = Customer.objects.create(name='Customer A of Client 1')
        cleanup_objects.append(self.custA)
        o=Relationship.objects.create(client=self.client1, customer=self.custA)
        cleanup_objects.append(o)
        # create users



        

        #  add product types
        o=ProductType.objects.create(code='WIND', name='Wind')
        cleanup_objects.append(o)
        o=ProductType.objects.create(code='HYDR', name='Hydro')
        cleanup_objects.append(o)
        o=ProductType.objects.create(code='BIOM', name='Biomass')
        cleanup_objects.append(o)
        # add products to the pool
        trade = Trade.objects.create(name='Carbon Credit 1',
            purchfrom='EXCH',
            total='10000.00',
            currency='EUR',
            tonnes='2500',
            ref='test 1',
            )
        product = Product.objects.get(trade=trade)
        product.quality = 'G'
        product.type = ProductType.objects.get(code='HYDR')
        product.save()
        product.move2pool()
        cleanup_objects.append(product)
        cleanup_objects.append(trade)

        # add products to the pool
        trade = Trade.objects.create(name='Carbon Credit 2',
            purchfrom='EXCH',
            total='1532.22',
            currency='EUR',
            tonnes='3221',
            ref='test 2',
            )
        product = Product.objects.get(trade=trade)
        product.quality = 'P'
        product.type = ProductType.objects.get(code='HYDR')
        product.save()
        product.move2pool()
        cleanup_objects.append(product)
        cleanup_objects.append(trade)
        product = Product.objects.get(trade=trade)
        product.quality = 'P'
        product.type = ProductType.objects.get(code='BIOM')
        product.save()
        product.move2pool()
        cleanup_objects.append(product)
        self.cleanup_objects = cleanup_objects

    def _add_users_clients(self):
# client 1 has two users
        from web.models import User
        u= User.objects.create_user('uclient1a','ucient1a@trialflight.com','pass')
        u.save()
        profile = u.profile
        profile.client = self.client1
        profile.save()
        self.cleanup_objects.append(u)
        u= User.objects.create_user('uclient1b','ucient1b@trialflight.com','pass')
        u.save()
        profile = u.profile
        profile.client = self.client1
        profile.save()
        self.cleanup_objects.append(u)
        # client 2 has two users
        u= User.objects.create_user('uclient2a','ucient2a@trialflight.com','pass')
        u.save()
        profile = u.profile
        profile.client = self.client2
        profile.save()
        self.cleanup_objects.append(u)

class UtilsTest(ApiTestCase):
    def test_ping(self):
        """Testing PING call
            // PING REQUEST
            {
            "call": "PING"
            }
            // PING RESPONSE
            {
            "call": "PING",
            "status": "OK",
            "timestamp": 1321267155000
            }
        """
        call_data = {
            "call": 'PING'
        }
        jsoncontent = self._api_call(call_data)
        self.assertEquals(jsoncontent['call'],'PING', jsoncontent)
        self.assertEquals(jsoncontent['status'],'OK')
        self.assertTrue(int(jsoncontent['timestamp']) > 0)

class AuthTest(ApiTestCase):
    def test_login(self):
        """Testing LOGIN 
            // LOGIN REQUEST
            // Username is set for each Client. Loging in allows access only to administrative
            API calls (TBD), to make transactions user needs to create auths and allow
            them access at least to TRANSACT and PAY calls.
            {
            "call": "LOGIN",
            "username": "jdoe",
            !
            "password": "pwd1234"
            }
            // LOGIN RESPONSE - SUCCESS
            {
            "call": "LOGIN",
            "status": "OK",
            "timestamp": 1321267155000,
            "token": "1db6b44cafa0494a950d9ef531c02e69",
            "expires": 1321363155
            }
            // LOGIN RESPONSE - FAILURE
            {
            "call": "LOGIN",
            "timestamp": 1321267155000,
            "status": "FAILED",
            "code": 402
            }
            //

        """
        call_data = {
            "call": 'LOGIN',
            "username": "jdoe",
            "password": "pwd1234"
        }
        #This should fail
        jsoncontent = self._api_call(call_data)
        self.assertEquals(jsoncontent['call'],'LOGIN')
        self.assertEquals(jsoncontent['status'],'FAILED')
        self.assertTrue(int(jsoncontent['timestamp']) > 0)
        self.assertEquals(jsoncontent['code'], 402)
        user=User.objects.create(username="tester")
        user.set_password("1234567890")
        user.active=True
        user.save()
        call_data = {
            "call": 'LOGIN',
            "username": "tester",
            "password": "1234567890"
        }

        #This should succeed
        jsoncontent = self._api_call(call_data)
        self.assertEquals(jsoncontent['call'],'LOGIN')
        self.assertEquals(jsoncontent['status'],'OK')
        self.assertTrue(int(jsoncontent['timestamp']) > 0)
        self.assertTrue(isinstance(jsoncontent['token'], basestring))
        value = cache.get(jsoncontent['token'])
        self.assertEquals(value,'tester')

        
class TradeTest(ApiWithDataTestCase):



    def test_listqualities(self):
        """
        // LISTQUALITIES REQUEST
        {
            "call": "LISTQUALITIES", // required
            "token": "1db6b44cafa0494a950d9ef531c02e69" // required
        }
        // LISTQUALITIES RESPONSE
        {
            "call": "LISTQUALITIES",
            "timestamp": 1321267155000,
            "status": "OK",
            "types": [
                {
                    "code": "B",
                    "name": "Bronze"
                },
                {
                    "code": "S",
                    "name": "Silver"
                },
                {
                    "code": "G",
                    "name": "Gold"
                },
                {
                    "code": "P",
                    "name": "Platinum"
                }
                
            ]
        }
    
        """
      
        call = {
            "call": "LISTQUALITIES",
            "token": self._auth()
        }
        data = self._api_call(call)
        self.assertEqual(data.get('status'), "OK")
        self.assertEqual(data.get('call'), 'LISTQUALITIES', data)


        
        
    """
    {
        "call": "PRICECHECK", // required
        "token": "1db6b44cafa0494a950d9ef531c02e69", // required
        "quantity": 100, // required
        "type": "TNWP", // optional, here Tamil Nadu Wind Project
        "quality": "BRONZE" // optional, default BRONZE
    }
    // PRICECHECK RESPONSE
    {
        "call": "PRICECHECK",
        "status": "OK",
        "timestamp": 1321267155000,
        "quantity": 100,
        "type": "TNWP",
        "quality": "BRONZE",
        "currencies":
        {
            "EUR":
            {
                "unit": 2.4567,
                "total": 245.67
            },
            "USD":
            {
                "unit": 3.37919,
                "total": 337.92
            },
            "GBP":
            {
                "unit": 2.10384,
                "total": 210.38
            }
        }
    }
    """
    def test_simple_pricecheck(self):
        token = "1db6b44cafa0494a950d9ef531c02e69"
        call = {
            "call": "PRICECHECK",
            "token": token,
            "quantity": 10.0
        }
        data = self._api_call(call)
        self.assertEqual(data.get('status'), "FAILED")
        self.assertEqual(data.get('call'), 'PRICECHECK', data)
        self.assertEqual(data.get('code'), 401, data)


        call['token'] = self._auth()
        data = self._api_call(call)
        self.assertEqual(data.get('status'), "OK", data)
        self.assertEqual(data.get('call'), 'PRICECHECK')
        self.assertEqual(data.get('quantity'), 10.0)
        self.assertEqual(data.get('type'), "HYDR")
        self.assertEqual(data.get('quality'), 'G')
        self.assertEqual(data['currencies']['EUR']['total'], 44.25)
        self.assertEqual(data['currencies']['EUR']['unit'], 4.4)

    def test_simple_qtycheck(self):
    
        # fails if token does not match currently logged in user
        token = "1db6b44cafa0494a950d9ef531c02e69"
        call = {
            "call": "QTYCHECK",
            "token": token,
            "price": 4.4,
        }
        data = self._api_call(call)
        self.assertEqual(data.get('status'), "FAILED")
        self.assertEqual(data.get('call'), 'QTYCHECK', data)
        self.assertEqual(data.get('code'), 401, data)

        call['token'] = self._auth()

        data = self._api_call(call)

        self.assertEqual(data.get('status'), "OK", data)
        self.assertEqual(data.get('call'), 'QTYCHECK')
        self.assertEqual(data.get('quantity'), 2500.0)
        self.assertEqual(data.get('type'), "HYDR")
        self.assertEqual(data.get('quality'), 'G')
        self.assertEqual(data['currencies']['EUR']['total'], 11000.25)
        self.assertEqual(data['currencies']['EUR']['unit'], 4.4)
        
        

    def test_price_check_errors(self):
        auth_call = {
            "call": "LOGIN",
            "username": "system",
            "password": "pass"
        }
        data = self._api_call(auth_call)
        token = data.get('token')
        call = {
            "call": "PRICECHECK",
            "token": token,
            "quantity": "bugger"
        }
        data = self._api_call(call)
        self.assertEqual(data.get('status'), "FAILED VALIDATION", data)
        self.assertEqual(data.get('call'), 'PRICECHECK')
        self.assertEqual(data.get('description'), "failed validation with not valid decimal format")

        call = {
            "call": "PRICECHECK",
            "token": token,
        }
        data = self._api_call(call)
        self.assertEqual(data.get('status'), "FAILED VALIDATION", data)
        self.assertEqual(data.get('call'), 'PRICECHECK')
        self.assertEqual(data.get('description'), "parameter 'quantity' is required")
        
    def test_type_check(self):
        """ api.TradeTest.test_type_check
        /////////////////////////////////////////////////////////////////////
        // LISTTYPES REQUEST
        {
        "call": "LISTTYPES", // required
        "token": "1db6b44cafa0494a950d9ef531c02e69" // required
        }
        // LISTTYPES RESPONSE
        {
        "call": "LISTTYPES",
        "timestamp": 1321267155000,
        "status": "OK",
        "types": [
        {
        "code": "BIOM",
        "name": "Biomass"
        },
        {
        "code": "HYDR",
        "name": "Hydro"
        },
        {
        "code": "WIND",
        "name": "Wind"
        }

        """

        call_data ={
            "call": "LISTTYPES",
            "token": self._auth()
            }
        data = self._api_call(call_data)
        self.assertEqual(data.get('status'), "OK", data)
        self.assertEqual(data.get('call'), 'LISTTYPES')
        self.assertEqual(type(data.get('types')), type([]), data)
        listtypes = data.get('types')
        self.assertEqual(len(listtypes), 2)
        testlist = {
                'HYDR':'Hydro',
                'BIOM':'Biomass'
            }
        for item in listtypes:
            self.assertTrue(item.get('code'))
            self.assertTrue(item.get('name'))
            code = item.get('code')
            if code in testlist.keys():
                self.assertEquals(item.get('name'), testlist[code])
                del testlist[code]
            else:
                self.fail("missing code '%s' in response [%s]" % (code, data))
        self.assertEquals(len(testlist),0)
        #adding blank
        call_data ={
            "call": "LISTTYPES",
            "blank": "my blank",
            "token": self._auth()
            }
        data = self._api_call(call_data)
        self.assertEqual(data.get('status'), "OK", data)
        self.assertEqual(data.get('call'), 'LISTTYPES')
        self.assertEqual(type(data.get('types')), type([]), data)
        listtypes = data.get('types')
        self.assertEqual(len(listtypes), 3)
        testlist = {
                '': "my blank",
                'HYDR':'Hydro',
                'BIOM':'Biomass'
            }
        for item in listtypes:
            # test blank code ''
            self.assertTrue(item.get('code') or item.get('code') == '')
            self.assertTrue(item.get('name'))
            code = item.get('code')
            if code in testlist.keys():
                self.assertEquals(item.get('name'), testlist[code])
                del testlist[code]
            else:
                self.fail("missing code '%s' in response [%s]" % (code, data))
        self.assertEquals(len(testlist),0)

    def test_list_quantities(self):
        """api.TradeTest.test_list_quantities
            /////////////////////////////////////////////////////////////////////
            // LISTQUALITIES REQUEST
            {
            "call": "LISTQUALITIES", // required
            "token": "1db6b44cafa0494a950d9ef531c02e69" // required
            }
            // LISTTYPES RESPONSE
            {
            "call": "LISTQUALITIES",
            "timestamp": 1321267155000,
            "status": "OK",
            "types": [
            {
            "code": "B",
            "name": "Bronze"
            },
            {
            "code": "S",
            "name": "Silver"
            },
            {
            "code": "G",
            "name": "Gold"
            },
            {
            "code": "P",
            "name": "Platinum"
            }
            }
        """
        #test without blank call
        call_data ={
            "call": "LISTQUALITIES",
            "token": self._auth(),
        }
        data = self._api_call(call_data)
        self.assertEqual(data.get('status'), "OK", data)
        self.assertEqual(data.get('call'), 'LISTQUALITIES')
        self.assertEqual(type(data.get('types')), type([]), data)
        listtypes = data.get('types')
        self.assertEqual(len(listtypes), 2, listtypes)
        testlist = {
                'G':'Gold',
                'P':'Platinum',
            }
        for item in listtypes:
            self.assertTrue(item.get('code'))
            self.assertTrue(item.get('name'))
            code = item.get('code')
            if code in testlist.keys():
                self.assertEquals(item.get('name'), testlist[code])
                del testlist[code]
            else:
                self.fail("missing code '%s' in response [%s]" % (code, data))
        self.assertEquals(len(testlist),0)
        #test with blank option
        call_data ={
            "call": "LISTQUALITIES",
            "blank": "Any quality",
            "token": self._auth(),
        }
        data = self._api_call(call_data)
        self.assertEqual(data.get('status'), "OK", data)
        self.assertEqual(data.get('call'), 'LISTQUALITIES')
        self.assertEqual(type(data.get('types')), type([]), data)
        listtypes = data.get('types')
        self.assertEqual(len(listtypes), 3, listtypes)
        testlist = {
                '':"Any quality",
                'G':'Gold',
                'P':'Platinum',
            }
        for item in listtypes:
            # check for any code ''
            self.assertTrue(item.get('code') or item.get('code') == '')
            self.assertTrue(item.get('name'))
            code = item.get('code')
            if code in testlist.keys():
                self.assertEquals(item.get('name'), testlist[code])
                del testlist[code]
            else:
                self.fail("missing code '%s' in response [%s]" % (code, data))
        self.assertEquals(len(testlist),0)

    def test_list_products(self):
        """api.TradeTest.test_list_products
            ///////////////////////////////////////////////////////
            // LISTPRODUCTS REQUEST
            {
            "call": "LISTPRODUCTS", // required
            "token": "1db6b44cafa0494a950d9ef531c02e69" // required
            }
            // LISTPRODUCTS RESPONSE
            {
            "call": "LISTPRODUCTS",
            "timestamp": 1321267155000,
            "status": "OK",
            "types": [
            {
            "id": 13452678321
            "type": "WIND",
            "quality": "G",
            "name": "Tamil Nadu Wind Project",
            "price": "7.75",
            "currency": "EUR"
            },
            {
            "id": 13452678322
            "type": "BIOM",
            "quality": "P",
            "name": "Nobrecel Biomass Energy Project",
            "price": "9.00",
            "currency": "EUR"
            },
            {
            "id": 13452678323
            "type": "HYDR",
            "quality": "P",
            !
            }
            }

        """
        #test without blank call
        call_data ={
            "call": "LISTPRODUCTS",
            "token": self._auth(),
        }
        data = self._api_call(call_data)
        self.assertEqual(data.get('status'), "FAILED VALIDATION", data)
        self.assertEqual(data.get('call'), 'LISTPRODUCTS')
        


    def test_transact(self):
        """api.TradeTest.test_transact
            /////////////////////////////////////////////////////////////////////
            // TRANSACT REQUEST
            // Create pending transaction request
            {
            "call": "TRANSACT", // required
            "token": "1db6b44cafa0494a950d9ef531c02e69", // required
            "quantity": 100, // required
            "type": "TNWP", // optional
            "quality": "BRONZE", // optional
            "currency": "EUR", // optional(?), default EUR?
            "customer": // optional
            { // details TBD
            "customerID": "123123" // the way Client identifies the customer -
            TransAct may link this Client+CustomerID information to its internal user
            database. customerID must be unique for that Client.
            }
            }
            // TRANSACT RESPONSE
            Updated 24 Nov 2011!
            Page 32
            {
            }
            "call": "TRANSACT",
            "status": "OK",
            "transID": "9d664a382e6f4dbd8cfd9cf2bf96040b",
            "timestamp": 1321267155000,
            "quantity": 100,
            "type": "TNWP",
            "quality": "BRONZE",
            "currency": "EUR",
            "total": 245.67,
            "customer":
            {
            "customerID": "123123"
            }
        """
#        item = Pool.PRICECHECK(10.55)
#        before_qty = item.quantity
        self._add_users_clients()
        call_data ={
            "call": "TRANSACT",
            "token": self._auth("uclient1a"),
            "quantity": 10.0,
        }
        data = self._api_call(call_data)

        self.assertEqual(data.get('status'), "OK", data)
        self.assertEqual(data.get('call'), 'TRANSACT')
        self.assertEqual(data.get('quantity'), 10.0)
        self.assertEqual(data.get('type'), 'HYDR')
        self.assertEqual(data.get('quality'), 'Gold')
        self.assertEqual(data.get('currency'), 'EUR')
        self.assertEqual(data.get('total'), 44.25)
        self.assertTrue(data.get('transID'))

        call_data ={
            "call": "TRANSACT",
            "token": self._auth("uclient1a"),
            "value": 100.0,
        }
        data = self._api_call(call_data)

        self.assertEqual(data.get('status'), "OK", data)
        self.assertEqual(data.get('call'), 'TRANSACT')
        self.assertEqual(data.get('quantity'), 22.67)
        self.assertEqual(data.get('type'), 'HYDR')
        self.assertEqual(data.get('quality'), 'Gold')
        self.assertEqual(data.get('currency'), 'EUR')
        self.assertEqual(data.get('total'), 100.0)
        self.assertTrue(data.get('transID'))

    def test_pay(self):
        """api.TradeTest.test_pay
        /////////////////////////////////////////////////////////////////////
        // PAY REQUEST
        // Note: PAY moves the status of a Transaction from PENDING to PAID
        {
        "call": "PAY",
        "transID": "9d664a382e6f4dbd8cfd9cf2bf96040b", // required
        "token": "1db6b44cafa0494a950d9ef531c02e69" // required
        }
        // PAY RESPONSE - SUCCESS
        {
        "call": "PAY",
        "status": "OK",
        "transID": "9d664a382e6f4dbd8cfd9cf2bf96040b",
        "timestamp": 1321267155000,
        "quantity": 100,
        "type": "TNWP",
        "quality": "BRONZE",
        "currency": "EUR",
        "total": 245.67,
        "customer": // optional
        {
        "customerID": "123123"
        }
        }
        // PAY RESPONSE - FAILURE
        {
        "call": "PAY",
        "status": "FAILED",
        "reason": "description here",
        "code": 100234
        }

        """
        self._add_users_clients()
        call_data ={
            "call": "TRANSACT",
            "token": self._auth("uclient1a"),
            "quantity": 10.0,
        }
        data = self._api_call(call_data)
        transId=data.get('transID')
        self.assertTrue(transId)
        ## try to pay with other user
        call_data ={
            "call": "PAY",
            "token": self._auth("uclient2a"),
            "transID": transId,
        }
        data = self._api_call(call_data)

        self.assertEqual(data.get('status'), "FAILED VALIDATION", data)
        self.assertEqual(data.get('call'), 'PAY')
        self.assertEqual(data.get('code'), 306, data)
        self.assertEqual(data.get('description'), 'Transaction Belongs to different User')

        call_data ={
            "call": "PAY",
            "token": self._auth("uclient1a"),
            "transID": transId,
        }
        

        data = self._api_call(call_data)

        self.assertEqual(data.get('status'), "OK", data)
        self.assertEqual(data.get('call'), 'PAY')
        self.assertEqual(data.get('quantity'), 10.0)
        self.assertEqual(data.get('type'), 'HYDR')
        self.assertEqual(data.get('quality'), 'Gold')
        self.assertEqual(data.get('currency'), 'EUR')
        self.assertEqual(data.get('total'), 44.25)
        data = self._api_call(call_data)
        self.assertEqual(data.get('status'), "FAILED VALIDATION", data)
        self.assertEqual(data.get('call'), 'PAY')
        self.assertEqual(data.get('code'), 303)
        self.assertEqual(data.get('description'), 'Transaction Closed')

    def test_transact_info(self):
        """api.TradeTest.test_transact_info
            /////////////////////////////////////////////////////////////////////
            // TRANSACTINFO REQUEST
            {
            "call": "TRANSACTINFO",
            "token": "1db6b44cafa0494a950d9ef531c02e69", // required
            "transID": "9d664a382e6f4dbd8cfd9cf2bf96040b" // required
            }
            // TRANSACTINFO RESPONSE
            {
            "call": "TRANSACTINFO",
            "status": "OK",
            "transID": "9d664a382e6f4dbd8cfd9cf2bf96040b",
            "state": "PENDING", // PENDING, PAID, EXPIRED, CANCELLED
            "timestamp": 1321267155000,
            "quantity": 100.000,
            "type": "TNWP",
            "quality": "BRONZE",
            "name": "Tamil Nadu Wind Project",
            "productID": "Dd664a382e6f4dbd8cfd9cf2bf96040a",
            "currency": "EUR",
            "total": 245.67,
            "authID": "51a93cda2d654ca882e0373b2c25cee3",
            "customer":
            {
            "customerID": "123123"

        """
        self._add_users_clients()
        self._auth("uclient1a")
        call_data ={
            "call": "TRANSACTINFO",
            "token": self.token,
            "transID": 123,
        }
        data = self._api_call(call_data)

        self.assertEqual(data.get('status'), "FAILED VALIDATION", data)
        self.assertEqual(data.get('call'), 'TRANSACTINFO')
        self.assertEqual(data.get('code'), 304)
        self.assertEqual(data.get('description'), 'Transaction does not exist', data)


        call_data ={
            "call": "TRANSACT",
            "token": self.token,
            "quantity": 10.0,
        }
        data = self._api_call(call_data)
        transId=data.get('transID')
        self.assertTrue(transId, data)

        ## try to pay with other user
        call_data ={
            "call": "TRANSACTINFO",
            "token": self._auth("uclient2a"),
            "transID": transId,
        }
        data = self._api_call(call_data)

        self.assertEqual(data.get('status'), "FAILED VALIDATION", data)
        self.assertEqual(data.get('call'), 'TRANSACTINFO')
        self.assertEqual(data.get('code'), 306, data)
        self.assertEqual(data.get('description'), 'Transaction Belongs to different User')

        call_data ={
            "call": "TRANSACTINFO",
            "token": self._auth("uclient1a"),
            "transID": transId,
        }
        data = self._api_call(call_data)

        self.assertEqual(data.get('status'), "OK", data)
        self.assertEqual(data.get('call'), 'TRANSACTINFO')
        self.assertEqual(data.get('quantity'), 10.0)
        self.assertEqual(data.get('type'), 'HYDR')
        self.assertEqual(data.get('quality'), 'Gold')
        self.assertEqual(data.get('currency'), 'EUR')
        self.assertEqual(data.get('total'), 44.25)
        self.assertEqual(data.get('state'), 'PENDING')
        self.assertEqual(data.get('name'), 'Carbon Credit 1')
        self.assertTrue(data.get('productID'))

        call_data ={
            "call": "PAY",
            "token": self._auth("uclient1a"),
            "transID": transId,
        }
        data = self._api_call(call_data)

        call_data ={
            "call": "TRANSACTINFO",
            "token": self.token,
            "transID": transId,
        }
        data = self._api_call(call_data)

        self.assertEqual(data.get('status'), "OK", data)
        self.assertEqual(data.get('call'), 'TRANSACTINFO')
        self.assertEqual(data.get('quantity'), 10.0)
        self.assertEqual(data.get('type'), 'HYDR')
        self.assertEqual(data.get('quality'), 'Gold')
        self.assertEqual(data.get('currency'), 'EUR')
        self.assertEqual(data.get('total'), 44.25)
        self.assertEqual(data.get('state'), 'PAID')
        self.assertEqual(data.get('name'), 'Carbon Credit 1')
        self.assertTrue(data.get('productID'))

    def test_transact_cancel(self):
        """api.TradeTest.test_transact_cancel
            /////////////////////////////////////////////////////////////////////
            // TRANSACTCANCEL REQUEST
            {
            "call": "TRANSACTCANCEL",
            "token": "1db6b44cafa0494a950d9ef531c02e69", // required
            "transID": "9d664a382e6f4dbd8cfd9cf2bf96040b" // required
            }
            // TRANSACTCANCEL RESPONSE
            {
            "call": "TRANSACTCANCEL",
            "status": "OK",
            "timestamp": 1321267155000
            }

        """
        self._add_users_clients()
        self._auth("uclient1a")
        call_data ={
            "call": "TRANSACTCANCEL",
            "token": self.token,
            "transID": 123,
        }
        data = self._api_call(call_data)

        self.assertEqual(data.get('status'), "FAILED VALIDATION", data)
        self.assertEqual(data.get('call'), 'TRANSACTCANCEL')
        self.assertEqual(data.get('code'), 304, data)
        self.assertEqual(data.get('description'), 'Transaction does not exist', data)


        call_data ={
            "call": "TRANSACT",
            "token": self.token,
            "quantity": 10.0,
        }
        data = self._api_call(call_data)
        self.assertTrue(data.get('transID'), data)
        transact_id = data.get('transID')



        call_data ={
            "call": "TRANSACTINFO",
            "token": self._auth("uclient1a"),
            "transID": transact_id,
        }
        data = self._api_call(call_data)

        self.assertEqual(data.get('status'), "OK", data)
        self.assertEqual(data.get('call'), 'TRANSACTINFO')
        self.assertEqual(data.get('quantity'), 10.0)
        self.assertEqual(data.get('type'), 'HYDR')
        self.assertEqual(data.get('quality'), 'Gold')
        self.assertEqual(data.get('currency'), 'EUR')
        self.assertEqual(data.get('total'), 44.25)
        self.assertEqual(data.get('state'), 'PENDING')
        self.assertEqual(data.get('name'), 'Carbon Credit 1')
        self.assertTrue(data.get('productID'))

        ## try to cancel with other user
        call_data ={
            "call": "TRANSACTCANCEL",
            "token": self._auth("uclient2a"),
            "transID": transact_id,
        }
        data = self._api_call(call_data)

        self.assertEqual(data.get('status'), "FAILED VALIDATION", data)
        self.assertEqual(data.get('call'), 'TRANSACTCANCEL')
        self.assertEqual(data.get('code'), 306, data)
        self.assertEqual(data.get('description'), 'Transaction Belongs to different User')

        call_data ={
            "call": "TRANSACTCANCEL",
            "token": self._auth("uclient1a"),
            "transID": transact_id,
        }
        data = self._api_call(call_data)
        self.assertEqual(data.get('status'), "OK", data)
        self.assertEqual(data.get('call'), 'TRANSACTCANCEL')

        call_data ={
            "call": "TRANSACTINFO",
            "token": self.token,
            "transID": transact_id,
        }
        data = self._api_call(call_data)

        self.assertEqual(data.get('status'), "OK", data)
        self.assertEqual(data.get('call'), 'TRANSACTINFO')
        self.assertEqual(data.get('quantity'), 10.0)
        self.assertEqual(data.get('type'), 'HYDR')
        self.assertEqual(data.get('quality'), 'Gold')
        self.assertEqual(data.get('currency'), 'EUR')
        self.assertEqual(data.get('total'), 44.25)
        self.assertEqual(data.get('state'), 'CANCELLED')
        self.assertEqual(data.get('name'), 'Carbon Credit 1')
        self.assertTrue(data.get('productID'))

        call_data ={
            "call": "TRANSACTCANCEL",
            "token": self.token,
            "transID": transact_id,
        }
        data = self._api_call(call_data)
        self.assertEqual(data.get('status'), "FAILED VALIDATION", data)
        self.assertEqual(data.get('call'), 'TRANSACTCANCEL')
        self.assertEqual(data.get('code'), 307, data)
        self.assertEqual(data.get('description'), 'Transaction status not pending')

    def test_client_balance_and_recharge(self):
        """api.TradeTest.test_transact_cancel
            /////////////////////////////////////////////////////////////////////
            // BALANCE REQUEST
            {
            "call": "BALANCE",
            "token": "1db6b44cafa0494a950d9ef531c02e69", // required
            }
            // BALANCE RESPONSE
            {
            "call": "BALANCE",
            "status": "OK",
            "timestamp": 1321267155000,
            "balance": 102.90
            }

        """
        

        self._add_users_clients()
        self._auth("uclient1a")
        call_data_balance ={
            "call": "BALANCE",
            "token": self.token,
        }

        data = self._api_call(call_data_balance)

        self.assertEqual(data.get('status'), "OK", data)
        self.assertEqual(data.get('call'), 'BALANCE')
        self.assertEqual(data.get('balance'), 1000)

        # remove 100 from balance
        trans = Transaction.new(self.client1, value=100)

        # balance hasn't changed yet
        data = self._api_call(call_data_balance)
        self.assertEqual(data.get('balance'), 1000)

        # once paid, balance changes
        trans.pay('REF')

        data = self._api_call(call_data_balance)
        self.assertEqual(data.get('balance'), 900)

        client = Client.objects.get(id=self.client1.id)
        self.assertEqual(client.balance, Decimal(str('900')))
        
        # recharge account by 50
  
        call_data ={
            "call": "RECHARGE",
            "token": self.token,
            "amount": 50,
        }

        data = self._api_call(call_data)
        self.assertEqual(data.get('status'), "OK", data)
        self.assertEqual(data.get('call'), 'RECHARGE')
        self.assertEqual(data.get('amount'), 50)


        client1again = Client.objects.get(id=self.client1.id)
        data = self._api_call(call_data_balance)
        self.assertEqual(data.get('balance'), 950)
        self.assertEqual(client1again.balance, 950)

        
        # Check decimals working
        
        trans2 = Transaction.new(self.client1, value=0.31)        
        trans2.pay('REF')
        
        data1 = self._api_call(call_data_balance)
        self.assertEqual(data1.get('balance'), 949.69)
        
        
class UnitTests(TestCase):

    def setUp(self):
        self.system_user = User.objects.create_user('system', 'system@trialflight.com', 'pass')
        auth_call = {
            "call": "LOGIN",
            "username": "system",
            "password": "pass"
        }
        apirequest = base.dispatch(auth_call)
        result = apirequest.run()
        result = result.data
        self.token = result.get('token')

    def test_validation(self):
        data = {
            "call": "PRICECHECK",
            "token": self.token,
            "quantity": "bugger"
        }
        self.assertRaises(ValidationDecimalException, base.dispatch, data)

    def test_unknowncall(self):
        data = {
            "call": "BENIU",
            "token": self.token,
            "quantity": "bugger"
        }
        self.assertRaises(DispatcherException, base.dispatch, data)

    def test_ping(self):
        call_data = {
            "call": 'PING'
        }
        request = base.dispatch(call_data)
        response = request.run()
        content = response.data
        self.assertEquals(content['call'],'PING')
        self.assertEquals(content['status'],'OK')
        self.assertTrue(int(content['timestamp']) > 0)
        
    def test_listtypes(self):
        call_data = {
            "call": 'LISTTYPES',
            "token": self.token,
        }
        request = base.dispatch(call_data)
        response = request.run()
        content = response.data
        self.assertEquals(content['call'],'LISTTYPES')
        self.assertEquals(content['status'],'OK')
        self.assertTrue(int(content['timestamp']) > 0)        
        
    def test_qualities(self):
        call_data = {
            "call": 'LISTQUALITIES',
            "token": self.token,
        }
        request = base.dispatch(call_data)
        response = request.run()
        content = response.data
        self.assertEquals(content['call'],'LISTQUALITIES')
        self.assertEquals(content['status'],'OK')
        self.assertTrue(int(content['timestamp']) > 0)                
    """   
    def test_pricecheck(self):

        call_data = {
            "call": 'PRICECHECK',
            "quantity": 10,
            "token": self.token
        }

        request = base.dispatch(call_data)
        response = request.run()
        content = response.data
        self.assertEquals(content['call'],'PRICECHECK')
        self.assertEquals(content['status'],'OK')
        self.assertTrue(int(content['timestamp']) > 0)           

    def test_transact(self):
        call_data ={
            "call": "TRANSACT",
            "token": self.token,
            "quantity": 10.0,
        }
        request = base.dispatch(call_data)

        self.assertRaises(NoMatchInPoolException, request.run)

    def test_pay(self):
        call_data = {
            "call": 'PAY'
        }
        request = base.dispatch(call_data)
        response = request.run()
        content = response.data
        self.assertEquals(content['call'],'PAY')
        self.assertEquals(content['status'],'OK')
        self.assertTrue(int(content['timestamp']) > 0)       
    def test_transactcancel(self):
        call_data = {
            "call": 'TRANSACTCANCEL'
        }
        request = base.dispatch(call_data)
        response = request.run()
        content = response.data
        self.assertEquals(content['call'],'TRANSACTCANCEL')
        self.assertEquals(content['status'],'OK')
        self.assertTrue(int(content['timestamp']) > 0)       
        

    def test_transactinfo(self):
        call_data = {
            "call": 'TRANSACTINFO'
        }
        request = base.dispatch(call_data)
        response = request.run()
        content = response.data
        self.assertEquals(content['call'],'TRANSACTINFO')
        self.assertEquals(content['status'],'OK')
        self.assertTrue(int(content['timestamp']) > 0)       
        
    def test_listproducts(self):
        call_data = {
            "call": 'LISTPRODUCTS'
        }
        request = base.dispatch(call_data)
        response = request.run()
        content = response.data
        self.assertEquals(content['call'],'LISTPRODUCTS')
        self.assertEquals(content['status'],'OK')
        self.assertTrue(int(content['timestamp']) > 0)       
        
        
                # fails with not enough funds
        
        data = self._api_call(call_data)
        self.assertEqual(data.get('status'), "FAILED", data)
        self.assertEqual(data.get('call'), 'PAY')
        self.assertEqual(data.get('code'), 112, data)
        self.assertEqual(data.get('description'), 'Not enough Funds')
        
        # 

    """        

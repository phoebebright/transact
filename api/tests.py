"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import json

from django.test import TestCase
from web.models import *

class ApiTest(TestCase):

    def _api_call(self, call_data):
        json_call = json.dumps(call_data)
        response = self.client.post('/api/',call_data,content_type='application/json')
        self.assertEquals(response.status_code, 200)
        content = response.content
        try:
            jsoncontent = json.loads(content)
            return jsoncontent
        except ValueError:
            self.fail("no json in response\nWe got\n%s" % content)

    def test_ping(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        call = {
            "call": 'PING'
        }
        jsoncontent = self._api_call('{"call":"PING"}')
        self.assertEquals(jsoncontent['call'],'PING')
        self.assertEquals(jsoncontent['status'],'OK')
        self.assertTrue(int(jsoncontent['timestamp']) > 0)


class PriceCheckTest(TestCase):
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
    def setUp(self):
        """ running setup """

        self.client1 = Client.objects.create(name='Client 1')
        self.client2 = Client.objects.create(name='Client 2')

        self.custA = Customer.objects.create(name='Customer A of Client 1')
        Relationship.objects.create(client=self.client1, customer=self.custA)

        # create users
        self.system_user = User.objects.create_user('system', 'system@trialflight.com', 'pass')

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

    def test_simple_pricecheck(self):
        token = "1db6b44cafa0494a950d9ef531c02e69"
        call = {
            "call": "PRICECHECK",
            "token": token,
            "quantity": 10.0
        }
        response = self.client.post('/api/', json.dumps(call), content_type='application/json')
        self.assertEquals(response.status_code, 200)
        content = response.content
        try:
            data = json.loads(content)
        except ValueError:
            self.fail("no json in response\nWe got\n%s" % content)
        self.assertEqual(data.get('status'), "OK")
        self.assertEqual(data.get('call'), 'PRICECHECK')
        self.assertEqual(data.get('quantity'), 10.0)
        self.assertEqual(data.get('type'), "HYDR")
        self.assertEqual(data.get('quality'), 'G')
        self.assertEqual(data['currencies']['EUR']['total'], 44.25)
        self.assertEqual(data['currencies']['EUR']['unit'], 4.4)

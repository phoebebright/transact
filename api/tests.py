"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import json
from django.contrib.auth.models import User
from django.core.cache import cache

from django.test import TestCase


class ApiTest(TestCase):

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
        self.assertEquals(jsoncontent['call'],'PING')
        self.assertEquals(jsoncontent['status'],'OK')
        self.assertTrue(int(jsoncontent['timestamp']) > 0)

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
        #This should fail
        jsoncontent = self._api_call(call_data)
        self.assertEquals(jsoncontent['call'],'LOGIN')
        self.assertEquals(jsoncontent['status'],'OK')
        self.assertTrue(int(jsoncontent['timestamp']) > 0)
        self.assertTrue(isinstance(jsoncontent['token'], basestring))
        value = cache.get(jsoncontent['token'])
        self.assertEquals(value,'tester')

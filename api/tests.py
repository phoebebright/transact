"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import json

from django.test import TestCase


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

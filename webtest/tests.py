"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase


class WebTestTest(TestCase):
    def test_template_display(self):
        """
        make sure template works
        """
        response = self.client.get('/webtest/')
        self.assertEqual(response.status_code, 200)

from django.test import TestCase
from django.core.exceptions import ValidationError
from core.tests import helpers
from core.models import *
from core.serializers import *
from core import views
from rest_framework.test import APIClient
from unittest.mock import patch
from decimal import Decimal
from datetime import timedelta


class ShowRequestTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = helpers.build_user()
        self.venue_manager, self.venue = helpers.build_venue()
        self.owner_act = helpers.build_band(band_member=self.user)
        self.other_act = helpers.build_band()
        self.date = datetime.now() + timedelta(days=1)

    def test_request_show_as_new_user(self): 
        self.client.force_authenticate(self.user)

        #Send the show request
        data = {
            'venue': None,
            'date': self.date.strftime('%Y-%m-%dT%I:%M:%S'),
            'performers': [{
                'name': 'My first act on RedPine!',
                'is_redpine': False,
                'is_headliner': True
             }],
            'extra_slots': '0',
            'payout_type': 1,
            'ticket_price': '10.00',
            'doors_price': '15.00',
            'extra_info': '',
            'is_crowdfunded': False,
            'is_open': True,
            'is_opening': False
        }
        res = self.client.post('/v1/show-requests/', data=data, format='json')
        self.assertEqual(res.status_code, 200)

        #Confirm that the act was created successfully
        res = self.client.get('/v1/bands/?name__icontains={}'.format('My first act on RedPine!'))
        data = res.json().get('results')
        self.assertEqual(len(data), 1)

    def test_request_show_as_existing_user(self): 
        self.client.force_authenticate(self.user)

        #Send the show request
        data = {
            'venue': None,
            'date': self.date.strftime('%Y-%m-%dT%I:%M:%S'),
            'performers': [{
                'band': self.owner_act.id,
                'name': self.owner_act.name,
                'is_redpine': self.owner_act.is_redpine,
                'is_headliner': True,
                'is_accepted': True
              },{
                'band': self.other_act.id,
                'name': self.other_act.name,
                'is_redpine': self.other_act.is_redpine,
                'is_headliner': False,
                'is_accepted': False
              }],
            'extra_slots': '0',
            'payout_type': 1,
            'ticket_price': '10.00',
            'doors_price': '15.00',
            'extra_info': '',
            'is_crowdfunded': False,
            'is_open': True,
            'is_opening': False
        }
        res = self.client.post('/v1/show-requests/', data=data, format='json')
        self.assertEqual(res.status_code, 200)

    #WIP
    def test_create_show_from_opening(self):
        """ Should be able to request crowdfunded shows """
        self.client.force_authenticate(self.user)

        #Send the show request
        data = {
            'venue': None,
            'date': self.date.strftime('%Y-%m-%dT%I:%M:%S'),
            'performers': [{
                'band': self.owner_act.id,
                'name': self.owner_act.name,
                'is_redpine': self.owner_act.is_redpine,
                'is_headliner': True,
                'is_accepted': True
              },{
                'band': self.other_act.id,
                'name': self.other_act.name,
                'is_redpine': self.other_act.is_redpine,
                'is_headliner': False,
                'is_accepted': False
              }],
            'extra_slots': '0',
            'payout_type': 1,
            'ticket_price': '10.00',
            'doors_price': '15.00',
            'extra_info': '',
            'is_crowdfunded': True,
            'is_open': True,
            'is_opening': False
        }
        res = self.client.post('/v1/show-requests/', data=data, format='json')
        self.assertEqual(res.status_code, 200)


    def test_create_anon(self):
        """ should not be able to create a request without being logged in """
        res = self.client.post('/v1/show-requests/', data={})
        self.assertEqual(res.status_code, 401)

    def test_update(self):
        """ shouldn't be able to update a non-model url """
        self.client.force_authenticate(self.user)
        res = self.client.put('/v1/show-requests/')
        self.assertEqual(res.status_code, 405)

    def test_delete(self):
        """ shouldn't be able to delete a non-model url """
        self.client.force_authenticate(self.user)
        res = self.client.delete('/v1/show-requests/')
        self.assertEqual(res.status_code, 405)

    def tearDown(self):
        helpers.clear_media()
        self.client.logout()
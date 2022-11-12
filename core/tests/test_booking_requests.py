from django.test import TestCase
from django.core.exceptions import ValidationError
from core.tests import helpers
from core.models import *
from core import views
from rest_framework.test import APIClient
from unittest.mock import patch
from decimal import Decimal
from datetime import timedelta


class BookingRequestViewSetTest(TestCase):
    def setUp(self):
        self.user = helpers.build_user()
        self.bookingRequest = helpers.build_booking_request(user=self.user)
        self.client = APIClient()

    def tearDown(self):
        helpers.clear_media()
        self.client.logout()

    def test_create_success(self):
        """ should be able to create a request if logged in """
        data = {
            'user': self.user.id,
            'venue': self.bookingRequest.venue.id
        }
        self.client.force_authenticate(self.user)
        res = self.client.post('/v1/booking-requests/', data=data)
        self.assertEqual(res.status_code, 201)

    def test_create_anon(self):
        """ should not be able to create a request without being logged in """
        res = self.client.post('/v1/booking-requests/', data={})
        self.assertEqual(res.status_code, 401)

    def test_query(self):
        """ shouldn't be able to query requests """
        res = self.client.get('/v1/booking-requests/')
        self.assertEqual(res.status_code, 401)

    def test_update(self):
        """ shouldn't be able to update requests """
        res = self.client.put('/v1/booking-requests/')
        self.assertEqual(res.status_code, 401)

    def test_delete(self):
        """ shouldn't be able to delete requests """
        res = self.client.delete('/v1/booking-requests/')
        self.assertEqual(res.status_code, 401)
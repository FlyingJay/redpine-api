from django.test import TestCase
from core.tests import helpers
from core.models import *
from core import views
from rest_framework.test import APIClient
from unittest.mock import patch
from decimal import Decimal
from datetime import datetime, timedelta
from django.forms.models import model_to_dict
import pytz

timeslots_url = '/v1/timeslots/'


class TimeslotModelTest(TestCase):
    def setUp(self):
        self.time = datetime.now()
        self.manager, self.venue = helpers.build_venue()
        self.timeslot = helpers.build_timeslot(self.venue, start_time=self.time, end_time=self.time + timedelta(hours=1))


class TimeslotViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.start_times = [
            datetime.now() + timedelta(minutes=30),
            datetime.now() + timedelta(days=1, minutes=30),
            datetime.now() + timedelta(days=2, minutes=30),
        ]
        self.end_times = [
            datetime.now() + timedelta(minutes=90),
            datetime.now() + timedelta(days=1, minutes=90),
            datetime.now() + timedelta(days=2, minutes=90),
        ]
        self.manager, self.venue = helpers.build_venue()
        self.manager2, self.venue2 = helpers.build_venue()
        self.timeslots = [
            helpers.build_timeslot(self.venue, start_time=self.start_times[0], end_time=self.end_times[0]),
            helpers.build_timeslot(self.venue, start_time=self.start_times[1], end_time=self.end_times[1]),
            helpers.build_timeslot(self.venue, start_time=self.start_times[2], end_time=self.end_times[2]),
        ]
        self.timeslots2 = [
            helpers.build_timeslot(self.venue2, start_time=self.start_times[0], end_time=self.end_times[0]),
            helpers.build_timeslot(self.venue2, start_time=self.start_times[1], end_time=self.end_times[1]),
            helpers.build_timeslot(self.venue2, start_time=self.start_times[2], end_time=self.end_times[2]),
        ]

    def tearDown(self):
        pass

    def test_query_for_venue(self):
        """ should be able to query timeslots for a venue, including time ranges """
        """ this test case was designed with loading timeslots for timeslot calendar in mind """
        res = self.client.get('/v1/timeslots/?venue={}'.format(self.venue.id))
        self.assertEqual(res.status_code, 200)
        results = res.json().get('results')
        self.assertEqual(len(results), 3)
        self.assertTrue(self.timeslots[0].id in [r.get('id') for r in results])
        self.assertTrue(self.timeslots[1].id in [r.get('id') for r in results])
        self.assertTrue(self.timeslots[2].id in [r.get('id') for r in results])

        res = self.client.get('/v1/timeslots/?venue={}&start_time__gte={}'.format(self.venue2.id, self.start_times[1]))
        self.assertEqual(res.status_code, 200)
        results = res.json().get('results')
        self.assertEqual(len(results), 2)
        self.assertTrue(self.timeslots2[1].id in [r.get('id') for r in results])
        self.assertTrue(self.timeslots2[2].id in [r.get('id') for r in results])

        res = self.client.get('/v1/timeslots/?venue={}&start_time__gt={}'.format(self.venue2.id, self.start_times[1]))
        self.assertEqual(res.status_code, 200)
        results = res.json().get('results')
        self.assertEqual(len(results), 1)
        self.assertEqual(self.timeslots2[2].id, results[0].get('id'))

        res = self.client.get('/v1/timeslots/?venue={}&start_time__lte={}'.format(self.venue2.id, self.start_times[1]))
        self.assertEqual(res.status_code, 200)
        results = res.json().get('results')
        self.assertEqual(len(results), 2)
        self.assertTrue(self.timeslots2[0].id in [r.get('id') for r in results])
        self.assertTrue(self.timeslots2[1].id in [r.get('id') for r in results])

        res = self.client.get('/v1/timeslots/?venue={}&start_time__lt={}'.format(self.venue2.id, self.start_times[1]))
        self.assertEqual(res.status_code, 200)
        results = res.json().get('results')
        self.assertEqual(len(results), 1)
        self.assertEqual(self.timeslots2[0].id, results[0].get('id'))

        res = self.client.get('/v1/timeslots/?venue={}&end_time__gte={}'.format(self.venue2.id, self.end_times[1]))
        self.assertEqual(res.status_code, 200)
        results = res.json().get('results')
        self.assertEqual(len(results), 2)
        self.assertTrue(self.timeslots2[1].id in [r.get('id') for r in results])
        self.assertTrue(self.timeslots2[2].id in [r.get('id') for r in results])

        res = self.client.get('/v1/timeslots/?venue={}&end_time__gt={}'.format(self.venue2.id, self.end_times[1]))
        self.assertEqual(res.status_code, 200)
        results = res.json().get('results')
        self.assertEqual(len(results), 1)
        self.assertEqual(self.timeslots2[2].id, results[0].get('id'))

        res = self.client.get('/v1/timeslots/?venue={}&end_time__lte={}'.format(self.venue2.id, self.end_times[1]))
        self.assertEqual(res.status_code, 200)
        results = res.json().get('results')
        self.assertEqual(len(results), 2)
        self.assertTrue(self.timeslots2[0].id in [r.get('id') for r in results])
        self.assertTrue(self.timeslots2[1].id in [r.get('id') for r in results])

        res = self.client.get('/v1/timeslots/?venue={}&end_time__lt={}'.format(self.venue2.id, self.end_times[1]))
        self.assertEqual(res.status_code, 200)
        results = res.json().get('results')
        self.assertEqual(len(results), 1)
        self.assertEqual(self.timeslots2[0].id, results[0].get('id'))

    def test_create_anon(self):
        """ should be denied timeslot creation if not logged in """
        res = self.client.post(timeslots_url, data={})
        self.assertEqual(res.status_code, 401)

    def test_create_not_manager(self):
        """ should fail if the user is not the manager """
        self.client.force_authenticate(self.manager2)
        data = {
            'venue': self.venue.id,
        }

        res = self.client.post(timeslots_url, data=data)
        self.assertEqual(res.status_code, 403)

    def test_create_no_venue_id(self):
        """ should fail if the user does not supply a venue id """
        self.client.force_authenticate(self.manager2)
        data = {}
        res = self.client.post(timeslots_url, data=data)
        self.assertEqual(res.status_code, 403)

    def test_create_success(self):
        self.client.force_authenticate(self.manager)
        self.timeslots[0].delete()
        data = {
            'venue': self.venue.id,
            'asking_price': '200.00',
            'min_headcount': 20,
            'start_time': self.start_times[0],
            'end_time': self.end_times[0]
        }

        res = self.client.post(timeslots_url, data=data)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        timeslot = Timeslot.objects.get(id=int(data.get('id')))
        self.assertEqual(timeslot.booked, False)

    def test_create_booked(self):
        """ should not be able to set timeslot as booked """
        self.client.force_authenticate(self.manager)
        self.timeslots[0].delete()

        data = {
            'venue': self.venue.id,
            'asking_price': '200.00',
            'min_headcount': 20,
            'start_time': self.start_times[0],
            'end_time': self.end_times[0],
            'booked': True
        }

        res = self.client.post(timeslots_url, data=data)
        self.assertEqual(res.status_code, 201)

        timeslot = Timeslot.objects.get(id=int(res.json().get('id')))
        self.assertEqual(timeslot.booked, False)

    def test_create_end_before_start(self):
        self.client.force_authenticate(self.manager)
        self.timeslots[0].delete()

        data = {
            'venue': self.venue.id,
            'asking_price': '200.00',
            'min_headcount': 20,
            'start_time': self.end_times[0],
            'end_time': self.start_times[0],
        }

        res = self.client.post(timeslots_url, data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json().get('detail'), Timeslot.ERRORS.END_BEFORE_START)

    def test_create_end_equals_start(self):
        self.client.force_authenticate(self.manager)
        self.timeslots[0].delete()

        data = {
            'venue': self.venue.id,
            'asking_price': '200.00',
            'min_headcount': 20,
            'start_time': self.start_times[0],
            'end_time': self.start_times[0],
        }

        res = self.client.post(timeslots_url, data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json().get('detail'), Timeslot.ERRORS.END_EQUALS_START)

    def test_delete_anon(self):
        """ anon cant delete """
        res = self.client.delete('{}{}/'.format(timeslots_url, self.timeslots[0].id))
        self.assertEqual(res.status_code, 401)

    def test_delete_not_manager(self):
        """ can't delete random timeslotz """
        self.client.force_authenticate(self.manager2)
        res = self.client.delete('{}{}/'.format(timeslots_url, self.timeslots[0].id))
        self.assertEqual(res.status_code, 403)

    def test_delete_booked(self):
        """ can't delete booked timeslots """
        self.client.force_authenticate(self.manager)
        self.timeslots[0].booked = True
        self.timeslots[0].save()
        url = '{}{}/'.format(timeslots_url, self.timeslots[0].id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json().get('detail'), Timeslot.ERRORS.BOOKED)

    def test_delete(self):
        """ delete success """
        self.client.force_authenticate(self.manager)
        url = '{}{}/'.format(timeslots_url, self.timeslots[0].id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, 204)

    def test_update_anon(self):
        """ fuk anon """
        res = self.client.put('{}{}/'.format(timeslots_url, self.timeslots[0].id), data={})
        self.assertEqual(res.status_code, 401)

    def test_update_not_manager(self):
        self.client.force_authenticate(self.manager2)
        res = self.client.put('{}{}/'.format(timeslots_url, self.timeslots[0].id), data={})
        self.assertEqual(res.status_code, 403)

    def test_update_end_before_start(self):
        self.client.force_authenticate(self.manager)

        data = {
            'id':self.timeslots[0].id,
            'venue': self.venue.id,
            'asking_price': '200.00',
            'min_headcount': 20,
            'start_time': self.end_times[0],
            'end_time': self.start_times[0],
        }

        res = self.client.put('{}{}/'.format(timeslots_url, self.timeslots[0].id), data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json().get('detail'), Timeslot.ERRORS.END_BEFORE_START)

    def test_update_end_equals_start(self):
        self.client.force_authenticate(self.manager)

        data = {
            'id':self.timeslots[0].id,
            'venue': self.venue.id,
            'asking_price': '200.00',
            'min_headcount': 20,
            'start_time': self.start_times[0],
            'end_time': self.start_times[0],
        }

        res = self.client.put('{}{}/'.format(timeslots_url, self.timeslots[0].id), data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json().get('detail'), Timeslot.ERRORS.END_EQUALS_START)

    def test_update_success(self):
        self.client.force_authenticate(self.manager)

        data = {
            'id':self.timeslots[0].id,
            'venue': self.venue.id,
            'asking_price': '201.00',
            'min_headcount': 22,
            'start_time': self.start_times[0] - timedelta(minutes=30),
            'end_time': self.end_times[0] - timedelta(minutes=30),
        }

        res = self.client.put('{}{}/'.format(timeslots_url, self.timeslots[0].id), data=data)
        self.assertEqual(res.status_code, 200)
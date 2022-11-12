from django.test import TestCase
from core.tests import helpers
from core.models import *
from core import views
from rest_framework.test import APIClient
from unittest.mock import patch
from decimal import Decimal
from google import GeocodingResult
from django.contrib.gis.geos import Point


class VenueViewSetTest(TestCase):
    def setUp(self):
        self.manager, self.venue = helpers.build_venue()
        self.manager2, self.venue2 = helpers.build_venue()
        self.client = APIClient()

    def tearDown(self):
        pass

    def test_query(self):
        """ should be able to query venues """
        res = self.client.get('/v1/venues/')
        self.assertEqual(res.status_code, 200)

        data = res.json().get('results')
        self.assertEqual(len(data), 2)

        ids = [v.get('id') for v in data]
        self.assertTrue(self.venue.id in ids)
        self.assertTrue(self.venue2.id in ids)

    def test_query_by_manager(self):
        """ should be able to query venues by manager """
        res = self.client.get('/v1/venues/?managers__id__in={}'.format(self.manager.id))
        self.assertEqual(res.status_code, 200)

        data = res.json().get('results')
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].get('id'), self.venue.id)

        res = self.client.get('/v1/venues/?managers__id__in={}'.format(self.manager2.id))
        self.assertEqual(res.status_code, 200)

        data = res.json().get('results')
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].get('id'), self.venue2.id)

    def test_query_by_title(self):
        """ should be able to query by title (for home page search) """
        third_venue = helpers.build_venue(name = 'test_venue')
        query = 'est_ven'
        res = self.client.get('/v1/venues/?title__icontains={}'.format(query))
        data = res.json().get('results')
        self.assertEqual(len(data), 1)

    def test_query_by_is_featured(self):
        """ should be able to query venues by the is featured flag, to pull them out for the home page """
        self.venue2.is_featured = True
        self.venue2.save()

        res = self.client.get('/v1/venues/?is_featured=true')
        data = res.json().get('results')
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].get('id'), self.venue2.id)

        res = self.client.get('/v1/venues/?is_featured=false')
        data = res.json().get('results')
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].get('id'), self.venue.id)

    def test_query_doesnt_return_archived(self):
        """ archived venues should not be returned in the query """
        self.venue2.archived = True
        self.venue2.save()
        res = self.client.get('/v1/venues/')
        self.assertEqual(res.status_code, 200)

        data = res.json().get('results')
        self.assertEqual(len(data), 1)

        ids = [v.get('id') for v in data]
        self.assertTrue(self.venue.id in ids)

    def test_get_404_on_archived(self):
        """ archived venues should not be accessible """
        self.venue2.archived = True
        self.venue2.save()
        res = self.client.get('/v1/venues/{}/'.format(self.venue2.id))
        self.assertEqual(res.status_code, 404)

    def test_create_anon(self):
        """ should not be able to create a venue """
        res = self.client.post('/v1/venues/', data={})
        self.assertEqual(res.status_code, 401)

    @patch('google.GoogleClient.geocode', return_value=GeocodingResult(location=Point(1, 2, srid=4326)))
    def test_create_success(self, geocode):
        """ authenticated users should be able to create a venue """
        data = {
            'title': 'Test Venue',
            'description': 'Test Description',
            'capacity': 200,
            'address': '123 test address',
            'picture': helpers.mock_image_raw,
            'postal_code': 'test'
        }
        self.client.force_authenticate(self.manager)
        res = self.client.post('/v1/venues/', data=data)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json().get('location').get('latitude'), '1.0')
        self.assertEqual(res.json().get('location').get('longitude'), '2.0')
        self.assertEqual(geocode.call_count, 1)
        venue = Venue.objects.get(pk=res.json().get('id'))
        self.assertEqual([m.id for m in venue.managers.all()], [self.manager.id])

    def test_update_anon(self):
        """ anon should not be able to update """
        res = self.client.put('/v1/venues/{}/'.format(self.venue.id), data={})
        self.assertEqual(res.status_code, 401)

    def test_update_not_manager(self):
        """ not manager should not be able to update """
        self.client.force_authenticate(self.manager2)
        res = self.client.put('/v1/venues/{}/'.format(self.venue.id), data={})
        self.assertEqual(res.status_code, 403)

    def test_update_manager(self):
        """ manager should be able to update """
        data = {
            'title': 'new title',
            'description': 'new description',
            'capacity': 54321,
            'address': '123 new street!',
            'managers': [1, 2, 3],
            'postal_code': 'test',
        }

        self.client.force_authenticate(self.manager)
        res = self.client.put('/v1/venues/{}/'.format(self.venue.id), data=data)
        self.assertEqual(res.status_code, 200)

    def test_cant_update_managers(self):
        """ shouldnt be able to change managers for now.. """
        data = {
            'title': 'new title',
            'description': 'new description',
            'capacity': 54321,
            'address': '123 new street!',
            'postal_code': '123',
            'managers': [1, 2, 3]
        }

        self.client.force_authenticate(self.manager)
        res = self.client.put('/v1/venues/{}/'.format(self.venue.id), data=data)
        self.assertEqual(res.status_code, 200)
        venue = Venue.objects.get(pk=self.venue.id)
        self.assertEqual([m.id for m in venue.managers.all()], [self.manager.id])

    def test_delete_anon(self):
        """ anon should not be able to delete """
        res = self.client.delete('/v1/venues/{}/'.format(self.venue.id))
        self.assertEqual(res.status_code, 401)

    def test_delete_not_manager(self):
        """ not manager should not be able to delete """
        self.client.force_authenticate(self.manager2)
        res = self.client.delete('/v1/venues/{}/'.format(self.venue.id))
        self.assertEqual(res.status_code, 403)

    def test_delete_manager(self):
        """ manager should be able to delete, but delete should simply archive the venue """
        self.client.force_authenticate(self.manager)
        res = self.client.delete('/v1/venues/{}/'.format(self.venue.id))
        self.assertEqual(res.status_code, 204)
        venue = Venue.all_objects.get(pk=self.venue.id)
        self.assertEqual(venue.archived, True)

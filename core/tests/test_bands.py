from django.test import TestCase
from django.core.exceptions import ValidationError
from core.tests import helpers
from core.models import *
from core import views
from rest_framework.test import APIClient
from unittest.mock import patch
from decimal import Decimal


class BandViewSetQueryTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        manager, venue = helpers.build_venue()
        self.user = helpers.build_user()
        self.bands = [
            helpers.build_band(band_member=self.user),
            helpers.build_band(band_member=self.user),
            helpers.build_band(),
            helpers.build_band(),
            helpers.build_band(),
        ]
        self.bands[4].archived = True
        self.bands[4].save()

    def tearDown(self):
        pass

    def test_query_anon(self):
        res = self.client.get('/v1/bands/')
        self.assertEqual(res.status_code, 200)

        results = res.json().get('results')
        self.assertEqual(len(results), 4)

    def test_query_logged_in(self):
        """ should receive all bands """
        self.client.force_authenticate(self.user)
        res = self.client.get('/v1/bands/')
        self.assertEqual(res.status_code, 200)

        results = res.json().get('results')
        self.assertEqual(len(results), 4)

    def test_query_by_user(self):
        """ should be able to filter by user's bands """
        res = self.client.get('/v1/bands/?owner={}'.format(self.user.id))
        self.assertEqual(res.status_code, 200)

        results = res.json().get('results')
        self.assertEqual(len(results), 2)

        ids = [r.get('id') for r in results]
        self.assertTrue(self.bands[0].id in ids)
        self.assertTrue(self.bands[1].id in ids)

    def test_query_by_is_featured(self):
        """ should be able to filter by whether the band is featured """
        self.bands[0].is_featured = True
        self.bands[0].save()

        res = self.client.get('/v1/bands/?is_featured=true')
        self.assertEqual(res.status_code, 200)

        results = res.json().get('results')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get('id'), self.bands[0].id)

        res = self.client.get('/v1/bands/?is_featured=false')
        self.assertEqual(res.status_code, 200)

        results = res.json().get('results')
        self.assertEqual(len(results), 3)
        self.assertTrue(self.bands[0].id not in [r.get('id') for r in results])

    def test_query_by_name(self):
        """ should be able to filter by icontains """
        name = self.bands[3].name
        query = name[1:len(name) - 1]
        res = self.client.get('/v1/bands/?name__icontains={}'.format(query))
        data = res.json().get('results')
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].get('id'), self.bands[3].id)


class BandViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        manager, venue = helpers.build_venue()
        self.bands = [
            helpers.build_band(),
        ]
        self.user = helpers.build_user()

    def tearDown(self):
        pass

    def test_get_anon(self):
        res = self.client.get('/v1/bands/{}/'.format(self.bands[0].id))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json().get('id'), self.bands[0].id)

    def test_get_logged_in(self):
        self.client.force_authenticate(self.user)
        res = self.client.get('/v1/bands/{}/'.format(self.bands[0].id))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json().get('id'), self.bands[0].id)

    def test_create_anon(self):
        """ anon shouldnt be able to create band """
        res = self.client.post('/v1/bands/')
        self.assertEqual(res.status_code, 401)

    def test_create(self):
        self.client.force_authenticate(self.user)
        genre = Genre.objects.create(name='Rock')
        data = {
            'name': 'test', 
            'short_bio': 'test',
            'genre': genre.id,
            'is_redpine': True
        }
        res = self.client.post('/v1/bands/', data=data)
        self.assertEqual(res.status_code, 201)

        band = Band.objects.get(id=res.json().get('id'))
        self.assertEqual(band.owner, self.user)

    def test_create_cant_set_owner(self):
        self.client.force_authenticate(self.user)
        genre = Genre.objects.create(name='Rock')
        data = {
            'name': 'test', 
            'short_bio': 'test',
            'owner': 12984712,
            'genre': genre.id,
            'is_redpine': True
        }
        res = self.client.post('/v1/bands/', data=data)
        self.assertEqual(res.status_code, 201)

        band = Band.objects.get(id=res.json().get('id'))
        self.assertEqual(band.owner, self.user)

    def test_update_anon(self):
        res = self.client.put('/v1/bands/{}/'.format(self.bands[0].id))
        self.assertEqual(res.status_code, 401)

    def test_update(self):
        user = self.bands[0].owner
        self.client.force_authenticate(user)
        data = {
            'name': 'test',
            'short_bio': 'test',
            'owner': user.id 
        }
        res = self.client.put('/v1/bands/{}/'.format(self.bands[0].id), data=data)
        self.assertEqual(res.status_code, 200)

        result = res.json()
        self.assertEqual(result.get('name'), 'test')
        self.assertEqual(result.get('short_bio'), 'test')
        self.assertEqual(result.get('owner'), user.id)

    def test_destroy_anon(self):
        """ fuk off anon """
        res = self.client.delete('/v1/bands/{}/'.format(self.bands[0].id))
        self.assertEqual(res.status_code, 401)

    def test_delete_not_owner(self):
        self.client.force_authenticate(self.user)
        data = {}
        res = self.client.delete('/v1/bands/{}/'.format(self.bands[0].id))
        self.assertEqual(res.status_code, 403)

    def test_delete(self):
        user = self.bands[0].owner
        self.client.force_authenticate(user)
        res = self.client.delete('/v1/bands/{}/'.format(self.bands[0].id))
        self.assertEqual(res.status_code, 204)

        band = Band.all_objects.get(id=self.bands[0].id)
        self.assertEqual(band.archived, True)

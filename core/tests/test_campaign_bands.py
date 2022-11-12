from django.test import TestCase
from django.core.exceptions import ValidationError
from core.tests import helpers
from core.models import *
from core import views
from rest_framework.test import APIClient
from unittest.mock import patch
from decimal import Decimal
from datetime import timedelta


class CampaignViewSetTest(TestCase):
    def setUp(self):
        manager, venue = helpers.build_venue()
        self.manager = manager
        self.band = helpers.build_band()
        self.band2 = helpers.build_band()
        self.timeslot = helpers.build_timeslot(venue)
        self.client = APIClient()
        self.campaign = helpers.build_campaign([self.band], self.timeslot, manager)
        self.photo1 = CampaignPhoto.objects.create(photo=helpers.mock_image, campaign=self.campaign)
        self.photo2 = CampaignPhoto.objects.create(photo=helpers.mock_image, campaign=self.campaign)

    def tearDown(self):
        pass

    def test_create_anon(self):
        """ fuk off anon """
        res = self.client.post('/v1/campaign-bands/')
        self.assertEqual(res.status_code, 401)

    def test_update_anon(self):
        """ fuk off anon """
        res = self.client.put('/v1/campaign-bands/')
        self.assertEqual(res.status_code, 401)

    def test_delete_anon(self):
        """ fuk off anon """
        res = self.client.delete('/v1/campaign-bands/')
        self.assertEqual(res.status_code, 401)

    def test_create_not_campaign_owner(self):
        """ should be disallowed """
        rando = helpers.build_user()
        self.client.force_authenticate(user=rando)
        data = {
            'campaign': self.campaign.id,
            'band': self.band2.id,
            'is_headliner': True
        }

        res = self.client.post('/v1/campaign-bands/', data=data)
        self.assertEqual(res.status_code, 403)

    def test_create_campaign_owner(self):
        """ should be allowed """ 
        owner = helpers.build_user()
        self.campaign.created_by = owner
        self.campaign.save()
        self.client.force_authenticate(user=owner)

        data = {
            'campaign': self.campaign.id,
            'band': self.band2.id,
            'is_headliner': False
        }
        res = self.client.post('/v1/campaign-bands/', data=data)
        self.assertEqual(res.status_code, 201)

    def test_update(self):
        """ should be allowed """ 
        owner = helpers.build_user()
        self.campaign.created_by = owner
        self.campaign.save()
        self.client.force_authenticate(user=owner)

        res = self.client.get('/v1/campaign-bands/?campaign='.format(self.campaign.id))
        bands = res.json().get('results')
        res = self.client.put('/v1/campaign-bands/{}/'.format(bands[0].get('id')), data=bands[0].update(campaign=self.campaign.id))
        self.assertEqual(res.status_code, 200)

    def test_delete(self):
        """ should be allowed """ 
        owner = helpers.build_user()
        self.campaign.created_by = owner
        self.campaign.save()
        self.client.force_authenticate(user=owner)

        res = self.client.get('/v1/campaign-bands/?campaign='.format(self.campaign.id))
        bands = res.json().get('results')

        res = self.client.delete('/v1/campaign-bands/{}/'.format(bands[0].get('id')))
        self.assertEqual(res.status_code, 204)



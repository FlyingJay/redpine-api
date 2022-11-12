from django.test import TestCase, Client
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
        self.venue = venue
        self.band = helpers.build_band(band_member=self.manager)
        self.timeslot = helpers.build_timeslot(venue)
        self.client = APIClient()
        self.campaign = helpers.build_campaign([self.band], self.timeslot, manager)
        self.purchaseItem = helpers.build_purchase_item(self.campaign)
        self.photo1 = CampaignPhoto.objects.create(photo=helpers.mock_image, campaign=self.campaign)
        self.photo2 = CampaignPhoto.objects.create(photo=helpers.mock_image, campaign=self.campaign)

    def tearDown(self):
        pass

    def test_get(self):
        res = self.client.get('/v1/campaigns/{}/'.format(self.campaign.id))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json().get('id'), self.campaign.id)

    def test_query_by_id_array(self):
        """ should return campaigns for queries like: GET /v1/campaigns/?id__in=1,2,3
        important note: query strings are limited to 2,048 characters by RFC 3986 so we may run into trouble if we try to load way too much data. """
        
        campaign_2 = helpers.build_campaign([self.band], self.timeslot, self.manager)
        res = self.client.get('/v1/campaigns/?id__in={}'.format(self.campaign.id))
        data = res.json().get('results')
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].get('id'), self.campaign.id)

        res = self.client.get('/v1/campaigns/?id__in={}'.format(campaign_2.id))
        data = res.json().get('results')
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].get('id'), campaign_2.id)

        res = self.client.get('/v1/campaigns/?id__in={},{}'.format(self.campaign.id, campaign_2.id))
        data = res.json().get('results')
        self.assertEqual(len(data), 2)

        ids = [ campaign.get('id') for campaign in data ]
        self.assertTrue(self.campaign.id in ids)
        self.assertTrue(campaign_2.id in ids)

    def test_query_by_is_featured(self):
        """ should be able to query campaigns by the is featured flag, to pull them out for the home page """
        campaign_2 = helpers.build_campaign([self.band], self.timeslot, self.manager)
        campaign_2.is_featured = True
        campaign_2.save()

        res = self.client.get('/v1/campaigns/?is_featured=true')
        data = res.json().get('results')
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].get('id'), campaign_2.id)

        res = self.client.get('/v1/campaigns/?is_featured=false')
        data = res.json().get('results')
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].get('id'), self.campaign.id)

    def test_query_by_title(self):
        """ should be able to query by title (for home page search) """
        campaign_2 = helpers.build_campaign([self.band], self.timeslot, self.manager)
        title = campaign_2.title
        query = title[1:len(title) - 1]
        res = self.client.get('/v1/campaigns/?title__icontains={}'.format(query))
        data = res.json().get('results')
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].get('id'), campaign_2.id)

    def test_query_by_band(self):
        """ shouldbe able to query by a band that is in the campaign """
        band_2 = helpers.build_band()
        campaign_2 = helpers.build_campaign([self.band], self.timeslot, self.manager)
        campaign_3 = helpers.build_campaign([band_2], self.timeslot, self.manager)
        res = self.client.get('/v1/campaigns/?bands__id__in={}'.format(band_2.id))
        data = res.json().get('results')
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].get('id'), campaign_3.id)

    def test_total_earned(self):
        """ should return the correct amount in the `total_earned` field """
        res = self.client.get('/v1/campaigns/{}/'.format(self.campaign.id))
        data = res.json()
        self.assertEqual(Decimal(data.get('total_earned')), Decimal('0'))

        transactions = [
            helpers.build_transaction([self.purchaseItem.id], [1], campaign = self.campaign),
            helpers.build_transaction([self.purchaseItem.id], [1], campaign = self.campaign),
            helpers.build_transaction([self.purchaseItem.id], [1], campaign = self.campaign)
        ]

        for transaction in transactions:
            transaction.is_processed = True
            transaction.save()
            
        cancelled = helpers.build_transaction([self.purchaseItem.id], [1], campaign = self.campaign)
        cancelled.is_cancelled = True
        cancelled.save()

        res = self.client.get('/v1/campaigns/{}/'.format(self.campaign.id))
        data = res.json()
        self.assertEqual(Decimal(data.get('total_earned')), sum([transaction.total for transaction in transactions]))

    def test_tickets_sold(self):
        """ should return the correct amount in the `tickets_sold` field """
        res = self.client.get('/v1/campaigns/{}/'.format(self.campaign.id))
        data = res.json()
        self.assertEqual(Decimal(data.get('tickets_sold')), 0)

        transactions = [
            helpers.build_transaction([self.purchaseItem.id], [1], campaign = self.campaign),
            helpers.build_transaction([self.purchaseItem.id], [1], campaign = self.campaign),
            helpers.build_transaction([self.purchaseItem.id], [1], campaign = self.campaign)
        ]

        for transaction in transactions:
            transaction.is_processed = True
            transaction.save()

        cancelled = helpers.build_transaction([self.purchaseItem.id], [1], campaign = self.campaign)
        cancelled.is_cancelled = True
        cancelled.save()

        res = self.client.get('/v1/campaigns/{}/'.format(self.campaign.id))
        data = res.json()
        self.assertEqual(Decimal(data.get('tickets_sold')), sum([transaction.count for transaction in transactions]))

    def test_campaign_query_1(self):
        """ should be able to load all necessary data for displaying venues on the campaign page """
        res = self.client.get('/v1/campaigns/{}/?expand=timeslot,timeslot.venue,timeslot.venue.city,timeslot.venue.city.province,timeslot.venue.city.province.country'.format(self.campaign.id))

        data = res.json()

        keys = [
            'timeslot',
            'timeslot.venue',
            'timeslot.venue.city',
            'timeslot.venue.city.name',
            'timeslot.venue.city.province',
            'timeslot.venue.city.province.name',
            'timeslot.venue.city.province.country',
            'timeslot.venue.city.province.country.name',
        ]

        helpers.assert_keys(data, keys)

    def test_query_campaign_requests(self):
        """ should be able to get all open campaign requests for a user """
        rando = helpers.build_user()
        timeslot2 = helpers.build_timeslot(self.venue)
        campaign2 = helpers.build_campaign([self.band], timeslot2, self.manager)
        campaign2.is_venue_approved = None
        campaign2.save()

        rando, venue2 = helpers.build_venue()
        timeslot3 = helpers.build_timeslot(venue2)
        campaign3 = helpers.build_campaign([self.band], timeslot3, rando)
        url = '/v1/campaigns/?timeslot__venue__managers__id__in={}&is_venue_approved=null'.format(self.manager.id)
        res = self.client.get(url)
        data = res.json().get('results')
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].get('id'), campaign2.id)


    def test_expand_photos(self):
        """ should be able to expand photos """
        res = self.client.get('/v1/campaigns/{}/?expand=photos'.format(self.campaign.id))
        data = res.json()
        photos = data.get('photos')
        ids = [p.get('id') for p in photos]
        urls = [p.get('photo') for p in photos]
        self.assertTrue(self.photo1.id in ids)
        self.assertTrue(self.photo2.id in ids)
        self.assertTrue(self.photo1.photo.url in urls)
        self.assertTrue(self.photo2.photo.url in urls)

    def test_create_anon(self):
        """ anon fuk off """
        data = {}
        res = self.client.post('/v1/campaigns/', data=data)
        self.assertEqual(res.status_code, 401)

    def test_delete_anon(self): 
        """ srsly anon fuggoff """
        res = self.client.delete('/v1/campaigns/{}/'.format(self.campaign.id))
        self.assertEqual(res.status_code, 401)

    def test_delete_not_owner(self):
        """ malicious """
        rando = helpers.build_user()
        self.client.force_authenticate(user=rando)
        res = self.client.delete('/v1/campaigns/{}/'.format(self.campaign.id))
        self.assertEqual(res.status_code, 403)

    def test_delete_success(self):
        """ malicious """
        self.client.force_authenticate(user=self.manager)
        res = self.client.delete('/v1/campaigns/{}/'.format(self.campaign.id))
        self.assertEqual(res.status_code, 204)
        campaign = Campaign.all_objects.get(pk=self.campaign.id)
        self.assertTrue(campaign.archived)

    def test_update_anon(self):
        res = self.client.put('/v1/campaigns/{}/'.format(self.campaign.id))
        self.assertEqual(res.status_code, 401)

    def test_update_not_owner(self):
        rando = helpers.build_user()
        self.client.force_authenticate(user=rando)
        res = self.client.put('/v1/campaigns/{}/'.format(self.campaign.id))
        self.assertEqual(res.status_code, 403)

    def test_update_success(self):
        """ legit """
        data = {
            'title': 'wat',
            'description': 'wat',
            'timeslot': self.timeslot.id,
            'min_ticket_price': '10.00'
        }

        self.client.force_authenticate(user=self.manager)
        res = self.client.put('/v1/campaigns/{}/'.format(self.campaign.id), data=data)
        self.assertEqual(res.status_code, 200)
        campaign = Campaign.objects.get(pk=self.campaign.id)
        self.assertEqual(campaign.title, 'wat')

    def test_check_door_code_success(self):
        self.client.force_authenticate(user=self.manager)
        url = '/v1/campaigns/check_door_code/'
        payload = {
            'door_code': self.campaign.door_code
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json().get('campaign'), self.campaign.id)

    def test_check_door_code_fail(self):
        self.client.force_authenticate(user=self.manager)
        url = '/v1/campaigns/check_door_code/'
        payload = {
            'door_code': 'wat sauce u put in this?'
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, 400)

    def test_get_door_code_success_manager(self):
        self.client.force_authenticate(self.manager)
        url = '/v1/campaigns/{}/door_code/'.format(self.campaign.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json().get('door_code'), self.campaign.door_code)

    def test_get_door_code_success_band_member(self):
        self.band.owner = helpers.build_user()
        self.band.save()
        self.client.force_authenticate(self.band.owner)
        url = '/v1/campaigns/{}/door_code/'.format(self.campaign.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json().get('door_code'), self.campaign.door_code)

    def test_get_door_code_not_authorized(self):
        user = helpers.build_user()
        self.client.force_authenticate(user)
        url = '/v1/campaigns/{}/door_code/'.format(self.campaign.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, 403)

    def test_get_door_code_anon(self):
        url = '/v1/campaigns/{}/door_code/'.format(self.campaign.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, 403)


class CampaignModelTest(TestCase):
    def setUp(self):
        manager, venue = helpers.build_venue()
        self.band = helpers.build_band()
        self.timeslot = helpers.build_timeslot(venue)
        self.client = APIClient()
        self.campaign = helpers.build_campaign([self.band], self.timeslot)
        self.purchaseItem = helpers.build_purchase_item(self.campaign)

    def test_description_valid(self):
        description = """
        # BOOTLEG BACKWOODS SHOW

        ## Come get drunk plz

        We will be getting *quite fucking inebriated* in the backwoods **THIS SATURDAY** and we would __LOVE__ if you could join us.

        There will be plenty of:

        * circus shenanigans
        * firebreathing faeries
        * STRIPPERS! (who doesnt love strippers right)

        Please make sure you are:

        1. Prepared
        2. Drunk

        _k fuck off pass tests plz._
        """

        self.campaign.description = description
        self.campaign.save()
        self.assertEqual(self.campaign.description, description)

    def test_goal_count(self):
        self.campaign.funding_type = Campaign.GOAL_COUNT
        self.campaign.save()
        self.timeslot.min_headcount = 10
        self.timeslot.save()
        self.assertFalse(self.campaign.check_if_successful())
        tp = self.campaign.min_ticket_price
        u1 = helpers.build_user()
        helpers.build_transaction([self.purchaseItem.id], [1], campaign = self.campaign, total = tp * Decimal('5'), count = 5)
        self.assertFalse(self.campaign.check_if_successful())
        helpers.build_transaction([self.purchaseItem.id], [1], campaign = self.campaign, total = tp * Decimal('2'), count = 2)
        self.assertFalse(self.campaign.check_if_successful())
        helpers.build_transaction([self.purchaseItem.id], [1], campaign = self.campaign, total = tp * Decimal('2'), count = 2)
        self.assertFalse(self.campaign.check_if_successful())
        helpers.build_transaction([self.purchaseItem.id], [1], campaign = self.campaign, total = tp * Decimal('2'), count = 2)
        self.assertTrue(self.campaign.check_if_successful())

    def test_goal_amount(self):
        self.campaign.funding_type = Campaign.GOAL_AMOUNT
        self.campaign.save()
        self.timeslot.asking_price = Decimal('10')*self.campaign.min_ticket_price
        self.timeslot.save()
        self.assertFalse(self.campaign.check_if_successful())
        tp = self.campaign.min_ticket_price
        u1 = helpers.build_user()
        helpers.build_transaction([self.purchaseItem.id], [1], campaign = self.campaign, total = tp * Decimal('5'), count = 5)
        self.assertFalse(self.campaign.check_if_successful())
        helpers.build_transaction([self.purchaseItem.id], [1], campaign = self.campaign, total = tp * Decimal('2'), count = 2)
        self.assertFalse(self.campaign.check_if_successful())
        helpers.build_transaction([self.purchaseItem.id], [1], campaign = self.campaign, total = tp * Decimal('2'), count = 2)
        self.assertFalse(self.campaign.check_if_successful())
        helpers.build_transaction([self.purchaseItem.id], [1], campaign = self.campaign, total = tp * Decimal('2'), count = 2)
        self.assertTrue(self.campaign.check_if_successful())

    def test_has_door_code(self):
        self.assertNotEqual(self.campaign.door_code, None)
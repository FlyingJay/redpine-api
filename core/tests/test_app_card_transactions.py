from django.test import TestCase
from core.tests import helpers
from core.models import *
from core import views
from rest_framework.test import APIClient
from unittest.mock import patch
from decimal import Decimal


class AppCardTransactionTest(TestCase):
    def setUp(self):
        manager, venue = helpers.build_venue()
        self.user1 = User.objects.create_user(username='user1', password='user1')
        self.band_member = User.objects.create_user(username='user2', password='user2')
        self.band = helpers.build_band(band_member=self.band_member)
        timeslot = helpers.build_timeslot(venue)
        self.client = APIClient()
        self.campaign = helpers.build_campaign([self.band], timeslot)
        self.venue_manager = manager
        self.purchaseItem = helpers.build_purchase_item(self.campaign)

    def tearDown(self):
        helpers.clear_media()
        self.client.logout()

    def test_list_anon(self):
        res = self.client.get('/v1/app-card-transactions/')
        self.assertEqual(res.status_code, 401)

    def test_list(self):
        self.client.force_authenticate(user=self.user1)
        res = self.client.get('/v1/app-card-transactions/')
        self.assertEqual(res.status_code, 403)

    def test_retrieve_anon(self):
        transaction = helpers.build_app_card_transaction(campaign=self.campaign)
        res = self.client.get('/v1/app-card-transactions/{}/'.format(transaction.id))
        self.assertEqual(res.status_code, 401)

    def test_retrieve(self):
        transaction = helpers.build_app_card_transaction(campaign=self.campaign)
        self.client.force_authenticate(user=self.user1)
        res = self.client.get('/v1/app-card-transactions/{}/'.format(transaction.id))
        self.assertEqual(res.status_code, 403)

    def test_update_anon(self):
        transaction = helpers.build_app_card_transaction(campaign=self.campaign)
        res = self.client.put('/v1/app-card-transactions/{}/'.format(transaction.id), {})
        self.assertEqual(res.status_code, 401)

    def test_update(self):
        transaction = helpers.build_app_card_transaction(campaign=self.campaign)
        self.client.force_authenticate(user=self.user1)
        res = self.client.put('/v1/app-card-transactions/{}/'.format(transaction.id), {})
        self.assertEqual(res.status_code, 403)

    def test_delete_anon(self):
        transaction = helpers.build_app_card_transaction(campaign=self.campaign)
        res = self.client.delete('/v1/app-card-transactions/{}/'.format(transaction.id), {})
        self.assertEqual(res.status_code, 401)

    def test_delete(self):
        transaction = helpers.build_app_card_transaction(campaign=self.campaign)
        self.client.force_authenticate(user=self.user1)
        res = self.client.delete('/v1/app-card-transactions/{}/'.format(transaction.id), {})
        self.assertEqual(res.status_code, 403)

    def test_create_anon(self):
        transaction = helpers.build_app_card_transaction(campaign=self.campaign)
        res = self.client.post('/v1/app-card-transactions/', {})
        self.assertEqual(res.status_code, 401)

    def _create_purchase(self, door_code=None):
        """ this method creates a transaction.  if the user
        is appropriately authenticated, then it should work """
        CampaignBand.objects.filter(campaign=self.campaign)

        bands = [CampaignBand.objects.filter(campaign=self.campaign).first().id]
        payload = {
            'campaign': self.campaign.id,
            'bands': [CampaignBand.objects.filter(campaign=self.campaign).first().id],
            'items': [self.purchaseItem.id],
            'quantities': [2],
        }

        if door_code is not None:
            payload['door_code'] = door_code

        res = self.client.post('/v1/app-card-transactions/', payload, format='json')

        return res

    def test_create_random(self):
        """ user is not authorized """
        self.client.force_authenticate(user=self.user1)
        res = self._create_purchase()
        self.assertEqual(res.status_code, 403)

    def test_create_venue(self):
        """ user is a venue manager """
        self.client.force_authenticate(user=self.venue_manager)
        res = self._create_purchase()
        self.assertEqual(res.status_code, 201)

    def test_create_band_member(self):
        """ user is a band member in the show """
        self.client.force_authenticate(user=self.band_member)
        res = self._create_purchase()
        self.assertEqual(res.status_code, 201)

    def test_create_door_code(self):
        """ user has been given access via door code """
        self.client.force_authenticate(user=self.user1)
        res = self._create_purchase(self.campaign.door_code)
        self.assertEqual(res.status_code, 201)

    def test_create_invalid_door_code(self):
        """ user has been given access via door code """
        self.client.force_authenticate(user=self.user1)
        res = self._create_purchase('invalid')
        self.assertEqual(res.status_code, 403)

    def test_create_verify_data(self):
        """ this test verifies the information stored in the db is
        correct after creation """
        self.client.force_authenticate(user=self.venue_manager)
        res = self._create_purchase()
        data = res.json()
        self.assertEqual(data.get('total'), '20.00') # tickets are $10.00
        self.assertEqual(data.get('count'), 2) # 2 tickets purchased
        self.assertEqual(data.get('redpine_fee'), '3.00') # default fee is 15%
        self.assertEqual(data.get('processed_by'), self.venue_manager.id)
        self.assertEqual(len(data.get('purchases')), 1)
        purchase_id = data.get('purchases')[0]
        purchase = AppCardTransactionPurchase.objects.get(pk=purchase_id)
        self.assertEqual(purchase.quantity, 2)
        self.assertEqual(purchase.item, self.purchaseItem)

    def _square_callback_test(self, door_code=None):
        """ runs the square callback test.  used below with different actors """
        transaction = helpers.build_app_card_transaction(campaign=self.campaign)
        payload = {
            'transaction_id': 'transaction_id',
            'client_transaction_id': 'client_transaction_id'
        }

        if door_code: payload['door_code'] = door_code
        res = self.client.post('/v1/app-card-transactions/{}/square_pos_callback/'.format(transaction.id), payload, format='json')
        self.assertEqual(res.status_code, 204)
        transaction = AppCardTransaction.objects.get(pk=transaction.id)
        self.assertEqual(transaction.transaction_id, 'transaction_id')
        self.assertEqual(transaction.client_transaction_id, 'client_transaction_id')

    def test_square_callback_venue(self):
        self.client.force_authenticate(user=self.venue_manager)
        self._square_callback_test()

    def test_square_callback_band_member(self):
        self.client.force_authenticate(user=self.band_member)
        self._square_callback_test()

    def test_square_callback_door_code(self):
        self.client.force_authenticate(user=self.user1)
        self._square_callback_test(self.campaign.door_code)

    def _square_callback_fail(self, status_code, door_code = None):
        """ tests failure, if they're not authorized """
        transaction = helpers.build_app_card_transaction(campaign=self.campaign)
        payload = {
            'transaction_id': 'transaction_id',
            'client_transaction_id': 'client_transaction_id'
        }
        if door_code is not None: payload['door_code'] = door_code
        res = self.client.post('/v1/app-card-transactions/{}/square_pos_callback/'.format(transaction.id), payload, format='json')
        self.assertEqual(res.status_code, status_code)

    def test_square_callback_random(self):
        self.client.force_authenticate(user=self.user1)
        self._square_callback_fail(403)

    def test_square_callback_anon(self):
        self._square_callback_fail(401)

    def test_square_callback_fail_door_code(self):
        self.client.force_authenticate(user=self.user1)
        self._square_callback_fail(403, 'wrong door code')
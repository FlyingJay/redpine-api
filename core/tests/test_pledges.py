from django.test import TestCase
from core.tests import helpers
from core.models import *
from core import views
from rest_framework.test import APIClient
from unittest.mock import patch
from decimal import Decimal
import square

from squareconnect.rest import ApiException

class WebTransactionViewSetTest(TestCase):
    def setUp(self):
        manager, venue = helpers.build_venue()
        band = helpers.build_band()
        timeslot = helpers.build_timeslot(venue)
        self.client = APIClient()
        self.campaign = helpers.build_campaign([band], timeslot)
        self.purchaseItem = helpers.build_purchase_item(self.campaign)
        self.user1 = helpers.build_user(username='user1', password='user1', email='fake@fakaroo.com')
        self.user2 = helpers.build_user(username='user2', password='user2', email='fake2@fakaroo.com')

    def tearDown(self):
        helpers.clear_media()
        self.client.logout()

    def test_create_transaction_anonymous(self):
        """ Should fail if an unauthenticated user attempts to create a transaction """
        res = self.client.post('/v1/pledges/', data={})
        self.assertEqual(res.status_code, 401)
    """
    def test_create_rsvp_success(self):
        Should create a new rsvp.
        data = {
            'total': 0.00,
            'count': 1,
            'campaign': self.campaign.id,
            'bands': [ self.campaign.campaignband_set.first().id ],
            'items': [self.purchaseItem.id],
            'quantities': [1]
        }
        self.client.force_authenticate(user=self.user1)
        res = self.client.post('/v1/transactions/', data=data)
        self.assertEqual(res.status_code, 200)

        data = res.json()
        transaction = Pledge.objects.get(id=data.get('id'))
        self.assertEqual(transaction.total, Decimal('25'))
        self.assertEqual(transaction.count, 1)
        self.assertEqual(transaction.campaign, self.campaign)
        self.assertEqual(transaction.bands.count(), 1)
        self.assertEqual(transaction.bands.first(), self.campaign.campaignband_set.first())
    """
    def test_list_transactions(self):
        """ Should return a paginated list of a user's transactions """
        going_to_see = [self.campaign.campaignband_set.first()]
        transaction = helpers.build_transaction(
            [self.purchaseItem.id],
            [1],
            user=self.user1, 
            campaign=self.campaign, 
            bands=going_to_see
            )
        self.client.force_authenticate(user=self.user1)
        res = self.client.get('/v1/pledges/')
        self.assertEqual(res.status_code, 200)
        transactions = res.json().get('results')
        self.assertEqual(len(transactions), 1)

        purchase = transaction.purchases.first()

        expected = {
            'id': transaction.id,
            'total': str(transaction.total),
            'redpine_fee': str(transaction.redpine_fee),
            'count': transaction.count,
            'campaign': transaction.campaign.id,
            'bands': [g.id for g in going_to_see],
            'is_cancelled': False,
            'is_processed': transaction.is_processed,
            'is_processing_failed': transaction.is_processing_failed,
            'promoter': None,
            'purchases': [purchase.id]
        }

        self.assertEqual(transactions[0], expected)


    def test_list_transactions_anonymous(self):
        """ Should return 401 for anonymous user """

        res = self.client.get('/v1/pledges/')
        self.assertEqual(res.status_code, 401)


    def test_retrieve_transaction_success(self):
        """ Should return a transaction successfully """
        
        going_to_see = [self.campaign.campaignband_set.first()]
        transaction = helpers.build_transaction(
            [self.purchaseItem.id],
            [1],
            user=self.user1, 
            campaign=self.campaign, 
            bands=going_to_see
            )
        self.client.force_authenticate(user=self.user1)
        res = self.client.get('/v1/pledges/{}/'.format(transaction.id))
        self.assertEqual(res.status_code, 200)

        purchase = transaction.purchases.first()

        expected = {
            'id': transaction.id,
            'total': str(transaction.total),
            'redpine_fee': str(transaction.redpine_fee),
            'count': transaction.count,
            'campaign': transaction.campaign.id,
            'bands': [g.id for g in going_to_see],
            'is_cancelled': False,
            'is_processed': transaction.is_processed,
            'is_processing_failed': transaction.is_processing_failed,
            'promoter': None,
            'purchases': [purchase.id]
        }
        self.assertEqual(res.json(), expected)


    def test_delete_processed_transaction_failure(self):
        """ A user should not be able to delete a processed transaction; should return 403 """
        
        going_to_see = [self.campaign.campaignband_set.first()]
        transaction = helpers.build_transaction(
            [self.purchaseItem.id],
            [1],
            user=self.user1, 
            campaign=self.campaign, 
            bands=going_to_see
            )
        transaction.is_processed = True
        transaction.save()

        self.client.force_authenticate(user=self.user1)
        res = self.client.delete('/v1/pledges/{}/'.format(transaction.id))
        self.assertEqual(res.status_code, 403)


    def test_delete_unprocessed_transaction_wrong_user(self):
        """ A user not be able to delete another user's transaction """

        going_to_see = [self.campaign.campaignband_set.first()]
        transaction_1 = helpers.build_transaction(
            [self.purchaseItem.id],
            [1],
            user=self.user1, 
            campaign=self.campaign, 
            bands=going_to_see
            )
        transaction_2 = helpers.build_transaction(
            [self.purchaseItem.id],
            [1],
            user=self.user2, 
            campaign=self.campaign, 
            bands=going_to_see
            )
        self.client.force_authenticate(user=self.user1)
        res = self.client.delete('/v1/pledges/{}/'.format(transaction_2.id))
        self.assertEqual(res.status_code, 403)


    def test_delete_unprocessed_transaction(self):
        """ 
        A user should be able to DELETE a transaction that has not yet been processed
        however, this should effectively only set the `is_cancelled` flag on the transaction
        """
        going_to_see = [self.campaign.campaignband_set.first()]
        transaction = helpers.build_transaction(
            [self.purchaseItem.id],
            [1],
            user=self.user1, 
            campaign=self.campaign, 
            bands=going_to_see
            )
        self.client.force_authenticate(user=self.user1)
        res = self.client.delete('/v1/pledges/{}/'.format(transaction.id))
        self.assertEqual(res.status_code, 200)

        reloaded_transaction = Pledge.objects.get(id=transaction.id)
        self.assertTrue(reloaded_transaction.is_cancelled)


    def test_delete_anonymous(self):
        """ Anonymous user should get 401 """
        res = self.client.delete('/v1/pledges/1/')
        self.assertEqual(res.status_code, 401)


    def test_update_transaction_failure(self):
        """ No user should be able to update a transaction; should be 403 forbidden """
        going_to_see = [self.campaign.campaignband_set.first()]
        transaction = helpers.build_transaction(
            [self.purchaseItem.id],
            [1],
            user=self.user1, 
            campaign=self.campaign, 
            bands=going_to_see
            )
        self.client.force_authenticate(user=self.user1)
        res = self.client.put('/v1/pledges/{}/'.format(transaction.id), data={'dont': 'care'})
        self.assertEqual(res.status_code, 403)
from django.test import TestCase
from core.tests import helpers
from core.models import *
from core import views
from rest_framework.test import APIClient
from unittest.mock import patch
from decimal import Decimal


class TicketViewSetTest(TestCase):
    def setUp(self):
        manager, self.venue = helpers.build_venue()
        self.band = helpers.build_band()
        self.timeslot = helpers.build_timeslot(self.venue)
        self.client = APIClient()
        self.campaign = helpers.build_campaign([self.band], self.timeslot)
        self.purchaseItem = helpers.build_purchase_item(self.campaign)
        self.user1 = User.objects.create_user(username='user1', password='user1')
        self.user2 = User.objects.create_user(username='user2', password='user2')
        self.transaction1 = helpers.build_transaction(
            [self.purchaseItem.id],
            [1],
            user=self.user1,
            campaign=self.campaign
        )
        self.ticket1 = helpers.build_ticket(transaction=self.transaction1,details=self.purchaseItem)
        self.transaction2 = helpers.build_transaction(
            [self.purchaseItem.id],
            [1],
            user=self.user2,
            campaign=self.campaign
        )
        self.ticket2 = helpers.build_ticket(transaction=self.transaction2,details=self.purchaseItem)

    def tearDown(self):
        pass

    def test_create(self):
        """ users prob shouldn't be able to create tickets lol """
        self.client.force_authenticate(self.user1)
        res = self.client.post('/v1/tickets/')
        self.assertEqual(res.status_code, 403)

    def test_list(self):
        """ users should be able to list all tickets that they have in the system """
        self.client.force_authenticate(self.user1)
        res = self.client.get('/v1/tickets/')
        self.assertEqual(res.status_code, 200)

        data = res.json().get('results')
        self.assertEqual(data, [{ 'id': self.ticket1.id, 'code': self.ticket1.code, 'pledge': self.transaction1.id, 'details': self.purchaseItem.id, 'scans': [] }])

    def test_list_anon(self):
        """ anon should be denied """
        res = self.client.get('/v1/tickets/')
        self.assertEqual(res.status_code, 401)

    def test_get(self):
        """ user should be able to get their own ticket """
        self.client.force_authenticate(self.user1)
        res = self.client.get('/v1/tickets/{}/'.format(self.ticket1.id))
        self.assertEqual(res.status_code, 200)

        data = res.json()
        self.assertEqual(data, { 'id': self.ticket1.id, 'code': self.ticket1.code, 'pledge': self.transaction1.id, 'details': self.purchaseItem.id, 'scans': [] })

    def test_get_other_users_ticket(self):
        """ user should not be able to view someone elses ticket """
        self.client.force_authenticate(self.user1)
        res = self.client.get('/v1/tickets/{}/'.format(self.ticket2.id))
        self.assertEqual(res.status_code, 404)

    def test_update(self):
        """ user should not be able to update a ticket """
        self.client.force_authenticate(self.user1)
        res = self.client.put('/v1/tickets/{}/'.format(self.ticket1.id))
        self.assertEqual(res.status_code, 403)

    def test_delete(self):
        """ user should not be able to delete a ticket """
        self.client.force_authenticate(self.user1)
        res = self.client.delete('/v1/tickets/{}/'.format(self.ticket1.id))
        self.assertEqual(res.status_code, 403)

    def test_query_for_my_tickets(self):
        """ tests expansions required by the /users/me/tickets page on web """
        self.client.force_authenticate(self.user1)
        res = self.client.get('/v1/tickets/?expand=pledge,pledge.campaign,pledge.campaign.bands,pledge.campaign.bands.band,pledge.campaign.timeslot,pledge.campaign.timeslot.venue')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        results = data.get('results')
        res = results[0]

        transaction = res.get('pledge')
        self.assertEqual(transaction.get('id'), self.transaction1.id)

        campaign = transaction.get('campaign')
        self.assertEqual(campaign.get('id'), self.campaign.id)

        campaign_bands = campaign.get('bands')
        self.assertEqual(len(campaign_bands), 1)
        self.assertEqual(campaign_bands[0].get('id'), self.campaign.campaignband_set.first().id)
        self.assertEqual(campaign_bands[0].get('band').get('id'), self.band.id)

        timeslot = campaign.get('timeslot')
        self.assertEqual(timeslot.get('id'), self.timeslot.id)

        venue = timeslot.get('venue')
        self.assertEqual(venue.get('id'), self.venue.id)

    def test_expand_scans(self):
        """ verifies that we can expand scans from tickets """
        scan = Scan.objects.create(ticket=self.ticket1)
        self.client.force_authenticate(self.user1)
        res = self.client.get('/v1/tickets/?expand=scans')
        data = res.json()
        ticket = data.get('results')[0]
        scans = ticket.get('scans')
        self.assertEqual(len(scans), 1)

        _scan = scans[0]
        self.assertEqual(_scan.get('created'), scan.created.isoformat())

    def test_validate_no_code(self):
        self.client.force_authenticate(self.user1)
        data = {}
        res = self.client.post('/v1/tickets/validate/', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data.get('code'), views.ERROR_STRINGS.TICKET_CODE_NOT_SUPPLIED)

    def test_validate_failure(self):
        self.client.force_authenticate(self.user1)
        data = {
            'code': '123'
        }
        res = self.client.post('/v1/tickets/validate/', data=data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.data.get('detail'), views.ERROR_STRINGS.TICKET_CODE_INVALID)

    def test_validate_success(self):
        self.client.force_authenticate(self.user1)
        data = {
            'code': self.ticket1.code
        }
        res = self.client.post('/v1/tickets/validate/', data=data)
        self.assertEqual(res.status_code, 200)

    def test_validate_expansion(self):
        """ verifies that validated tickets can be expanded """
        self.client.force_authenticate(self.user1)
        data = {
            'code': self.ticket1.code
        }
        res = self.client.post('/v1/tickets/validate/?expand=pledge', data=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data.get('pledge').get('id'), self.ticket1.pledge.id)

    def test_validate_creates_scans(self):
        """ a scan should be created each time a ticket is scanned """
        self.client.force_authenticate(self.user1)
        data = {
            'code': self.ticket1.code
        }
        res = self.client.post('/v1/tickets/validate/', data=data)
        scans = Scan.objects.filter(ticket=self.ticket1)
        self.assertEqual(scans.count(), 1)

        res = self.client.post('/v1/tickets/validate/', data=data)
        scans = Scan.objects.filter(ticket=self.ticket1)
        self.assertEqual(scans.count(), 2)
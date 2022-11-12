from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings
from core import views, tasks, models
from core.tests import helpers
from rest_framework.test import APIClient
from unittest.mock import patch
from decimal import Decimal
from background_task.models import Task
from maas.models import Mail
import square

class CheckWebTransactionTest(TestCase):
    def setUp(self):
        manager, venue = helpers.build_venue()
        band = helpers.build_band()
        timeslot = helpers.build_timeslot(venue)
        self.client = APIClient()
        self.campaign = helpers.build_campaign([band], timeslot)
        self.purchaseItem = helpers.build_purchase_item(self.campaign)
        self.user1 = User.objects.create_user(username='user1', password='user1', email='fake@fakaroo.com')
        self.user2 = User.objects.create_user(username='user2', password='user2', email='fake2@fakaroo.com')
        self.profile1 = models.Profile.objects.create(user=self.user1, picture=helpers.mock_image)
        self.profile2 = models.Profile.objects.create(user=self.user2, picture=helpers.mock_image)


class ProcessWebTransactionTest(TestCase):
    def setUp(self):
        manager, venue = helpers.build_venue()
        band = helpers.build_band()
        timeslot = helpers.build_timeslot(venue)
        self.client = APIClient()
        self.campaign = helpers.build_campaign([band], timeslot)
        self.purchaseItem = helpers.build_purchase_item(self.campaign)
        self.user1 = User.objects.create_user(username='user1', password='user1')
        self.user2 = User.objects.create_user(username='user2', password='user2')

    @patch('square.models.Customer.charge')
    def test_process_cancelled_transaction(self, charge):
        """ should do nothing if a cancelled transaction is processed """
        transaction = helpers.build_transaction(
            [self.purchaseItem.id],
            [1],
            user=self.user1,
            campaign=self.campaign,
        )
        transaction.is_cancelled = True
        transaction.save()
        tasks.process_transaction.now(transaction.id)
        self.assertEqual(charge.call_count, 0)

    @patch('square.models.Customer.charge')
    def test_process_processed_transaction(self, charge):
        """ should do nothing if a processed transaction is processed """
        transaction = helpers.build_transaction(
            [self.purchaseItem.id],
            [1],
            user=self.user1,
            campaign=self.campaign,
        )
        transaction.is_processed = True
        transaction.save()
        tasks.process_transaction.now(transaction.id)
        self.assertEqual(charge.call_count, 0)

    @patch('core.helpers.create_mail_from_template')
    @patch('square.models.Customer.charge', return_value={'id': 'cust_id'})
    def test_process_transaction_success(self, charge, mail):
        """ should send email if the transaction was successfully processed """
        transaction = helpers.build_transaction(
            [self.purchaseItem.id],
            [1],
            count=1,
            user=self.user1,
            campaign=self.campaign,
        )
        tasks.process_transaction.now(transaction.id)
        pp = models.Pledge.objects.get(pk=transaction.id)
        self.assertTrue(pp.is_processed)


class SendMailTest(TestCase):
    def setUp(self):
        pass

    @patch('maas.models.Mail.send')
    def test_send_mail(self, send):
        """ should call send function """
        mail = Mail.objects.create(recipient='test@test.com', subject='Test', body='test')
        tasks.send_mail.now(mail.id)
        self.assertEqual(send.call_count, 1)

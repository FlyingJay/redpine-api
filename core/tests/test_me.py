from django.test import TestCase
from django.test.utils import override_settings
from core.tests import helpers
from core.models import *
from core import views
from rest_framework.test import APIClient
from unittest.mock import patch
from decimal import Decimal


class MeViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='user1', first_name='Test', last_name='User')
        self.profile = Profile.objects.create(user=self.user, picture=helpers.mock_image)
        self.client = APIClient()

    def tearDown(self):
        helpers.clear_media()
        self.client.logout()

    def test_get_unauthenticated(self):
        res = self.client.get('/v1/me/')
        self.assertEqual(res.status_code, 403)

    @override_settings(TAWK_API_KEY='known_value')
    def test_get(self):
        self.client.force_authenticate(self.user)
        res = self.client.get('/v1/me/')
        self.assertEqual(res.status_code, 200)

        expected = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'profile': {
                'account_balance': '0.00',
                'id': self.profile.id,
                'is_artist': self.profile.is_artist,
                'is_member_artist': self.profile.is_member_artist,
                'is_ultimate_artist': self.profile.is_ultimate_artist,
                'is_venue': self.profile.is_venue,
                'is_member_venue': self.profile.is_member_venue,
                'is_ultimate_venue': self.profile.is_ultimate_venue,
                'is_member_organizer': self.profile.is_member_organizer,
                'is_email_confirmed': self.profile.is_email_confirmed,
                'notifications': [],
                'picture': self.profile.picture.url,
                'birthdate': None,
                'has_unread_notifications': False,
                'tawk_hash': '64d0166340fad6a7ae4afcecd7eb087e183623b2320caf6b29ad46a14b6434f1',
                'referral_url': self.profile.referral_url(),

                'welcome_add_profile_pic': False,
                'welcome_view_my_tickets': False,
                'welcome_create_act': False,
                'welcome_add_act_socials': False,
                'welcome_submit_booking_request': False,
                'welcome_create_venue': False,
                'welcome_check_calendar': False,
                'welcome_add_event': False,
                'welcome_approve_booking_request': False
            }
        }

        self.maxDiff = None
        self.assertEqual(res.json(), expected)

    def test_post_unauthenticated(self):
        res = self.client.post('/v1/me/')
        self.assertEqual(res.status_code, 403)

    def test_post_is_artist(self):
        self.client.force_authenticate(self.user)

        data = {
            'profile': {
                'is_artist': True
            }
        }

        res = self.client.post('/v1/me/', data=data, format='json')
        self.assertEqual(res.status_code, 200)
        p2 = Profile.objects.get(id=self.profile.id)
        self.assertTrue(p2.is_artist)

    def test_post_is_venue(self):
        self.client.force_authenticate(self.user)

        data = {
            'profile': {
                'is_venue': True
            }
        }

        res = self.client.post('/v1/me/', data=data, format='json')
        self.assertEqual(res.status_code, 200)
        p2 = Profile.objects.get(id=self.profile.id)
        self.assertTrue(p2.is_venue)

    def test_post_is_email_confirmed(self):
        """ should NOT be able to update this property """
        self.client.force_authenticate(self.user)

        data = {
            'profile': {
                'is_email_confirmed': True
            }
        }

        res = self.client.post('/v1/me/', data=data, format='json')
        self.assertEqual(res.status_code, 200)
        p2 = Profile.objects.get(id=self.profile.id)
        self.assertFalse(p2.is_email_confirmed)

    def test_post_profile_picture(self):
        """ should be able to upload their profile picture """
        self.client.force_authenticate(self.user)

        data = {
            'profile': {
                'picture': helpers.mock_image_raw
            }
        }

        res = self.client.post('/v1/me/', data=data, format='json')
        self.assertEqual(res.status_code, 200)
        res = self.client.get('/v1/me/')
        p2 = Profile.objects.get(id=self.profile.id)
        self.assertEqual(res.json().get('profile').get('picture'), p2.picture.url)
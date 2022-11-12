from django.test import TestCase
from django.test.utils import override_settings
from rest_framework.test import APIClient
from core.tests import helpers
from core.models import *


class PushTokenTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='user1', first_name='Test', last_name='User')
        self.user2 = User.objects.create_user(username='user2', password='user2', first_name='Test', last_name='User')
        self.client = APIClient()

    def tearDown(self):
        helpers.clear_media()
        self.client.logout()

    def test_add_token(self):
        self.client.force_authenticate(self.user)
        res = self.client.post('/v1/push-tokens/', {
            'token': 'token'
        }, format='json')
        res = self.assertEqual(res.status_code, 201)
        self.assertTrue(PushToken.objects.filter(user=self.user).exists())
        self.assertEqual(PushToken.objects.get(user=self.user).token, 'token')

    def test_add_token_duplicate(self):
        PushToken.objects.filter(user=self.user).delete()
        PushToken.objects.create(user=self.user, token='test')
        self.client.force_authenticate(self.user)
        res = self.client.post('/v1/push-tokens/', {
            'token': 'token'
        }, format='json')
        res = self.assertEqual(res.status_code, 201)
        self.assertEqual(PushToken.objects.filter(user=self.user).count(), 2)
        self.client.force_authenticate(self.user)
        res = self.client.post('/v1/push-tokens/', {
            'token': 'token'
        }, format='json')
        res = self.assertEqual(res.status_code, 200)
        self.assertEqual(PushToken.objects.filter(user=self.user).count(), 2)

    def test_add_token_anon(self):
        res = self.client.post('/v1/push-tokens/', {
            'token': 'token'
        }, format='json')
        self.assertEqual(res.status_code, 401)

    def test_add_token_other_user(self):
        self.client.force_authenticate(self.user2)
        res = self.client.post('/v1/push-tokens/', {
            'token': 'token',
            'user': self.user.id
        }, format='json')
        self.assertEqual(res.status_code, 201)
        self.assertTrue(PushToken.objects.filter(user=self.user2).exists())

    def test_update(self):
        self.client.force_authenticate(self.user)
        token = PushToken.objects.create(token='hi', user=self.user)
        res = self.client.put('/v1/push-tokens/{}/'.format(token.id), {
            'token': 'token',
            'user': self.user.id
        }, format='json')
        self.assertEqual(res.status_code, 403)

    def test_delete_by_token_anon(self):
        token = PushToken.objects.create(token='hi', user=self.user)
        res = self.client.delete('/v1/push-tokens/delete_by_token/?token={}'.format(token.token))
        self.assertEqual(res.status_code, 401)

    def test_delete_token_for_other_user(self):
        self.client.force_authenticate(self.user2)
        token = PushToken.objects.create(token='hi', user=self.user)
        res = self.client.delete('/v1/push-tokens/delete_by_token/?token={}'.format(token.token))
        self.assertEqual(res.status_code, 403)
    
    def test_delete_token_for_self(self):
        self.client.force_authenticate(self.user)
        token = PushToken.objects.create(token='hi', user=self.user)
        res = self.client.delete('/v1/push-tokens/delete_by_token/?token={}'.format(token.token))
        self.assertEqual(res.status_code, 204)
        self.assertFalse(PushToken.objects.filter(id=token.id).exists())

    def test_delete(self):
        """ 
        this is the default delete method for DRF
        it takes an id, but we want to search by push token
        so instead, we use teh delete_by_token list route
        """
        self.client.force_authenticate(self.user)
        token = PushToken.objects.create(token='hi', user=self.user)
        res = self.client.delete('/v1/push-tokens/{}/'.format(token.id))
        self.assertEqual(res.status_code, 403)

    def test_get(self):
        self.client.force_authenticate(self.user)
        token = PushToken.objects.create(token='hi', user=self.user)
        res = self.client.get('/v1/push-tokens/{}/'.format(token.id))
        self.assertEqual(res.status_code, 403)

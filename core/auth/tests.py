from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.urls import reverse
from unittest.mock import patch, MagicMock
from core.models import *
from core.exceptions import *
from core.tests import helpers
from core.auth.views import *
from faker import Factory
from .views import check_user
import core.tests.helpers

fake = Factory.create()


class FacebookAuthTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch('facebook.facebook.FacebookClient.confirm')
    @patch('facebook.facebook.FacebookClient.get_email', side_effect=Exception())
    def test_facebook_auth_failure(self, confirm_patch, get_email_patch):
        """
        handles scenario where facebook calls fail
        """
        url = reverse('v1-auth-facebook')
        data = {
            'redirect_uri': 'http://fake.com',
            'code': 'fake'
        }

        res = self.client.post(url, data=data)
        data = res.json()
        
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data.get('detail'), 'Facebook authentication failed')

    @patch('facebook.facebook.FacebookClient.confirm')
    @patch('facebook.facebook.FacebookClient.get_email', return_value='test@test.com')
    def test_facebook_auth_email_not_found(self, confirm_patch, get_email_patch):
        """
        handles scenario where an email address is successfully retrieved from facebook but that email is not in our system
        """
        url = reverse('v1-auth-facebook')
        data = {
            'redirect_uri': 'http://fake.com',
            'code': 'fake'
        }

        res = self.client.post(url, data=data)
        data = res.json()
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data.get('detail'), 'User with specified email not found')

    @patch('facebook.facebook.FacebookClient.confirm')
    @patch('facebook.facebook.FacebookClient.get_email', return_value='test@test.com')
    def test_facebook_auth_success(self, confirm_patch, get_email_patch):
        """
        handles scenario where user successfully logs in
        """
        user = User.objects.create(
            username='test',
            password='test',
            email='test@test.com'
        )
        token = Token.objects.create(user=user)

        url = reverse('v1-auth-facebook')
        data = {
            'redirect_uri': 'http://fake.com',
            'code': 'fake'
        }

        res = self.client.post(url, data=data)
        data = res.json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data.get('token'), token.key)
        self.assertEqual(data.get('user'), user.id)

    @patch('facebook.facebook.FacebookClient.confirm')
    @patch('facebook.facebook.FacebookClient.get_email', return_value='test@test.com')
    def test_facebook_auth_success_case_insensitive(self, confirm_patch, get_email_patch):
        """
        handles scenario where user successfully logs in with the wrong case email
        """
        user = User.objects.create(
            username='test',
            password='test',
            email='test@tesT.com'
        )
        token = Token.objects.create(user=user)

        url = reverse('v1-auth-facebook')
        data = {
            'redirect_uri': 'http://fake.com',
            'code': 'fake'
        }

        res = self.client.post(url, data=data)
        data = res.json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data.get('token'), token.key)
        self.assertEqual(data.get('user'), user.id)


class PasswordAuthTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_user_not_found(self):
        url = reverse('v1-auth-password')
        data = {
            'username': 'fake',
            'password': 'fake'
        }

        res = self.client.post(url, data=data)
        self.assertEqual(res.status_code, 400)

    def test_user_found_by_username_invalid_password(self):
        user = User.objects.create_user(
            username='fake',
            password='fake',
        )

        profile = Profile.objects.create(user=user)

        url = reverse('v1-auth-password')
        data = {
            'username': 'fake',
            'password': 'fakez'
        }

        res = self.client.post(url, data=data)
        self.assertEqual(res.status_code, 400)

    def test_user_found_by_email_invalid_password(self):
        user = User.objects.create_user(
            username='fake',
            password='fake',
            email='fake@fake.com'
        )

        profile = Profile.objects.create(user=user)

        url = reverse('v1-auth-password')
        data = {
            'username': 'fake@fake.com',
            'password': 'fakez'
        }

        res = self.client.post(url, data=data)
        self.assertEqual(res.status_code, 400)

    def test_user_found_by_username_valid_password(self):
        user = User.objects.create_user(
            username='fake',
            password='fake',
        )

        profile = Profile.objects.create(user=user)

        token = Token.objects.create(user=user)

        url = reverse('v1-auth-password')
        data = {
            'username': 'fake',
            'password': 'fake'
        }

        res = self.client.post(url, data=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json().get('token'), token.key)

    def test_user_found_by_email_valid_password(self):
        user = User.objects.create_user(
            username='fake',
            password='fake',
            email='fake@fake.com'
        )

        profile = Profile.objects.create(user=user)

        token = Token.objects.create(user=user)

        url = reverse('v1-auth-password')
        data = {
            'username': 'fake@fake.com',
            'password': 'fake'
        }

        res = self.client.post(url, data=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json().get('token'), token.key)
        self.assertEqual(res.json().get('user'), user.id)

    def test_success_email_case_insensitive(self):
        """ should succeed for case insensitive email lookup """
        user = User.objects.create_user(
            username='fake',
            password='fake',
            email='fake@FAKE.com'
        )

        profile = Profile.objects.create(user=user)

        token = Token.objects.create(user=user)

        url = reverse('v1-auth-password')
        data = {
            'username': 'fake@fake.com',
            'password': 'fake'
        }

        res = self.client.post(url, data=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json().get('token'), token.key)
        self.assertEqual(res.json().get('user'), user.id)

    def test_user_found_by_username_valid_password(self):
        user = User.objects.create_user(
            username='FAke',
            password='fake',
        )

        profile = Profile.objects.create(user=user)

        token = Token.objects.create(user=user)

        url = reverse('v1-auth-password')
        data = {
            'username': 'fake',
            'password': 'fake'
        }

        res = self.client.post(url, data=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json().get('token'), token.key)

    @patch('core.auth.views.reset_password')
    def test_alpha_user(self, reset_func):
        user = User.objects.create_user(
            username='fake',
            password='fake',
            email='fake@fake.com'
        )

        profile = Profile.objects.create(user=user, is_alpha_user=True)

        data = {
            'username': 'fake',
            'password': 'fake'
        }

        url = reverse('v1-auth-password')
        res = self.client.post(url, data=data)
        self.assertEqual(reset_func.call_count, 1)
        self.assertEqual(reset_func.call_args[0][0], user)
        self.assertEqual(res.status_code, 418)


class PasswordRegistrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('v1-registration-password')

    def cleanUp(self):
        User.objects.delete()

    @patch('core.auth.views.check_user', side_effect=BadRequest('test'))
    def test_returns_exceptions(self, mock):
        """
        It should return the exception
        """
        data = {
            'username': 'test',
            'password': 'testpass',
            'email': 'test@test.com',
            'first_name': 'test',
            'last_name': 'test',
            'birthdate': '2011-11-03T18:21:26'
        }

        res = self.client.post(self.url, data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json(), {'detail': 'test'})

    @patch('core.helpers.create_mail_from_template')
    @patch('core.auth.views.check_user', return_value=True)
    def test_success(self, mock, mail):
        """
        Should create the user; mocks check_user because there is another test suite for that function
        """
        data = {
            'username': 'test',
            'password': 'testpass',
            'email': 'test@test.com',
            'first_name': 'test',
            'last_name': 'test',
            'birthdate': '2011-11-03T18:21:26',
        }

        res = self.client.post(self.url, data=data)
        self.assertEqual(res.status_code, 200)

        user = User.objects.get(email='test@test.com')
        self.assertEqual(user.username, 'test')
        self.assertEqual(user.check_password('testpass'), True)

        profile = user.profile
        self.assertEqual(profile.is_artist, False)
        self.assertEqual(profile.is_venue, False)
        self.assertEqual(profile.is_email_confirmed, False)
        self.assertTrue(profile.email_confirmation_token is not None)
        mock.assert_called_with('test', 'test@test.com')

        # mail.assert_called_with(
        #     recipient=user.email,
        #     subject='RedPine - Email Confirmation',
        #     template='mail/confirm_email.html',
        #     context={
        #         'confirmation_url': profile.get_email_confirmation_url
        #     }
        # )


class CheckUser(TestCase):
    """
    Tests the check_user function that is used by both PasswordRegistration and FacebookRegistration
    """
    def test_duplicate_username(self):
        """
        It should fail if the username submitted already exists in the database
        """
        user = User.objects.create_user(
            username='test',
            password='testpass',
            email='test@test.test'
        )

        with self.assertRaises(BadRequest):
            check_user('test', 'test@test.com')

    def test_case_insensitive_duplicate_username(self):
        """ should fail """
        user = User.objects.create_user(
            username='test',
            password='testpass',
            email='test@test.test'
        )

        with self.assertRaises(BadRequest):
            check_user('TEST', 'test@test.com')

    def test_duplicate_email(self):
        """
        It should fail if the email submitted already exists in the database
        """
        user = User.objects.create_user(
            username='test1',
            password='testpass',
            email='test@test.com'
        )

        with self.assertRaises(BadRequest):
            check_user('test2', 'test@test.com')

    def test_case_insensitive_duplicate_email(self):
        """ should fail """
        user = User.objects.create_user(
            username='test',
            password='testpass',
            email='test@test.test'
        )

        with self.assertRaises(BadRequest):
            check_user('test2', 'TEST@test.test')

    def test_success(self):
        check_user('test2', 'test@test.com')


class FacebookRegistrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch('facebook.facebook.FacebookClient.confirm')
    @patch('facebook.facebook.FacebookClient.get_email', side_effect=Exception())
    def test_facebook_registration_failure(self, confirm_patch, get_email_patch):
        """
        handles scenario where facebook calls fail
        """
        url = reverse('v1-registration-facebook')
        data = {
            'redirect_uri': 'http://fake.com',
            'code': 'fake',
            'username': 'fake',
            'first_name': 'first',
            'last_name': 'last'
        }

        res = self.client.post(url, data=data)
        data = res.json()
        
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data.get('detail'), 'Facebook authentication failed')

    @patch('secrets.token_hex', return_value='testpass')
    @patch('facebook.facebook.FacebookClient.confirm')
    @patch('facebook.facebook.FacebookClient.get_email', return_value='test@test.com')
    @patch('core.auth.views.check_user')
    def test_facebook_registration_success(self, check_user, get_email, confirm, token_hex):
        """
        handles scenario where facebook calls fail
        """
        url = reverse('v1-registration-facebook')
        data = {
            'redirect_uri': 'http://fake.com',
            'code': 'fake',
            'username': 'user',
            'first_name': 'first',
            'last_name': 'last'
        }

        res = self.client.post(url, data=data)
        data = res.json()
        check_user.assert_called_with('user', 'test@test.com')
        token_hex.assert_called_with(32)

        self.assertEqual(res.status_code, 200)

        user = User.objects.get(email='test@test.com')
        self.assertEqual(user.username, 'user')
        self.assertEqual(user.check_password('testpass'), True)

        profile = user.profile
        self.assertEqual(profile.is_artist, False)
        self.assertEqual(profile.is_venue, False)

    @patch('secrets.token_hex', return_value='testpass')
    @patch('facebook.facebook.FacebookClient.confirm')
    @patch('facebook.facebook.FacebookClient.get_email', return_value=None)
    @patch('core.auth.views.check_user')
    def test_facebook_registration_email_not_found(self, check_user, get_email, confirm, token_hex):
        """
        handles scenario where facebook calls fail
        """
        url = reverse('v1-registration-facebook')
        data = {
            'redirect_uri': 'http://fake.com',
            'code': 'fake',
            'username': 'user',
            'first_name': 'first',
            'last_name': 'last'
        }

        res = self.client.post(url, data=data)
        data = res.json()
        self.assertEqual(data.get('detail'), FacebookRegistrationView.email_not_found)


class ForgotPasswordTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_email_not_found(self):
        """ should return 200 and do nothing if the email is not found """
        data = { 'email': fake.email() }
        res = self.client.post('/v1/auth/forgot-password/', data=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {})

    @patch('core.helpers.create_mail_from_template')
    def test_email_found(self, mail):
        """ should return 200, set the password reset token, and send an email to the user if the email is found """
        email = fake.email()
        user = User.objects.create(email=email, username='user', password='password')
        profile = Profile.objects.create(user=user)
        data = { 'email': email }
        res = self.client.post('/v1/auth/forgot-password/', data=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {})

        p2 = Profile.objects.get(id=profile.id)
        self.assertNotEqual(p2.password_reset_token, None)

        mail.assert_called_with(
            recipient=user.email,
            subject='Reset Password',
            template='mail/reset_password.html',
            context={
                'url': p2.get_password_reset_url()
            }
        )


class ResetPasswordTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_user_not_found(self):
        """ should return 404 """
        data = {
            'email': fake.email(),
            'token': 'fake',
            'password': 'fake'
        }
        res = self.client.post('/v1/auth/reset-password/', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json(), {'detail': 'Password reset failed'})

    def test_code_doesnt_match(self):
        """ should return 404 """
        email = fake.email()
        user = User.objects.create(email=email, username='user', password='pass')
        profile = Profile.objects.create(user=user)
        data = {
            'email': email,
            'token': 'fake',
            'password': 'fake'
        }
        res = self.client.post('/v1/auth/reset-password/', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json(), {'detail': 'Password reset failed'})

    @patch('core.helpers.create_mail_from_template')
    def test_success(self, mail):
        """ should return 200, send an email, reset the user's password and scrub the reset code """
        email = fake.email()
        user = User.objects.create(email=email, username='user', password='pass')
        profile = Profile.objects.create(user=user, password_reset_token='fake')
        data = {
            'email': email,
            'token': 'fake',
            'password': 'fake'
        }
        res = self.client.post('/v1/auth/reset-password/', data=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {})

        mail.assert_called_with(
            recipient=user.email,
            subject='Password Successfully Reset',
            template='mail/reset_password_success.html',
            context={}
        )

        p2 = Profile.objects.get(id=profile.id)
        self.assertEqual(p2.password_reset_token, None)

        u2 = User.objects.get(id=user.id)
        self.assertTrue(u2.check_password('fake'))

    @patch('core.helpers.create_mail_from_template')
    def test_success_no_alpha(self, mail):
        email = fake.email()
        user = User.objects.create(email=email, username='user', password='pass')
        profile = Profile.objects.create(user=user, password_reset_token='fake', is_alpha_user=True)
        data = {
            'email': email,
            'token': 'fake',
            'password': 'fake'
        }
        res = self.client.post('/v1/auth/reset-password/', data=data)
        p2 = Profile.objects.get(pk=profile.id)
        self.assertFalse(p2.is_alpha_user)


class ConfirmEmailTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_user_not_found(self):
        """ should return 404 """
        data = {
            'email': fake.email(),
            'token': 'fake'
        }
        res = self.client.post('/v1/auth/confirm-email/', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json(), {'detail': 'Email confirmation failed'})

    def test_code_doesnt_match(self):
        """ should return 404 """
        email = fake.email()
        user = User.objects.create(email=email, username='user', password='pass')
        profile = Profile.objects.create(user=user)
        data = {
            'email': email,
            'token': 'fake'
        }
        res = self.client.post('/v1/auth/confirm-email/', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json(), {'detail': 'Email confirmation failed'})

    @patch('core.helpers.create_mail_from_template')
    def test_success(self, mail):
        """ should send an email, confirm the user's email and scrub the confirmation code """
        email = fake.email()
        user = User.objects.create(email=email, username='user', password='pass')
        profile = Profile.objects.create(user=user, email_confirmation_token='fake')
        data = {
            'email': email,
            'token': 'fake'
        }
        res = self.client.post('/v1/auth/confirm-email/', data=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {})

        mail.assert_called_with(
            recipient=user.email,
            subject='Email Confirmed',
            template='mail/confirm_email_success.html',
            context={}
        )

        p2 = Profile.objects.get(id=profile.id)
        self.assertEqual(p2.email_confirmation_token, None)
        self.assertEqual(p2.is_email_confirmed, True)


class LogoutTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = core.tests.helpers.build_user()
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        user2 = core.tests.helpers.build_user()
        Token.objects.create(user=user2)

    def test_destroys_token(self):
        token = Token.objects.get(user=self.user)
        res = self.client.post('/v1/auth/logout/')
        self.assertEqual(res.status_code, 200)
        tokens = Token.objects.all()
        self.assertEqual(len(tokens), 1)

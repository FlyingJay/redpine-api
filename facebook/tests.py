from django.test import TestCase
from unittest.mock import patch
from .facebook import *
import responses
import os
import re


FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID')
FACEBOOK_APP_SECRET = os.environ.get("FACEBOOK_APP_SECRET")

FACEBOOK_APP_ID = 'fake'
FACEBOOK_APP_SECRET = 'fake'


class FacebookClientTest(TestCase):
    """
    Facebook FacebookClient
    """

    def setUp(self):
        self.client = FacebookClient(FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)

    @responses.activate
    @patch('facebook.facebook.logger.error')
    def test_confirm_bad_response(self, err):
        """
        Should raise an exception when the request to get an access token fails
        """
        responses.add(
            responses.GET,
            re.compile(r'^{}'.format(FACEBOOK_OAUTH_BASE_URL)),
            json={},
            status=400
        )

        with self.assertRaises(FacebookException):
            self.client.confirm('fake', 'fake')

    @responses.activate
    @patch('facebook.facebook.logger.error')
    def test_confirm_bad_response_content(self, err):
        """
        Should raise an exception when the request to get an access token returns a body with
        no access token
        """
        responses.add(
            responses.GET,
            re.compile(r'^{}'.format(FACEBOOK_OAUTH_BASE_URL)),
            json={},
            status=200
        )

        with self.assertRaises(FacebookException):
            self.client.confirm('fake', 'fake')

    @responses.activate
    def test_confirm_success(self):
        """
        Should save the access_token after a successful code - access_token exchange
        """
        responses.add(
            responses.GET,
            re.compile(r'^{}'.format(FACEBOOK_OAUTH_BASE_URL)),
            json={'access_token': 'valid_token'},
            status=200
        )

        self.client.confirm('fake', 'fake')
        self.assertEqual(self.client.access_token, 'valid_token')

    @patch('facebook.facebook.logger.error')
    def test_get_email_no_access_token(self, logger):
        with self.assertRaises(FacebookException):
            self.client.get_email()

    @responses.activate
    @patch('facebook.facebook.logger.error')
    def test_get_email_bad_response(self, logger):
        """
        Should raise an exception when the request to get an email fails
        """
        responses.add(responses.GET, re.compile(r'^{}'.format(FACEBOOK_ME_URL)),
                      json={}, status=400)

        self.client.access_token = 'fake'

        with self.assertRaises(FacebookException):
            self.client.get_email()

    @patch('facebook.facebook.logger.error')
    @responses.activate
    def test_get_email_no_email(self, logger):
        """
        Should return None if the response doesn't have an email
        """
        responses.add(responses.GET, re.compile(r'^{}'.format(FACEBOOK_ME_URL)),
                      json={'wat': 'test'}, status=200)

        self.client.access_token = 'fake'
        self.assertEqual(self.client.get_email(), None)

    @responses.activate
    def test_get_email_success(self):
        """
        Should return the email after a successful request
        """
        responses.add(responses.GET, re.compile(r'{}'.format(FACEBOOK_ME_URL)),
                      json={'email': 'test@test.test'}, status=200)

        self.client.access_token = 'fake'
        self.assertEqual(self.client.get_email(), 'test@test.test')

    @responses.activate
    @patch('facebook.facebook.logger.error')
    @patch('facebook.facebook.logger.debug')
    def test_confirm_code_already_used(self, debug, error):
        data = {'error': {'code': 100}}
        responses.add(
            responses.GET,
            re.compile(r'^{}'.format(FACEBOOK_OAUTH_BASE_URL)),
            json=data,
            status=200
        )

        with self.assertRaises(FacebookException):
            self.client.confirm('fake', 'fake')

        self.assertEqual(debug.call_count, 1)
        self.assertEqual(error.call_count, 0)
        self.assertEqual(debug.call_args[0][0], data.get('error'))
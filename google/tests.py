from django.test import TestCase
from django.conf import settings
from unittest.mock import patch
from google import GoogleClient, GoogleClientFailureException, GoogleNoResultsException
from google.google import GEOCODING_BASE_URL, GEOCODING_STATUSES
import responses
import re


class GeocodingTest(TestCase):
    def setUp(self):
        self.client = GoogleClient('test_api_key')

    @responses.activate
    @patch('google.google.logger')
    def test_request_denied(self, logger):
        responses.add(
            responses.GET,
            re.compile(r'^{}'.format(GEOCODING_BASE_URL)),
            json={'status': GEOCODING_STATUSES.REQUEST_DENIED},
            status=200
        )

        with self.assertRaises(GoogleClientFailureException):
            self.client.geocode('test')

    @responses.activate
    @patch('google.google.logger')
    def test_unknown_error(self, logger):
        """ if the status code from google was not good, but we don't understand the response """
        responses.add(
            responses.GET,
            re.compile(r'^{}'.format(GEOCODING_BASE_URL)),
            json={},
            status=400
        )

        with self.assertRaises(GoogleClientFailureException):
            self.client.geocode('test')

    @responses.activate
    def test_no_results(self):
        """ if there are no results, throw a notfound exception """
        responses.add(
            responses.GET,
            re.compile(r'^{}'.format(GEOCODING_BASE_URL)),
            json={'status': GEOCODING_STATUSES.ZERO_RESULTS},
            status=200
        )

        with self.assertRaises(GoogleNoResultsException):
            self.client.geocode('test')

    @responses.activate
    def test_geocoding_address_only(self):
        responses.add(
            responses.GET,
            re.compile(r'^{}'.format(GEOCODING_BASE_URL)),
            json={
                'results': [
                    {
                        'geometry': {
                            'location': {
                                'lat': 1,
                                'lng': 2
                            }
                        }
                    }
                ],
                'status': GEOCODING_STATUSES.OK
            },
            status=200
        )
        result = self.client.geocode('123 test street')
        self.assertEqual(result.location.x, 1)
        self.assertEqual(result.location.y, 2)
        self.assertEqual(responses.calls[0].request.url, 'https://maps.googleapis.com/maps/api/geocode/json?address=123+test+street&key=test_api_key')

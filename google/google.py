from django.contrib.gis.geos import Point
import urllib.parse
import requests
import logging


logger = logging.getLogger('google')

GEOCODING_BASE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'

class GEOCODING_STATUSES:
    OK = 'OK'
    ZERO_RESULTS = 'ZERO_RESULTS'
    OVER_QUERY_LIMIT = 'OVER_QUERY_LIMIT'
    REQUEST_DENIED = 'REQUEST_DENIED'
    INVALID_REQUEST = 'INVALID_REQUEST'
    UNKNOWN_ERROR = 'UNKNOWN_ERROR'


class GoogleClientFailureException(Exception):
    """ we were unable to geocode """
    pass


class GoogleNoResultsException(Exception):
    """ no results found """
    pass


class GeocodingResult:
    def __init__(self, location):
        self.location = location


class GoogleClient:
    def __init__(self, api_key):
        self.api_key = api_key

    def geocode(self, address):
        query = {'address': address, 'key': self.api_key}
        res = requests.get(GEOCODING_BASE_URL, params=query)

        if res.status_code != 200:
            logger.error('received status code {} from google geocoding API, indicating an error'.format(res.status_code))
            raise GoogleClientFailureException()

        status = res.json().get('status')

        if status == GEOCODING_STATUSES.ZERO_RESULTS:
            raise GoogleNoResultsException()

        elif status != GEOCODING_STATUSES.OK:
            logger.error('received a non-OK status {} from google geocoding API'.format(status))
            raise GoogleClientFailureException()

        result = res.json().get('results')[0]
        geometry = result.get('geometry').get('location')
        location = Point(geometry.get('lat'), geometry.get('lng'), srid=4326)
        return GeocodingResult(location=location)
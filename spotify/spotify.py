import requests
import logging
import json
import base64
import six
from .models import *
from datetime import datetime, timedelta

logger = logging.getLogger('spotify')


class SpotifyException(Exception):
    pass


class SpotifyClient:
    AUTH_URL = 'https://accounts.spotify.com/api/token'

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorization = base64.b64encode(six.text_type(self.client_id + ':' + self.client_secret).encode('ascii')).decode('ascii')

    def login(self, code, redirect_uri):
        headers = {
            'Authorization': 'Basic %s' % self.authorization
            }

        data  = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri
            }

        try:
            response = requests.post(self.AUTH_URL, data=data, headers=headers)
            response_dict = response.json()

            if response.status_code != 200:
                raise SpotifyException(response_dict)

            access_token = response_dict['access_token']
            refresh_token = response_dict['refresh_token']
            expiration_date = datetime.now() + timedelta(seconds=response_dict['expires_in'])

            connection = SpotifyConnection.objects.create(
                access_token=access_token,
                refresh_token=refresh_token,
                expiration_date=expiration_date
            )
            return connection

        except Exception as e:
            raise e

    def refresh(self, connection):
        if connection.expiration_date > (datetime.now() + timedelta(minutes=5)):
            return connection
        else:
            headers = {
                'Authorization': 'Basic %s' % self.authorization
                }

            data  = {
                'grant_type' : 'refresh_token',
                'refresh_token' : connection.refresh_token
                }

            try:
                response = requests.post(self.AUTH_URL, data=data, headers=headers)
                response_dict = response.json()

                if response.status_code != 200:
                    raise SpotifyException(response_dict)

                connection.access_token = response_dict['access_token']
                connection.expiration_date = datetime.now() + timedelta(seconds=response_dict['expires_in'])
                connection.refresh_token = response_dict.get('refresh_token', connection.refresh_token)

                connection.save()
                return connection
            
            except Exception as e:
                raise e
import requests
import logging


logger = logging.getLogger('facebook')


FACEBOOK_GRAPH_BASE_URL = 'https://graph.facebook.com/v2.9'
FACEBOOK_OAUTH_BASE_URL = '{}/oauth/access_token'.format(FACEBOOK_GRAPH_BASE_URL)
FACEBOOK_ME_URL = '{}/me'.format(FACEBOOK_GRAPH_BASE_URL)


class FacebookException(Exception):
    pass


class FacebookClient:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def confirm(self, redirect_uri, code):
        def check_error(res):
            should_raise = False

            try:
                data = res.json()

                if 'error' in data:
                    error = data.get('error', {})

                    if 'fbtrace_id' in error:
                        error.pop('fbtrace_id')

                    error_code = error.get('code')

                    if error_code == 100:
                        # authorization code has already been used
                        logger.debug(error)

                    else:
                        logger.error(error)

                    should_raise = True

            except:
                pass

            if should_raise:
                raise FacebookException()

        try:
            params = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': redirect_uri,
                'code': code
            }

            res = requests.get(FACEBOOK_OAUTH_BASE_URL, params=params)
            res.raise_for_status()
            check_error(res)
            data = res.json()
            self.access_token = data.get('access_token')

        except FacebookException as e:
            raise e

        except Exception as e:
            check_error(res)
            logger.error(e)
            raise(FacebookException())

    def get_email(self):
        try:
            self.access_token

            params = {
                'access_token': self.access_token,
                'fields': 'email'
            }
            res = requests.get(FACEBOOK_ME_URL, params=params)
            res.raise_for_status()
            data = res.json()
            email = data.get('email', None)
            return email

        except Exception as e:
            logger.error(e)
            raise(FacebookException())
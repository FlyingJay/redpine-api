from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.utils.html import mark_safe
from .exceptions import *
import stripe
import logging
import json


logger = logging.getLogger('stripe')
stripe.api_key = settings.STRIPE_SECRET_KEY

STRIPE_BASE_URL = 'https://dashboard.stripe.com/{}'.format('test' if settings.STRIPE_TEST_MODE else 'live') # not sure if this should actually be "live" in live mode


class CustomerManager(models.Manager):
    def create_customer(self, email=None, token=None):
        try:
            res = stripe.Customer.create(
                email=email,
                source=token
            )

            return self.create(stripe_id=res.get('id'), email=email)

        except stripe.error.CardError as e:
            raise InvalidCardException()

        except stripe.error.InvalidRequestError as e:
            if e.param == 'source':
                raise InvalidTokenException()

            else:
                logger.error('Customer creation request failed for param `{}`: {}'.format(e.param, str(e)))
                raise InternalException()

        except stripe.error.AuthenticationError:
            logger.error('Stripe API key is improperly configured')
            raise InternalException()

        except Exception as e:
            type_details = type(e)
            logger.error('There was an unhandled Stripe error of type {}.{}: {}'.format(type_details.__module__, type_details.__name__, str(e)))
            raise InternalException()


class Charge(models.Model):
    customer = models.ForeignKey('Customer', related_name='charges')
    amount = models.IntegerField()
    currency = models.CharField(max_length=10)
    metadata = JSONField(default='{}', null=True, blank=True)
    success = models.BooleanField(default=True)
    stripe_id = models.CharField(max_length=100, help_text='The Stripe Charge object\'s ID', default='', null=True, blank=True)
    stripe_response = JSONField(default='{}', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return ''

    def stripe_anchor(self):
        """ This is used for adding a link in the admin panel """
        url = '{}/charges/{}'.format(STRIPE_BASE_URL, self.stripe_id)
        return mark_safe('<a href="{}" target="_blank">View in Stripe</a>'.format(url))

    def debug_charge(self):
        """ This is used to check the charge JSON """
        res = json.dumps(self.stripe_response)
        html = """
        <a href="javascript:document.getElementById('debug-charge-{id}').setAttribute('style', '')">Debug Charge</a>
        <textarea id="debug-charge-{id}" style="display:none">{res}</textarea>
        """.format(id=self.id, res=res)

        return mark_safe(html)


class Customer(models.Model):
    stripe_id = models.CharField(max_length=100, help_text="The Stripe Customer object's ID")
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = CustomerManager()

    def __str__(self):
        return self.email

    def stripe_anchor(self):
        """ This is used for adding a link in the admin panel """
        url = '{}/customers/{}'.format(STRIPE_BASE_URL, self.stripe_id)
        return mark_safe('<a href="{}" target="_blank">View in Stripe</a>'.format(url))

    def charge(self, amount=None, currency=None, metadata='{}'):
        charge = Charge(
            customer=self,
            amount=amount,
            currency=currency,
            metadata=metadata,
        )

        try:
            res = stripe.Charge.create(
                customer=self.stripe_id,
                amount=amount,
                currency=currency,
                metadata=metadata
            )

            charge.stripe_id = res.get('id', None)
            charge.stripe_response = res
            charge.save()

            if charge.stripe_id is None:
                logger.warning('failed to parse stripe charge id from successful stripe response (charge id {})'.format(charge.id))

        except stripe.error.CardError as e:
            charge.stripe_response = e.json_body
            charge.success = False
            body = e.json_body
            charge.stripe_id = body.get('error', {}).get('charge', None)
            charge.save()

            if charge.stripe_id is None:
                logger.warning('failed to parse stripe charge id from charge carderror response (charge id {})'.format(charge.id))

            raise ChargeFailureException()

        except stripe.error.AuthenticationError:
            logger.error('Stripe API key is improperly configured')
            raise InternalException()

        except Exception as e:
            charge.stripe_response = e.json_body
            charge.success = False
            charge.save()
            type_details = type(e)
            logger.error('there was an unhandled stripe error of type {}.{} for charge {}: {}'.format(type_details.__module__, type_details.__name__, charge.id, str(e)))
            raise InternalException()
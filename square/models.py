from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.utils.html import mark_safe
from django.core.validators import MinValueValidator, MaxValueValidator
from .exceptions import *
import logging
import json
import uuid
import requests

import squareconnect
from squareconnect.models import Money
from squareconnect.apis.locations_api import LocationsApi
from squareconnect.apis.customers_api import CustomersApi
from squareconnect.apis.transactions_api import TransactionsApi
from squareconnect.rest import ApiException


logger = logging.getLogger('square')

#STRIPE_BASE_URL = 'https://dashboard.stripe.com/{}'.format('test' if settings.STRIPE_TEST_MODE else 'live') # not sure if this should actually be "live" in live mode
SQUARE_BASE_URL = 'https://squareup.com/dashboard'

class CustomerManager(models.Manager):
    def create_customer(self, email=None, token=None):
        try:
            square_customers = CustomersApi()
            square_customers.api_client.configuration.access_token = settings.SQUARE_ACCESS_TOKEN

            customer_res = square_customers.create_customer({
                'email_address': email
            })

            customer = self.create(
                square_id=customer_res.customer.id, 
                email=email
            )

            try:
                card_res = square_customers.create_customer_card(customer_res.customer.id,{
                    'card_nonce': token
                })

                Card.objects.create(
                    square_id=card_res.card.id, 
                    customer=customer,
                    brand=card_res.card.card_brand,
                    exp_month=card_res.card.exp_month,
                    exp_year=card_res.card.exp_year
                )

            except ApiException as e:
                logger.error('Exception creating customer card:' + str(e))

            return customer

        except ApiException as e:
            logger.error('Exception creating customer:' + str(e))

        except Exception as e:
            type_details = type(e)
            logger.error('There was an unhandled Square error of type {}.{}: {}'.format(type_details.__module__, type_details.__name__, str(e)))
            raise InternalException()


class Customer(models.Model):
    square_id = models.CharField(max_length=100, help_text="The Square Customer object's ID")
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = CustomerManager()

    def __str__(self):
        return self.email

    def square_anchor(self):
        """ This is used for adding a link in the admin panel """
        url = '{}/customers/{}'.format(SQUARE_BASE_URL, self.square_id)
        return mark_safe('<a href="{}" target="_blank">View in Square</a>'.format(url))

    def charge(self, amount=None, currency=None, metadata='', app='RedPine'):
        charge = Charge(
            customer=self,
            amount=amount,
            currency=currency,
            metadata=metadata,
            success=False
        )
        #Get exchange rates... Square charges must use CAD.
        if currency == 'CAD':
            amount_CAD = amount
        else: 
            exchange_rates_url = 'https://api.exchangerate-api.com/v4/latest/{}'.format(currency)
            exchange_rates_response = requests.get(exchange_rates_url)
            exchange_rates = exchange_rates_response.json()

            if 'error' in exchange_rates:
                logger.error(exchange_rates['error'])
                raise ExchangeRateException()

            amount_CAD = round(amount * exchange_rates['rates']['CAD'])
            charge.exchange_rate = exchange_rates['rates']['CAD']

        try:
            if self.cards.count() == 0:
                raise NoCustomerCardException()

            card = self.cards.first()

            square_locations = LocationsApi()
            square_locations.api_client.configuration.access_token = settings.SQUARE_ACCESS_TOKEN

            locations_res = square_locations.list_locations()
            locations = locations_res.locations

            if len(locations) == 0:
                raise NoLocationsException()

            if app == 'inConcert':
                app_location = next((location for location in locations if location.name == 'inConcert'), None)
            else:
                if currency == 'USD':
                    app_location = next((location for location in locations if location.name == 'RedPine USA'), None)
                else:
                    app_location = next((location for location in locations if location.name == 'RedPine HQ'), None)

            #
            if app_location is None:
                app_location = locations[0]

            square_transactions = TransactionsApi() 
            square_transactions.api_client.configuration.access_token = settings.SQUARE_ACCESS_TOKEN

            charge_res = square_transactions.charge(app_location.id,{
                'buyer_email_address': self.email,
                'customer_id': self.square_id,
                'customer_card_id': card.square_id,
                'amount_money': Money(amount=amount_CAD, currency='CAD'),
                'note': json.dumps(metadata),
                'idempotency_key': str(uuid.uuid1())
            })

            charge.square_id = charge_res.transaction.id
            charge.square_response = json.dumps(charge_res, default=lambda o: o.__dict__, sort_keys=True)
            charge.success = True
            charge.save()

        except ApiException as e:
            logger.error('Exception charging customer card:' + str(e))
            raise ChargeFailureException()

        except Exception as e:
            type_details = type(e)
            logger.error('There was an unhandled error of type {}.{}: {}'.format(type_details.__module__, type_details.__name__, str(e)))
            raise ChargeFailureException()


class Card(models.Model):
    customer = models.ForeignKey('Customer', related_name='cards')
    square_id = models.CharField(max_length=100, help_text="The Square Card object's ID")
    brand = models.CharField(max_length=50, null=True, default=None)
    exp_month = models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(12)], null=True, default=None)
    exp_year = models.IntegerField(null=True, default=None)


class Charge(models.Model):
    customer = models.ForeignKey('Customer', related_name='charges')
    amount = models.IntegerField()
    currency = models.CharField(max_length=10)
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, default=1.000000)
    metadata = JSONField(default='{}', null=True, blank=True)
    success = models.BooleanField(default=True)
    square_id = models.CharField(max_length=100, help_text='The Square Charge object\'s ID', default='', null=True, blank=True)
    square_response = JSONField(default='{}', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return ''

    def square_anchor(self):
        """ This is used for adding a link in the admin panel """
        url = '{}/sales/transactions'.format(SQUARE_BASE_URL)
        return mark_safe('<a href="{}" target="_blank">View in Square</a>'.format(url))

    def debug_charge(self):
        """ This is used to check the charge JSON """
        res = json.dumps(self.square_response)
        html = """
        <a href="javascript:document.getElementById('debug-charge-{id}').setAttribute('style', '')">Debug Charge</a>
        <textarea id="debug-charge-{id}" style="display:none">{res}</textarea>
        """.format(id=self.id, res=res)

        return mark_safe(html)

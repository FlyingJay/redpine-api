from django.test import TestCase
from django.test.utils import override_settings
from unittest.mock import patch
from .models import *
from .exceptions import *
import stripe


class MockStripeException(Exception):
    def __init__(self, message, json_body={}):
        self.message = message
        self.json_body = json_body

    def __str__(self):
        return self.message


class CustomerTest(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        Customer.objects.all().delete()

    @patch('stripper.models.logger.error')
    @patch('stripe.Customer.create', side_effect=stripe.error.AuthenticationError)
    def test_create_customer_bad_api_key(self, create_func, err_func):
        """
        The Stripe logger should notify that Stripe API key is invalid
        """
        with self.assertRaises(InternalException):
            customer = Customer.objects.create_customer(email='fake', token='bad_token')

        self.assertEqual(err_func.call_count, 1)
        err_func.assert_called_with('Stripe API key is improperly configured')

    @patch('stripe.Customer.create', side_effect=stripe.error.InvalidRequestError('err', 'source'))
    def test_create_customer_invalid_token(self, create_func):
        """
        Should handle an invalid token and raise an exception (for the user of this package to deal with)
        """
        with self.assertRaises(InvalidTokenException):
            Customer.objects.create_customer(email='fake', token='bad token')

    @patch('stripper.models.logger.error')
    @patch('stripe.Customer.create', side_effect=stripe.error.InvalidRequestError('err', 'unknown'))
    def test_create_customer_unknown_invalid_request(self, create_func, err_func):
        """
        Should log the error if there is an unknown InvalidRequestError
        """
        with self.assertRaises(InternalException):
            Customer.objects.create_customer(email='fake', token='bad token')

        err_func.assert_called_with('Customer creation request failed for param `unknown`: err')

    @patch('stripe.Customer.create', side_effect=stripe.error.CardError('card was declined', 'wat', 'wat'))
    def test_create_customer_card_declined(self, create_func=None):
        """ Should handle card declined.. """

        with self.assertRaises(InvalidCardException):
            Customer.objects.create_customer(email='fake', token='tok_chargeDeclined')

    @patch('stripe.Customer.create', return_value={'id': 'cust_id'})
    def test_create_customer_success(self, create_func):
        """
        Should create the customer on success.  It's also important that the model can handle a character-based ID..
        """
        customer = Customer.objects.create_customer(email='fake', token='valid_token')
        self.assertEqual(customer.stripe_id, 'cust_id')

        db_loaded = Customer.objects.get(stripe_id='cust_id')
        self.assertEqual(db_loaded.id, customer.id)
        self.assertEqual(db_loaded.email, 'fake')

    @patch('stripper.models.logger.error')
    @patch('stripe.Customer.create', side_effect=InvalidTokenException('wat'))
    def test_create_customer_unknown_exception(self, create_func, err_func):
        """
        Should log an unknown exception with as much detail as possible
        """
        with self.assertRaises(InternalException):
            Customer.objects.create_customer(email='fake', token='fake')

        err_func.assert_called_with('There was an unhandled Stripe error of type stripper.exceptions.InvalidTokenException: wat')

    @patch('stripe.Charge.create', side_effect=stripe.error.CardError('card was declined', 'wat', 'wat', json_body={'error': {'charge': 'charge_id'}}))
    @patch('stripe.Customer.create', return_value={'id': 'cust_id'})
    def test_charge_customer_fails(self, cust_func, create_func):
        customer = Customer.objects.create_customer(email='testuser@test.com', token='tok_chargeCustomerFail')

        with self.assertRaises(ChargeFailureException):
            customer.charge(amount=2000, currency='usd')

        charge = customer.charges.first()
        self.assertEqual(charge.success, False)
        self.assertEqual(charge.stripe_response, {'error': {'charge': 'charge_id'}})
        self.assertEqual(charge.stripe_id, 'charge_id')

    @patch('stripper.models.logger.warning')
    @patch('stripe.Charge.create', side_effect=stripe.error.CardError('card was declined', 'wat', 'wat', json_body={}))
    @patch('stripe.Customer.create', return_value={'id': 'cust_id'})
    def test_charge_customer_fails_cant_parse_charge_id_no_err_in_body(self, cust_func, create_func, warning_func):
        """ We should be logging a warning if we're not able to parse the charge ID from the response """

        customer = Customer.objects.create_customer(email='testuser@test.com', token='tok_chargeCustomerFail')

        with self.assertRaises(ChargeFailureException):
            customer.charge(amount=2000, currency='usd')

        charge = customer.charges.first()
        self.assertEqual(charge.stripe_id, None)

        warning_func.assert_called_with('failed to parse stripe charge id from charge carderror response (charge id {})'.format(charge.id))

    @patch('stripper.models.logger.warning')
    @patch('stripe.Charge.create', side_effect=stripe.error.CardError('card was declined', 'wat', 'wat', json_body={'error': {}}))
    @patch('stripe.Customer.create', return_value={'id': 'cust_id'})
    def test_charge_customer_fails_cant_parse_charge_id_no_charge_id_in_err(self, cust_func, create_func, warning_func):
        """ We should be logging a warning if we're not able to parse the charge ID from the response """

        customer = Customer.objects.create_customer(email='testuser@test.com', token='tok_chargeCustomerFail')

        with self.assertRaises(ChargeFailureException):
            customer.charge(amount=2000, currency='usd')

        charge = customer.charges.first()
        self.assertEqual(charge.stripe_id, None)

        warning_func.assert_called_with('failed to parse stripe charge id from charge carderror response (charge id {})'.format(charge.id))

    @patch('stripe.Charge.create', return_value={'id': 'charge_id'})
    @patch('stripe.Customer.create', return_value={'id': 'cust_id'})
    def test_charge_customer_success(self, cust_func=None, create_func=None):
        customer = Customer.objects.create_customer(email='testuser@test.com', token='tok_visa')
        customer.charge(amount=2000, currency='usd')
        charge = customer.charges.first()
        self.assertEqual(charge.stripe_id, 'charge_id')
        self.assertEqual(charge.stripe_response, {'id': 'charge_id'})

    @patch('stripper.models.logger.warning')
    @patch('stripe.Charge.create', return_value={})
    @patch('stripe.Customer.create', return_value={'id': 'cust_id'})
    def test_charge_customer_success_without_id(self, cust_func=None, create_func=None, warning_func=None):
        """ If we weren't able to parse the charge ID from stripe's response, a warning should be logged """

        customer = Customer.objects.create_customer(email='testuser@test.com', token='tok_visa')
        customer.charge(amount=2000, currency='usd')
        charge = customer.charges.first()
        warning_func.assert_called_with('failed to parse stripe charge id from successful stripe response (charge id {})'.format(charge.id))

    @patch('stripper.models.logger.error')
    @patch('stripe.Charge.create', side_effect=MockStripeException('wat', json_body={'error': {}}))
    @patch('stripe.Customer.create', return_value={'id': 'cust_id'})
    def test_charge_customer_unknown_exception(self, cust_func=None, create_func=None, error_func=None):
        """ If we weren't able to handle the exception that was thrown, an error should be logged """

        customer = Customer.objects.create_customer(email='testwat@test.com', token='tok_visa')

        with self.assertRaises(InternalException):
            customer.charge(amount=2000, currency='usd')

        charge = customer.charges.first()
        error_func.assert_called_with('there was an unhandled stripe error of type stripper.tests.MockStripeException for charge {}: wat'.format(charge.id))
        self.assertEqual(charge.success, False)
        self.assertEqual(charge.stripe_response, {'error': {}})

    @patch('stripper.models.logger.error')
    @patch('stripe.Charge.create', side_effect=stripe.error.AuthenticationError)
    @patch('stripe.Customer.create', return_value={'id': 'cust_id'})
    def test_charge_customer_bad_authentication(self, cust_func=None, create_func=None, error_func=None):
        """ Should handle invalid Stripe API key """

        customer = Customer.objects.create_customer(email='testwat@test.com', token='tok_visa')

        with self.assertRaises(InternalException):
            customer.charge(amount=2000, currency='usd')

        error_func.assert_called_with('Stripe API key is improperly configured')
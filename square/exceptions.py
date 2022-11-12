class InvalidTokenException(Exception):
    """ This exception is thrown when an invalid token is passed to Square. """
    pass

class InternalException(Exception):
    """ This is an exception that is likely OUR FAULT. """
    pass

class ChargeFailureException(Exception):
    """ A attempted to charge a customer failed """
    pass

class InvalidCardException(Exception):
    """ Attempted to create a customer using a token representing an invalid card """
    pass

class NoLocationsException(Exception):
    """ Square was unable to return any business locations for RedPine. """
    pass

class NoCustomerCardException(Exception):
    """ We do not have a card saved for the user. Square may still have the info. """
    pass

class ExchangeRateException(Exception):
    """ An error occurred while trying to convert currencies. https://www.exchangerate-api.com/docs/documentation """
    pass
class InvalidTokenException(Exception):
    """ This exception is thrown when an invalid token is passed to Stripe. """
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
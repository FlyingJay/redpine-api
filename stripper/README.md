# Functionality

1. A customer object which can be created with an email & a stripe token.  When created via `Customer.objects.create_customer(email='email', token='token')`, the relevant Customer object will be created in Stripe (unless errors are thrown).

2. A charge object, which can be created via `customer.charge(amount=2000, currency='usd')`.  When created, the relevant Charge object will be created in Stripe.

3. Admin views.  Browse customers by email address; view all charges associated with a customer; click a link to view the customer or charge in Stripe; view original JSON response from Charge request (for debugging purposes).

# Error Scenarios

Error handling has been implemented for the following scenarios:

1. When creating a customer, if the token used represents an invalid card then a `stripper.exceptions.InvalidCardException` will be raised.

2. When creating a customer, if the token used was not found in Stripe, then a `stripper.exceptions.InvalidTokenException` will be raised.

3. When creating a charge, if there is an error charging the card then a `stripper.exceptions.ChargeFailureException` will be raised.

4. When creating a charge or a customer, if there is an API key error or any unrecognized Stripe response then a `stripper.exceptions.InternalException` will be raised and `stripper.models.logger.error` will be called appropriately.
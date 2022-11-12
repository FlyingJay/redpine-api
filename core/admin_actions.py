import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str
from core import models
from datetime import datetime, timedelta
from decimal import Decimal
from core import tasks

"""
modelAdmin -> current Model, sometimes used for Meta properties
request -> haven't needed it yet (permissions?)
queryset -> the set of model records on which to apply the action
"""
def refresh_subscription(modelAdmin, request, queryset):
	for subscription in queryset:
	    account_subscription = models.AccountSubscription.objects.get(pk=subscription.id)

	    new_account_subscription = models.AccountSubscription.objects.create(
	        user=account_subscription.user,
	        square_customer=account_subscription.square_customer,
	        account_type=account_subscription.account_type,
	        product_name=account_subscription.product_name,
	        amount=account_subscription.amount
	        )

	    amount = int(account_subscription.amount * Decimal(100.00))
	    metadata = 'U'+str(account_subscription.user.id)+' '+account_subscription.account_type+'-'+account_subscription.product_name
	    
	    new_account_subscription.square_customer.charge(
	        amount=amount, 
	        currency='CAD',#Expand to multi-currency (at least USA) soon. 
	        metadata=metadata
	    )

	    account_subscription.is_cancelled = True
	    account_subscription.save()    

	    new_account_subscription.is_processed = True
	    new_account_subscription.save()
	    
	    today = datetime.now()
	    renewal_date = today + timedelta(days=30)
	    tasks.renew_subscription(new_account_subscription.pk, schedule=renewal_date)
refresh_subscription.short_description = u"Refresh Subscription(s)"

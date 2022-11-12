from background_task import background
from inconcert import models, exceptions


@background(schedule=0)
def renew_subscription(subscription_id):
	subscription = models.Subscription.objects.get(pk=subscription_id)
	subscription.user.inconcert_profile.premium_months -= 1
	subscription.user.inconcert_profile.save()

	if subscription.is_cancelled:
		return

	new_subscription = None
	if subscription.user.inconcert_profile.premium_months == 0:
		try:
			new_subscription = models.Subscription.objects.create(
				user=subscription.user,
				square_customer=subscription.square_customer
			)
			try:
				new_subscription.square_customer.charge(
					amount=999, #9.99
					currency='CAD',#Expand to multi-currency (at least USA) soon. 
					metadata='U'+str(subscription.user.id)+' inconcert subscription',
					app='inConcert'
				)
				new_subscription.is_processed = True
				new_subscription.save()
			except:
				new_subscription.is_processing_failed = True
				new_subscription.save()
				raise

			subscription.is_cancelled = True
			subscription.save()    

			new_subscription.user.inconcert_profile.premium_months += 1
			new_subscription.user.inconcert_profile.save()

			renewal_date = datetime.now() + timedelta(days=30)
			renew_subscription(new_subscription.pk, schedule=renewal_date)

		except Exception as e:
			if not subscription.is_processing_failed and new_subscription is None:
				subscription.is_processing_failed = True
				subscription.is_cancelled = True
				subscription.save()
			print(e)
			pass
	else:
		renewal_date = datetime.now() + timedelta(days=30)
		renew_subscription(subscription.pk, schedule=renewal_date)
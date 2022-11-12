from django.conf import settings
from django.db.models import Q
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from core import models, helpers
from decimal import Decimal
"""
MAIL TEMPLATE API

Parameters for templates are a recipient email and a JSON object with any queried data to be shown.
If an object's id value is passed instead of the object itself, then the data will be retrieved.

When sending mail from internal tasks, we often already have queried for the data we want and do not need to query again for it.
But, we want to be able to easily send templated emails manually which match those our API sends.

Merging both functions guarantees equivalence between emails, regardless of sending method and provides a 1-line mail sending interface:

  Passing Data
  mail.act_show_invite('some@email.ca',{'join_token':'AAW4FD76DS'})

  Passing IDs
  mail.new_feed_message('some@email.ca',{'user':1022,'campaign':1})

"""
def act_signup(email,data):
	user = data.get('user')

	if isinstance(user, int):
		user = User.objects.get(pk=user)

	helpers.create_mail_from_template(
		recipient=email,
		subject='Thanks for signing up!',
		template='mail/artist_signup.html',
		context={
			'user': user,
			'play_show_url': settings.REDPINE_WEBAPP_URLS['PLAY_SHOW']
		}
	)

#Play a Show "your request was submitted" confirmation
def booking_recieved(email,data):
	user = data.get('user')

	if isinstance(user, int):
		user = User.objects.get(pk=user)

	helpers.create_mail_from_template(
		recipient=email,
		subject='Your booking request has been received',
		template='mail/Booking_Received.html',
		context={
			'user' : user
		   }
	  )

def act_show_invite(email,data):
	join_token = data.get('join_token', None)
	campaign = data.get('campaign')

	if isinstance(campaign, int):
		campaign = models.Campaign.objects.get(pk=campaign)

	headliner = models.CampaignBand.objects.filter(campaign=campaign.id,is_headliner=True).first()
	headliner_name = ''
	if headliner:
		headliner_name = headliner.band.name

	link = settings.REDPINE_WEBAPP_URLS['SHOW_HUB'](campaign.id)
	if join_token:
		link = settings.REDPINE_WEBAPP_URLS['REGISTER_WITH_ACT'](email,join_token)

	helpers.create_mail_from_template(
		recipient=email,
		subject='You\'ve been invited to play a show!',
		template='mail/act_invited_to_show.html',
		context={
			'callback_link': link,
			'headliner': headliner_name
		}
	)

def open_lineup_request_submitted(email,data):
	campaign = data.get('campaign')

	if isinstance(campaign, int):
		campaign = models.Campaign.objects.get(pk=campaign)

	helpers.create_mail_from_template(
		recipient=email,
		subject='You have requested to join {}'.format(campaign.title),
		template='mail/OpenLineup_Applicant_submitted_request.html',
		context={
			'campaign': campaign,
			'feed_url': settings.REDPINE_WEBAPP_URLS['SHOW_HUB'](campaign.id)
		}
	)

def open_lineup_request_recieved(email,data):
	band = data.get('band')
	campaign = data.get('campaign')

	if isinstance(band, int):
		band = Band.objects.get(pk=band)
	if isinstance(campaign, int):
		campaign = models.Campaign.objects.get(pk=campaign)

	helpers.create_mail_from_template(
		recipient=email,
		subject='{} is requesting to join {}'.format(band.name,campaign.title),
		template='mail/OpenLineup_Organizer_got_request.html',
		context={
			'band': band,
			'campaign': campaign,
			'feed_url': settings.REDPINE_WEBAPP_URLS['SHOW_HUB'](campaign.id)
		}
	)

def open_lineup_act_accepted(email,data):
	band = data.get('band')
	campaign = data.get('campaign')

	if isinstance(band, int):
		band = Band.objects.get(pk=band)
	if isinstance(campaign, int):
		campaign = models.Campaign.objects.get(pk=campaign)

	helpers.create_mail_from_template(
		recipient=email,
		subject='Your application was accepted!',
		template='mail/OpenLineup_Act_Accepted.html',
		context={
			'band': band,
			'campaign': campaign,
			'feed_url': settings.REDPINE_WEBAPP_URLS['SHOW_HUB'](campaign.id)
		}
	)

def open_lineup_act_rejected(email,data):
	band = data.get('band')
	campaign = data.get('campaign')

	if isinstance(band, int):
		band = Band.objects.get(pk=band)
	if isinstance(campaign, int):
		campaign = models.Campaign.objects.get(pk=campaign)

	helpers.create_mail_from_template(
		recipient=email,
		subject='Your application was declined.',
		template='mail/OpenLineup_Act_Rejected.html',
		context={
			'band': band,
			'campaign': campaign,
			'browse_open_lineups_url': settings.REDPINE_WEBAPP_URLS['SEARCH_OPEN_LINEUPS']('')
		}
	)

def new_feed_message(email,data):
	user = data.get('user')
	campaign = data.get('campaign')

	if isinstance(user, int):
		user = User.objects.get(pk=user)
	if isinstance(campaign, int):
		campaign = models.Campaign.objects.get(pk=campaign)

	helpers.create_mail_from_template(
		recipient=email,
		subject='You have new chat messages for {}'.format(campaign.title),
		template='mail/new_feed_messages.html',
		context={
			'user': user,
			'campaign': campaign,
			'shows_url': settings.REDPINE_WEBAPP_URLS['SHOWS'],
			'feed_url': settings.REDPINE_WEBAPP_URLS['SHOW_HUB'](campaign.id)
		}
	)

def booking_request_on_venue_hold(email,data):
	user = data.get('user')
	campaign = data.get('campaign')

	if isinstance(user, int):
		user = User.objects.get(pk=user)
	if isinstance(campaign, int):
		campaign = models.Campaign.objects.get(pk=campaign)

	venue = None
	if campaign.timeslot:
		venue = campaign.timeslot.venue

	helpers.create_mail_from_template(
		recipient=email,
		subject='Your date has been held',
		template='mail/booking_request_on_venue_hold.html',
		context={
			'user'     : user,
			'campaign' : campaign,
			'venue'	   : venue,
			'feed_url' : settings.REDPINE_WEBAPP_URLS['SHOW_HUB'](campaign.id)
		}
	)

def booking_request_internally_approved(email,data):
	user = data.get('user')
	campaign = data.get('campaign')

	if isinstance(user, int):
		user = User.objects.get(pk=user)
	if isinstance(campaign, int):
		campaign = models.Campaign.objects.get(pk=campaign)

	venue = None
	if campaign.timeslot:
		venue = campaign.timeslot.venue

	helpers.create_mail_from_template(
		recipient=email,
		subject='Your request has been sent to the venue',
		template='mail/Booking_Request_Internally_Approved.html',
		context={
			'user'     : user,
			'campaign' : campaign,
			'venue'	   : venue,
			'feed_url' : settings.REDPINE_WEBAPP_URLS['SHOW_HUB'](campaign.id)
		}
	)

def promotion_reminder(email,data):
	campaign = data.get('campaign')

	if isinstance(campaign, int):
		campaign = models.Campaign.objects.get(pk=campaign)

	helpers.create_mail_from_template(
		recipient=email,
		subject='Time to start promoting your show!',
		template='mail/Accepted_Show_(2 A.B)_Time_to_Promote.html',
		context={
			'feed_url' : settings.REDPINE_WEBAPP_URLS['SHOW_HUB'](campaign.id)
		}
	)

def one_month_reminder(email,data):
	campaign = data.get('campaign')
	venue = data.get('venue')

	if isinstance(campaign, int):
		campaign = models.Campaign.objects.get(pk=campaign)
	if isinstance(venue, int):
		venue = User.objects.get(pk=venue)

	helpers.create_mail_from_template(
		recipient=email,
		subject='Easy ways to stay on top of your show',
		template='mail/Accepted_Show (30 B.S.) - Checklist_Reminder.html',
		context={
			'feed_url' : settings.REDPINE_WEBAPP_URLS['SHOW_HUB'](campaign.id),
			'venue' : venue
		   }
	)

def one_week_reminder(email,data):
	campaign = data.get('campaign')
	venue = data.get('venue')

	if isinstance(campaign, int):
		campaign = models.Campaign.objects.get(pk=campaign)
	if isinstance(venue, int):
		venue = User.objects.get(pk=venue)

	helpers.create_mail_from_template(
		recipient=email,
		subject='Your show is in a week. Are you ready?',
		template='mail/Accepted_Show (7 B.S.) - Checklist_Reminder_2.html',
		context={
			'feed_url' : settings.REDPINE_WEBAPP_URLS['SHOW_HUB'](campaign.id),
			'venue' : venue
		   }
	)

def day_of_summary(email,data):
	campaign = data.get('campaign')

	if isinstance(campaign, int):
		campaign = models.Campaign.objects.get(pk=campaign)

	helpers.create_mail_from_template(
		recipient=email,
		subject='Things to know before your show',
		template='mail/Accepted_Show_(2 B.S.) - Pre_Show_Education.html',
		context={
			'feed_url' : settings.REDPINE_WEBAPP_URLS['SHOW_HUB'](campaign.id),
			'guest_list_url' : settings.REDPINE_WEBAPP_URLS['GUEST_LIST'](campaign.id)
		}
	)

def payouts_reminder(email,data):
	user = data.get('user')

	if isinstance(user, int):
		user = User.objects.get(pk=user)

	helpers.create_mail_from_template(
		recipient=email,
		subject='The show is done: collect your funds',
		template='mail/Post_Show.html',
		context={
			'user' : user,
			'myacts_url' : settings.REDPINE_WEBAPP_URLS['ACTS'],
			'reviews_url'  : settings.REDPINE_WEBAPP_URLS['REVIEWS']
		   }
	  )

def next_show_reminder(email,data):
	user = data.get('user')

	if isinstance(user, int):
		user = User.objects.get(pk=user)

	helpers.create_mail_from_template(
		recipient=email,
		subject='Hey, you planning a show soon?',
		template='mail/Reengage_(30 P.S).html',
		context={
			'user' : user,
			'search_venues_url' : settings.REDPINE_WEBAPP_URLS['SEARCH_VENUES'](''),
			'browse_open_lineups_url'  : settings.REDPINE_WEBAPP_URLS['SEARCH_OPEN_LINEUPS']('')
		   }
	  )

def transaction_cancelled(email,data):
	user = data.get('user')
	transaction = data.get('transaction')

	if isinstance(user, int):
		user = User.objects.get(pk=user)
	if isinstance(transaction, int):
		transaction = models.Pledge.objects.select_related('campaign').get(pk=transaction)

	helpers.create_mail_from_template(
		recipient=email,
		subject='Transaction cancelled for {}'.format(transaction.campaign.title),
		template='mail/transaction_cancelled.html',
		context={
			'transaction': transaction,
			'user': user,
			'campaign_url': settings.REDPINE_WEBAPP_URLS['SHOW'](transaction.campaign.id),
			'transactions_url': settings.REDPINE_WEBAPP_URLS['PLEDGES']()
		}
	)

def transaction_failed(email,data):
	user = data.get('user')
	campaign = data.get('campaign')

	if isinstance(user, int):
		user = User.objects.get(pk=user)
	if isinstance(campaign, int):
		campaign = models.Campaign.objects.get(pk=campaign)

	helpers.create_mail_from_template(
		recipient=email,
		subject='Transaction Failed',
		template='mail/charge_failed.html',
		context={
			'user': user,
			'campaign': campaign,
		}
	)

def subscription_failed(email,data):
	user = data.get('user')

	if isinstance(user, int):
		user = User.objects.get(pk=user)

	helpers.create_mail_from_template(
		recipient=email,
		subject='Transaction Failed',
		template='mail/subscription_failed.html',
		context={
			'user': user
		}
	)

def subscription_success(email,data):
	user = data.get('user')
	account_type = data.get('account_type','')
	product_name = data.get('product_name','')

	if isinstance(user, int):
		user = User.objects.get(pk=user)

	helpers.create_mail_from_template(
		recipient=email,
		subject='Your Subscription',
		template='mail/subscription_success.html',
		context={
			'user': user,
			'account_type': account_type,
			'product_name': product_name
		}
	)

def tickets_created(email,data):
	transaction = data.get('transaction')

	if isinstance(transaction, int):
		transaction = models.Pledge.objects.select_related('campaign').get(pk=transaction)

	purchaseSummary = []
	transactionItems = models.PledgePurchase.objects.select_related('item').filter(transaction=transaction)
	for transactionItem in transactionItems:
		purchaseSummary.append({
			'name': transactionItem.item.name,
			'quantity': transactionItem.quantity,
			'price': Decimal(transactionItem.quantity) * transactionItem.item.price
		})

	#Add redpine_fee and total row to purchase summary
	purchaseSummary.append({'name': 'Service Charge','quantity': '1','price': transaction.redpine_fee})
	purchaseSummary.append({'name': 'Total','quantity': '1','price': Decimal(transaction.total) + Decimal(transaction.redpine_fee)})
	
	i=1
	acts_list = []
	performers_string=""
	acts = models.CampaignBand.objects.filter(campaign=transaction.campaign.id,is_accepted=True,is_application=True)
	acts_count = acts.count()
	
	for act in acts:
		acts_list.append({
			'name': act.band.name,
			'short_bio': act.band.short_bio,
			'profile_link': settings.REDPINE_WEBAPP_URLS['ACT'](act.band.id)
		})
		performers_string+=act.band.name
		if i < acts_count:
			performers_string+=' | '
		i+=1    

	helpers.create_mail_from_template(
		recipient=transaction.user.email,
		subject='Attending {}'.format(transaction.campaign.title),
		template='mail/purchase_confirmation.html',
		context={
			'transaction': transaction,
			'purchases': purchaseSummary,
			'venue': transaction.campaign.timeslot.venue,
			'user': transaction.user,
			'campaign_url': settings.REDPINE_WEBAPP_URLS['SHOW'](transaction.campaign.id),
			'tickets_url': settings.REDPINE_WEBAPP_URLS['TICKETS']()
		}
	)

	helpers.create_mail_from_template(
		recipient=transaction.user.email,
		subject='Your RedPine Tickets',
		template='mail/charge_success.html',
		context={
			'user': transaction.user,
			'transaction': transaction,
			'acts': acts_list,
			'performers': performers_string,
			'campaign_url': settings.REDPINE_WEBAPP_URLS['SHOW'](transaction.campaign.id),
			'tickets_url': settings.REDPINE_WEBAPP_URLS['TICKETS'](),
			'login_url': settings.REDPINE_WEBAPP_URLS['LOGIN']()
		}
	)


#for venues - new booking request
def show_requested(email,data):
	venue = data.get('venue', None)
	campaign = data.get('campaign')

	if isinstance(venue, int):
		venue = models.Venue.objects.get(pk=venue)
	if isinstance(campaign, int):
		campaign = models.Campaign.objects.get(pk=campaign)
	
	headliner = 'Not Specified.'
	headliner = models.CampaignBand.objects.filter(campaign=campaign.id,is_headliner=True).first()
	
	show_date = campaign.timeslot.start_time
	
	i=1
	support_acts_loop=""
	support_acts = models.CampaignBand.objects.filter(campaign=campaign.id,is_headliner=False)
	support_acts_count = models.CampaignBand.objects.filter(campaign=campaign.id,is_headliner=False).count()
	
	for support_act in support_acts:
		support_acts_loop+=support_act.band.name
		if i < support_acts_count:
			support_acts_loop+=' | '
		i+=1	

	genres = ''
	if headliner:
		i=1
		genres_count = headliner.band.genres.all().count()
		for genre in headliner.band.genres.all():
			genres += genre.name
			if i < genres_count:
				genres+=' | '
			i+=1

	helpers.create_mail_from_template(
		recipient=email,
		subject='New Booking Request',
		template='mail/show_requested.html',
		context={
			'venue' : venue,
			'feed_url' : settings.REDPINE_WEBAPP_URLS['SHOW_HUB'](campaign.id),
			'headliner' : headliner.band if headliner else None,
			'genres' : genres,
			'show_date' : show_date,
			'support_acts' : support_acts_loop
		}
	)

def show_request_approved(email,data):
	user = data.get('user')
	venue = data.get('venue', None)
	campaign = data.get('campaign')

	if isinstance(user, int):
		user = User.objects.get(pk=user)
	if isinstance(venue, int):
		venue = models.Venue.objects.get(pk=venue)
	if isinstance(campaign, int):
		campaign = models.Campaign.objects.get(pk=campaign)

	helpers.create_mail_from_template(
		recipient=email,
		subject='Good News! Your show is approved',
		template='mail/show_approved.html',
		context={
			'user' : user,
			'venue' : venue,
			'campaign' : campaign,  
			'feed_url' : settings.REDPINE_WEBAPP_URLS['SHOW_HUB'](campaign.id),
			'ticket_url' : settings.REDPINE_WEBAPP_URLS['SHOW'](campaign.id),
		   }
	  )


def show_request_rejected(email,data):
	user = data.get('user', None)
	campaign = data.get('campaign')

	if isinstance(user, int):
		user = models.User.objects.get(pk=user)
	if isinstance(campaign, int):
		campaign = models.Campaign.objects.get(pk=campaign)

	helpers.create_mail_from_template(
		recipient=email,
		subject='Your booking request was declined',
		template='mail/show_rejected.html',
		context={
			'user': user,
			'campaign': campaign,
			'feed_url': settings.REDPINE_WEBAPP_URLS['SHOW_HUB'](campaign.id),
			'search_venues_url': settings.REDPINE_WEBAPP_URLS['SEARCH_VENUES']('')
		}
	)

def reviews_reminder(email,data):
	user = data.get('user')
	campaign = data.get('campaign')

	if isinstance(user, int):
		user = User.objects.get(pk=user)
	if isinstance(campaign, int):
		campaign = models.Campaign.objects.get(pk=campaign)

	helpers.create_mail_from_template(
		recipient=email,
		subject='Remember to review!',
		template='mail/reviews_reminder.html',
		context={
			'user': user,
			'campaign': campaign,
			'reviews_url': settings.REDPINE_WEBAPP_URLS['REVIEWS']
		}
	)

def new_active_show_by_subscription(email,data):
	campaign = data.get('campaign')

	if isinstance(campaign, int):
		campaign = models.Campaign.objects.get(pk=campaign)

	helpers.create_mail_from_template(
		recipient=email,
		subject='Someone you\'re subscribed to has added a show!',
		template='mail/new_active_show_by_subscription.html',
		context={
			'campaign': campaign,
			'campaign_url': settings.REDPINE_WEBAPP_URLS['SHOW'](campaign.id)
		}
	)

def weekly_venue_summary(email,data):
	venue = data.get('venue', None)

	if isinstance(venue, int):
		venue = models.Venue.objects.get(pk=venue)

	now = datetime.now()

	pending_shows = models.Campaign.objects.filter(
						timeslot__venue=venue,
						timeslot__start_time__gt=now,
						is_venue_approved=None,
						is_redpine_approved=True
						).order_by('timeslot__start_time').distinct()

	pending = []
	for show in pending_shows:
		date = '' if show.timeslot is None else show.timeslot.start_time
		headliner_name = 'Not Specified.'
		headliners = [b.band for b in models.CampaignBand.objects.filter(campaign=show,is_headliner=True,is_accepted=True)]
		if len(headliners) > 0:
			headliner_name = headliners[0].name

		pending.append({
			'date': date,
			'headliner': headliner_name,
			'hub_link': settings.REDPINE_WEBAPP_URLS['SHOW_HUB'](show.id),
			'tickets_link': settings.REDPINE_WEBAPP_URLS['SHOW'](show.id)
		})

	upcoming_shows = models.Campaign.objects.filter(
						timeslot__venue=venue,
						timeslot__start_time__gt=now,
						is_venue_approved=True,
						is_redpine_approved=True
						).order_by('timeslot__start_time').distinct()[0:20]

	upcoming = []
	for show in upcoming_shows:
		date = '' if show.timeslot is None else show.timeslot.start_time
		headliner_name = 'Not Specified.'
		headliners = [b.band for b in models.CampaignBand.objects.filter(campaign=show,is_headliner=True,is_accepted=True)]
		if len(headliners) > 0:
			headliner_name = headliners[0].name

		upcoming.append({
			'date': date,
			'headliner': headliner_name,
			'hub_link': settings.REDPINE_WEBAPP_URLS['SHOW_HUB'](show.id),
			'tickets_link': settings.REDPINE_WEBAPP_URLS['SHOW'](show.id)
		})

	historical_headcounts = { 'last_week': 0, 'last_month': 0 }
	if venue:
		historical_headcounts = venue.stats.historical_headcounts()

	#Don't send a sumary if they have no traffic.
	if len(pending) > 0 or len(upcoming) > 0:
		helpers.create_mail_from_template(
			recipient=email,
			subject='Your weekly summary for {}'.format(venue.title),
			template='mail/weekly_venue_summary.html',
			context={
				'now': now,
				'venue': venue,
				'pending_shows': pending,
				'upcoming_shows': upcoming,
				'historical_headcounts': historical_headcounts,
				'my_venues_url': settings.REDPINE_WEBAPP_URLS['VENUES'],
				'venue_calendar_url': settings.REDPINE_WEBAPP_URLS['VENUE_CALENDAR'](venue.id),
				'search_acts_url': settings.REDPINE_WEBAPP_URLS['SEARCH_ACTS_CITY']('', venue.city.id if venue.city else None)
			}
		)

def weekly_act_summary(email,data):
	act = data.get('act', None)

	if isinstance(act, int):
		act = models.Band.objects.get(pk=act)

	now = datetime.now()
	genre = act.genre.root()

	pending_shows = models.Campaign.objects.filter(
						bands=act,
						timeslot__start_time__gt=now,
						is_venue_approved=None,
						is_redpine_approved=True
						).order_by('timeslot__start_time').distinct()

	pending = []
	for show in pending_shows:
		date = '' if show.timeslot is None else show.timeslot.start_time
		headliner_name = 'Not Specified.'
		headliners = [b.band for b in models.CampaignBand.objects.filter(campaign=show,is_headliner=True,is_accepted=True)]
		if len(headliners) > 0:
			headliner_name = headliners[0].name

		pending.append({
			'date': date,
			'headliner': headliner_name,
			'hub_link': settings.REDPINE_WEBAPP_URLS['SHOW_HUB'](show.id),
			'tickets_link': settings.REDPINE_WEBAPP_URLS['SHOW'](show.id)
		})

	upcoming_shows = models.Campaign.objects.filter(
						bands=act,
						timeslot__start_time__gt=now,
						is_venue_approved=True,
						is_redpine_approved=True
						).order_by('timeslot__start_time').distinct()[0:20]

	upcoming = []
	for show in upcoming_shows:
		date = '' if show.timeslot is None else show.timeslot.start_time
		headliner_name = 'Not Specified.'
		headliners = [b.band for b in models.CampaignBand.objects.filter(campaign=show,is_headliner=True,is_accepted=True)]
		if len(headliners) > 0:
			headliner_name = headliners[0].name

		upcoming.append({
			'date': date,
			'headliner': headliner_name,
			'hub_link': settings.REDPINE_WEBAPP_URLS['SHOW_HUB'](show.id),
			'tickets_link': settings.REDPINE_WEBAPP_URLS['SHOW'](show.id)
		})

	helpers.create_mail_from_template(
		recipient=email,
		subject='Your weekly summary for {}'.format(act.name),
		template='mail/weekly_act_summary.html',
		context={
			'now': now,
			'act': act,
			'genre': genre.name if genre else '',
			'hometown': act.hometown.name if act.hometown else '',
			'pending_shows': pending,
			'upcoming_shows': upcoming,
			'play_a_show_url': settings.REDPINE_WEBAPP_URLS['PLAY_SHOW'],
			'my_acts_url': settings.REDPINE_WEBAPP_URLS['ACTS'],
			'just_tickets_url': settings.REDPINE_WEBAPP_URLS['JUST_TICKETS'],
			'search_acts_url': settings.REDPINE_WEBAPP_URLS['SEARCH_ACTS_GENRE']('', genre.id if genre else None),
			'search_venues_url': settings.REDPINE_WEBAPP_URLS['SEARCH_VENUES_CITY']('', act.hometown.id if act.hometown else None)
		}
	)


def weekly_user_concerts(email,data):
	user = data.get('user')

	if isinstance(user, int):
		user = User.objects.get(pk=user)

	transaction_campaigns = models.Pledge.objects.filter(user=user).select_related('campaign__bands__genres__genre').values('campaign__bands__genres__genre','campaign__timeslot__venue__city').distinct()
	
	campaign_genres = [c.get('campaign__bands__genres__genre') for c in transaction_campaigns]
	campaign_cities = [c.get('campaign__timeslot__venue__city') for c in transaction_campaigns]
	
	user_genres = models.Genre.objects.filter(id__in=campaign_genres)
	user_cities = models.City.objects.filter(id__in=campaign_cities)

	now = datetime.now()

	relevant_shows = models.Campaign.objects.filter(
						bands__genre__in=user_genres,
						timeslot__venue__city__in=user_cities,
						timeslot__start_time__gt=now,
						is_venue_approved=True,
						is_redpine_approved=True
						).order_by('timeslot__start_time').distinct()[:9]

	relevant = []
	for show in relevant_shows:
		date = '' if show.timeslot is None else show.timeslot.start_time
		venue = '' if show.timeslot is None else show.timeslot.venue.title

		bands_count = show.bands.count()

		i = 0
		band_names = ''
		for band in show.bands.all():
			i += 1
			band_names += band.name.upper()
			if i < bands_count:
				band_names += ' | '	

		relevant.append({
			'date': date,
			'bands': band_names,
			'venue': venue,
			'tickets_link': settings.REDPINE_WEBAPP_URLS['SHOW'](show.id)
		})

	genre = user_genres.first()
	city = user_cities.first()
	shows_count = relevant_shows.count()

	subject_line = None
	if city and genre:
		subject_line = '{} new {} shows in {}!'.format(shows_count, genre.name, city.name)
	elif city:
		subject_line = '{} new shows in {}!'.format(shows_count, city.name)
	elif genre:
		subject_line = '{} new {} shows!'.format(shows_count, genre.name)

	#Only send targetted messages.
	if subject_line and shows_count > 1:
		helpers.create_mail_from_template(
			recipient=email,
			subject=subject_line,
			template='mail/weekly_user_concerts.html',
			context={
				'now': now,
				'user': user,
				'relevant_shows': relevant,
				'search_shows_url': settings.REDPINE_WEBAPP_URLS['SEARCH_SHOWS_CITY']('', city.id if city else None)
			}
		)

def new_venue_notify_act(email,data):
	act = data.get('act', None)
	venue = data.get('venue', None)

	if isinstance(act, int):
		act = models.Band.objects.get(pk=act)
	if isinstance(venue, int):
		venue = models.Venue.objects.get(pk=venue)

	genre = act.genres.first().root()
	related_venues = models.Venue.objects.filter(Q(city=venue.city) & (Q(genres=genre) | Q(genres__genres=genre) | Q(genres__genres__genres=genre) | Q(genres__genres__genres__genres=genre)))
	related = []
	for venue in related_venues:
		genre_string = ''
		for genre in venue.genres.all():
			genre_string += genre.name
			genre_string += ' | '

		related.append({
			'title': venue.title,
			'genre': genre_string,
			'capacity': venue.capacity,
			'profile_link': settings.REDPINE_WEBAPP_URLS['VENUE'](venue.id),
			'booking_link': settings.REDPINE_WEBAPP_URLS['PLAY_SHOW_VENUE'](venue.id)
		})

	helpers.create_mail_from_template(
		recipient=email,
		subject='New {} venue in your city!'.format(genre),
		template='mail/new_venue_notify_act.html',
		context={
			'new_venue': venue,
			'act': act,
			'genre': genre.name if genre else '',
			'related_venues': related,
			'new_venue_booking_link': settings.REDPINE_WEBAPP_URLS['PLAY_SHOW_VENUE'](venue.id),
			'just_tickets_url': settings.REDPINE_WEBAPP_URLS['JUST_TICKETS'],
			'search_acts_url': settings.REDPINE_WEBAPP_URLS['SEARCH_ACTS_GENRE']('', genre.id if genre else None),
			'search_venues_url': settings.REDPINE_WEBAPP_URLS['SEARCH_VENUES_CITY']('', act.hometown.id if act.hometown else None)
		}
	)


#First message from a new user
def new_message_conversation(email,data):
	user = data.get('user', None)
	text = data.get('text')

	if isinstance(user, int):
		user = User.objects.get(pk=venue)

	helpers.create_mail_from_template(
		recipient=email,
		subject='{} wants to chat!'.format(user.username),
		template='mail/new_message_conversation.html',
		context={
			'from_user': user,
			'text': text,
			'messages_url': settings.REDPINE_WEBAPP_URLS['MESSAGES_CHAT'](user.id)
		}
	)


#Recent message from user
def new_message_reminder(email,data):
	user = data.get('user', None)
	text = data.get('text')

	if isinstance(user, int):
		user = User.objects.get(pk=venue)

	helpers.create_mail_from_template(
		recipient=email,
		subject='New message from {}!'.format(user.username),
		template='mail/new_message_reminder.html',
		context={
			'from_user': user,
			'text': text,
			'messages_url': settings.REDPINE_WEBAPP_URLS['MESSAGES_CHAT'](user.id)
		}
	)



#For Zee Mail Cannon
SEND_EMAIL = {
	'ACT_SHOW_INVITE': act_show_invite,
	'ACT_SIGNUP': act_signup,
	'SHOW_REQUESTED': show_requested,
	'SHOW_APPROVED': show_request_approved,
	'SHOW_REJECTED': show_request_rejected,
	'NEW_SHOW_HUB_MESSAGE': new_feed_message,
	'PLEDGE_CANCELLED': transaction_cancelled,
	'TRANSACTION_FAILED': transaction_failed,
	'TICKETS_CREATED': tickets_created,
	'WEEKLY_VENUE_SUMARY': weekly_venue_summary,
	'WEEKLY_ACT_SUMMARY': weekly_act_summary,
	'WEEKLY_USER_CONCERTS': weekly_user_concerts,
	'NEW_VENUE_NOTIFY_ACT': new_venue_notify_act
}

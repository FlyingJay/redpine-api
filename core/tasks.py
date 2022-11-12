from django.conf import settings
from background_task import background
from django.db.models import Q
from django.contrib.gis.geos import Point
from decimal import Decimal
from datetime import datetime, timedelta
from core import models, helpers, mail
from maas.models import Mail
from pyfcm import FCMNotification
from django.contrib.gis.measure import Distance, D
import background_task
import square
import math
import google

google_client = google.GoogleClient(settings.GOOGLE_API_KEY)


@background(schedule=0)
def send_mail(mail_id):
    """ schedules an email for sending """
    mail = Mail.objects.get(id=mail_id)
    mail.send()


@background()
def pay_performers(transaction_id):
    transaction = models.Pledge.objects.prefetch_related('campaign__bands__owner').get(id=transaction_id)

    if not transaction:
        raise Exception('pledge not found.')

    campaign = transaction.campaign
    if not campaign or transaction.payouts_processed:
        return
    
    remaining_amount = transaction.total
    
    #Pay the promoter, if neccessary
    if transaction.promoter:
        total_promoter_cut = Decimal(transaction.count) * Decimal(campaign.promoter_cut)

        if total_promoter_cut > remaining_amount:
            total_promoter_cut = remaining_amount
            remaining_amount = 0
        else:
            remaining_amount -= total_promoter_cut

        #Pay the promoter
        models.UserPayment.objects.create(
            user=transaction.promoter,
            campaign=campaign,
            amount=total_promoter_cut,
            paid=True
        )
        transaction.promoter.profile.account_balance += total_promoter_cut
        transaction.promoter.profile.save()

    if campaign.payout_type == models.Campaign.ALL_TO_ORGANIZATION:
        #Pay the organization
        if campaign.creator_organization:
            models.OrganizationPayment.objects.create(
                organization=campaign.creator_organization,
                campaign=campaign,
                amount=remaining_amount,
                paid=True
            )
            campaign.creator_organization.account_balance += remaining_amount
            campaign.creator_organization.save()

    elif campaign.payout_type == models.Campaign.ALL_TO_ORGANIZER:
        #Pay the organizer
        payee = models.User.objects.get(pk=campaign.created_by.id)
        models.UserPayment.objects.create(
            user=payee,
            campaign=campaign,
            amount=remaining_amount,
            paid=True
        )
        payee.profile.account_balance += remaining_amount
        payee.profile.save()

    elif campaign.payout_type == models.Campaign.SPLIT_BY_ACT_SALES:

        #Payouts may only be split between performers who have accepted the show.
        performers = models.CampaignBand.objects.select_related('band').filter(campaign=campaign,is_accepted=True)
        performers_count = performers.count()

        if performers_count == 0:
            raise Exception('Can\'t pay out acts, none are connected to the show.')

        going_to_see = performers.filter(pk__in=transaction.bands.all())
        performers_count = going_to_see.count()

        if performers_count == 0:
            """ 
            Pay the show's organizer. 
            This should only happen if an act the user is "going to see" dropped out of the show.
            """
            payee = models.User.objects.get(pk=campaign.created_by.id)
            models.UserPayment.objects.create(
                user=payee,
                campaign=campaign,
                amount=remaining_amount,
                paid=True
            )
            payee.profile.account_balance += remaining_amount
            payee.profile.save()
        else:
            #Share of the transaction amount for each act.
            int_total = int(remaining_amount * Decimal('100'))
            amount = math.floor(int_total/performers_count)/100.0

            for performer in going_to_see:
                band = models.Band.objects.get(pk=performer.band.id)
                models.ActPayment.objects.create(
                    band=performer.band,
                    campaign=campaign,
                    amount=amount,
                    paid=True
                )
                band.account_balance += Decimal(amount)
                band.save()
    else:
        raise Exception('Unknown payout method.')

    transaction.payouts_processed = True
    transaction.save()


@background(schedule=0)
def process_transaction(transaction_id):
    """ attempts to process a transaction into a ticket """
    transaction = models.Pledge.objects.prefetch_related('campaign__bands__owner__profile').get(id=transaction_id)

    if transaction.is_cancelled or transaction.is_processed:
        return

    campaign = transaction.campaign
    
    if campaign.timeslot.venue:
        currency = campaign.timeslot.venue.currency
    else:
        currency = models.Venue.CAD
        
    #.upper() is part of the Stripe implementation to be removed once all transactions are processed.
    if currency.upper() == models.Venue.CAD or currency.upper() == models.Venue.USD:
        total = int(transaction.total * Decimal('100'))
        fee = int(transaction.redpine_fee * Decimal('100'))
    else:
        raise Exception('attempting to charge an unknown currency.  might want to test first.')
    
    metadata = {
        'user': transaction.user.id,
        'transaction': transaction.id
    }
    try:
        if transaction.square_customer:
            transaction.square_customer.charge(
                amount=(total + fee), 
                currency=currency.upper(),
                metadata=metadata
            )

        #Update transaction statuses
        models.Pledge.objects.filter(id=transaction_id).update(is_processed=True,is_processing_failed=False)

        #Schedule payout task
        pay_performers(transaction_id, schedule=campaign.funding_end, queue='payouts_{}'.format(transaction.campaign.id))
        
        if campaign.tickets_sold() == transaction.count:
            for band in campaign.bands.all():
                if band.owner:
                    rewards = models.Reward.objects.filter(subject=band.owner,reward_type=1,is_completed=False) 
                    #Pay out rewards, if applicable
                    for reward in rewards:
                        band.owner.profile.account_balance += reward.amount
                        band.owner.profile.save()
                        reward.is_completed = True
                        reward.save()

        mail.tickets_created(email=transaction.user.email, data={'transaction':transaction})

        #Send mail
        """
        if campaign.is_only_tickets:
            mail.tickets_created(email=transaction.user.email, data={
                'timeslot': transaction.campaign.timeslot,
                'transaction': transaction,
                'user': transaction.user,
                'purchases': purchaseSummary
            })
        else:
            helpers.create_mail_from_template(
                recipient=transaction.user.email,
                subject='Attending {}'.format(campaign.title),
                template='mail/purchase_confirmation.html',
                context={
                    'transaction': transaction,
                    'purchases': purchaseSummary,
                    'venue': campaign.timeslot.venue,
                    'user': transaction.user,
                    'campaign_url': settings.REDPINE_WEBAPP_URLS['SHOW'](campaign.id),
                    'tickets_url': settings.REDPINE_WEBAPP_URLS['TICKETS']()
                }
            )
        """
        return transaction
        
    except square.exceptions.ChargeFailureException as e:
        if not transaction.is_processing_failed: #Allows task to be run again without re-sending an email
            mail.transaction_failed(email=transaction.user.email, data={
                'user': transaction.user,
                'campaign': transaction.campaign
                })
            transaction.is_processing_failed = True
            transaction.save()
            raise square.exceptions.ChargeFailureException()
        else:
            raise Exception('Failed to charge Square. (again)')
    except Exception as e:
        print(e)
        raise e


#1 day after the show
@background()
def create_reviews(campaign_id):
    campaign = models.Campaign.objects.prefetch_related('bands__owner__profile').get(pk=campaign_id)
    #Reschedule if needed.
    one_day_after_show = campaign.timeslot.start_time + timedelta(days=1)
    if one_day_after_show > datetime.now():
        create_reviews(campaign_id, schedule=one_day_after_show, queue='create_reviews_{}'.format(campaign_id))
    else:
        campaign_bands = models.CampaignBand.objects.filter(campaign=campaign.id,is_accepted=True,is_application=True).distinct()
        for band in campaign_bands:
            for band_2 in campaign_bands:
                if band.id != band_2.id:
                    models.BandToBandReview.objects.create(
                        band=band_2.band,
                        reviewer=band.band
                        )
            models.BandToVenueReview.objects.create(
                venue=campaign.timeslot.venue,
                reviewer=band.band
                )
            models.VenueToBandReview.objects.create(
                band=band.band,
                reviewer=campaign.timeslot.venue
                )
            #Reminder emails for acts
            owner = band.band.owner
            if owner and owner.profile.receives_emails:
                mail.reviews_reminder(email=owner.email, data={'user':owner,'campaign':campaign})
        
        #Reminder emails for venues
        venue = campaign.timeslot.venue
        if venue:
            for manager in venue.managers.all():
                if manager.profile.receives_emails:
                    mail.reviews_reminder(email=manager.email, data={'user':manager,'campaign':campaign})


#ACT EDUCATION EMAIL PIPELINE
#2 days after venue approval
@background()
def promotion_reminder(campaign_id):
    campaign = models.Campaign.objects.prefetch_related('bands__owner__profile').get(pk=campaign_id)

    for band in campaign.bands.all():
        if band.owner and band.owner.profile.receives_emails:
            mail.promotion_reminder(email=band.owner.email, data={'campaign':campaign})


#1 month before the show
@background()
def one_month_reminder(campaign_id):
    campaign = models.Campaign.objects.prefetch_related('bands__owner__profile').get(pk=campaign_id)
    #Reschedule if needed.
    thirty_days_before_show = campaign.timeslot.start_time - timedelta(days=30)
    if thirty_days_before_show > datetime.now():
        one_month_reminder(campaign_id, schedule=thirty_days_before_show, queue='show_touchpoints_{}'.format(campaign_id))
    else:
        for band in campaign.bands.all():
            if band.owner and band.owner.profile.receives_emails:
                mail.one_month_reminder(email=band.owner.email, data={'campaign':campaign,'venue':campaign.timeslot.venue})


#1 week before the show
@background()
def one_week_reminder(campaign_id):
    campaign = models.Campaign.objects.prefetch_related('bands__owner__profile').get(pk=campaign_id)
    #Reschedule if needed.
    seven_days_before_show = campaign.timeslot.start_time - timedelta(days=7)
    if seven_days_before_show > datetime.now():
        one_week_reminder(campaign_id, schedule=seven_days_before_show, queue='show_touchpoints_{}'.format(campaign_id))
    else:
        for band in campaign.bands.all():
            if band.owner and band.owner.profile.receives_emails:
                mail.one_week_reminder(email=band.owner.email, data={'campaign':campaign,'venue':campaign.timeslot.venue})


#2 days before the show
@background()
def day_of_summary(campaign_id):
    campaign = models.Campaign.objects.prefetch_related('bands__owner__profile').get(pk=campaign_id)
    #Reschedule if needed.
    two_days_before_show = campaign.timeslot.start_time - timedelta(days=2)
    if two_days_before_show > datetime.now():
        day_of_summary(campaign_id, schedule=two_days_before_show, queue='show_touchpoints_{}'.format(campaign_id))
    else:
        for band in campaign.bands.all():
            if band.owner and band.owner.profile.receives_emails:
                mail.day_of_summary(email=band.owner.email, data={'campaign':campaign})


#1 day after the show
@background()
def payouts_reminder(campaign_id):
    campaign = models.Campaign.objects.prefetch_related('bands__owner__profile').get(pk=campaign_id)
    #Reschedule if needed.
    one_day_after_show = campaign.timeslot.start_time + timedelta(days=1)
    if one_day_after_show > datetime.now():
        payouts_reminder(campaign_id, schedule=one_day_after_show, queue='show_touchpoints_{}'.format(campaign_id))
    else:
        for band in campaign.bands.all():
            if band.owner and band.owner.profile.receives_emails:
                mail.payouts_reminder(email=band.owner.email, data={'user':band.owner})


#30 days after the show
@background()
def next_show_reminder(campaign_id):
    campaign = models.Campaign.objects.prefetch_related('bands__owner__profile').get(pk=campaign_id)
    #Reschedule if needed.
    thirty_days_after_show = campaign.timeslot.start_time + timedelta(days=30)
    if thirty_days_after_show > datetime.now():
        next_show_reminder(campaign_id, schedule=thirty_days_after_show, queue='show_touchpoints_{}'.format(campaign_id))
    else:
        for band in campaign.bands.all():
            if band.owner and band.owner.profile.receives_emails:
                mail.next_show_reminder(email=band.owner.email, data={'user':band.owner})

#END OF ACT EDUCATION EMAIL PIPELINE


@background(schedule=0)
def new_venue_registered(venue_id):
    venue = models.Venue.objects.get(pk=venue_id)
    city_acts = venue.city.bands.filter(genres=venue.genres)
    for act in city_acts:
        if act.owner and act.owner.profile.receives_emails:
            mail.new_venue_notify_act(email=act.owner.email, data={
                'act': act,
                'venue': venue
                })


@background(schedule=0)
def renew_subscription(subscription_id):
    account_subscription = models.AccountSubscription.objects.get(pk=subscription_id)
    new_account_subscription = None
    
    if account_subscription.is_cancelled:
        return

    try:
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
        renew_subscription(new_account_subscription.pk, schedule=renewal_date)

    except Exception as e:
        if not account_subscription.is_processing_failed:
            mail.subscription_failed(email=account_subscription.user.email, data={'user': account_subscription.user})
            account_subscription.is_processing_failed = True
            account_subscription.is_cancelled = True
            account_subscription.save()
        print(e)
        pass


@background(schedule=0)
def weekly_reports(send_fans=True,send_venues=True,send_acts=True):
    #Fan Reports
    if send_fans:
        fans = models.User.objects.filter(profile__is_venue=False).select_related('profile')
        for fan in fans:
            if fan.profile and fan.profile.receives_emails:
                mail.weekly_user_concerts(email=fan.email, data={'user': fan})
    #Venue Reports
    if send_venues:
        venues = models.Venue.objects.prefetch_related('managers__profile').all()
        for venue in venues:
            for manager in venue.managers.all():
                if manager.profile.receives_emails:
                    mail.weekly_venue_summary(email=manager.email, data={'venue': venue})
    #Act Reports
    if send_acts:
        acts = models.Band.objects.prefetch_related('owner__profile').all()
        for act in acts:
            if act.owner and act.owner.profile.receives_emails:
                mail.weekly_act_summary(email=act.owner.email, data={'act': act})


#Update any cities in our system with missing lat/long coordinates.
def get_gps_coordinates(clear_previous=False):
    if clear_previous:
        models.City.objects.all().update(location=None)
        print('cleared.')

    cities = models.City.objects.filter(location=None)
    for city in cities.all():
        print(city)
        try:
            query = '{}, {}'.format(city.name, city.province.name)
            geocoded = google_client.geocode(query)
            city.location = Point(geocoded.location.y,geocoded.location.x)
            city.save()
        except google.GoogleNoResultsException:
            raise 
    print('done.')


@background(schedule=0)
def check_in():
    """ This just tells us the job runner is alive """
    checkin = models.JobRunnerCheckin.objects.first()

    if checkin is None:
        checkin = models.JobRunnerCheckin.objects.create()

    checkin.save()


""" 
This block registers our "check-in" task for the job runner.
We're doing a try; except; because it fails for some reason in
CI if we do not..
"""
try:
    if background_task.models.Task.objects.filter(task_name='core.tasks.check_in').count() < 1:
        check_in(repeat=60)
except:
    pass


######################
# INTERNAL FUNCTIONS #
######################

def confirm_campaign(campaign_id):
    from core import models
    campaign = models.Campaign.objects.filter(id=campaign_id).first()
    campaign.is_redpine_approved = True
    campaign.save()


#Use/Change this to test new email templates.
def test_email():
    # request = models.BookingRequest.objects.get(id=1)
    # venue = request.campaign.timeslot.venue
    # campaign =request.campaign
    #models.CampaignBand.objects.filter(campaign=77,is_headliner=True)
    #headliner = 'Not Specified.'
    #headliners = models.CampaignBand.objects.filter(campaign=77,is_headliner=True).first()
    
    # headliner=campaign.bands.filter(is_headliner=True).first().band


                                     #.filter(capacity__lt=200,has_wifi=False)
                                     #.exclude()
                                     #.order_by('capacity')
    #transaction = models.Pledge.objects.get(pk=216)

    #mail.weekly_venue_summary()

    #Use this to make a question
    #question = models.SurveyQuestion.objects.create(text='Would you like to answer this question?')

    #Use this to reuse the question you created before (it's saved now)
    #question = models.SurveyQuestion.objects.filter(text='Would you like to answer this question?').first()

    #user = models.User.objects.get(id=1022)
    transaction = models.Pledge.objects.get(id=423)
    timeslot = transaction.campaign.timeslot

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
        recipient='jrivers95@yahoo.com',
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


def create_campaign_ticket_items():
    """ Converts old transactions into the new tiered format. """
    """ DO NOT RUN UNLESS YOU KNOW EXACTLY WHY YOU NEED TO, THIS WILL DESTROY DATA """
    campaigns = models.Campaign.objects.all()
    for campaign in campaigns:
        models.PurchaseItem.objects.create(
            name="Standard Ticket",
            price=campaign.min_ticket_price,
            campaign=campaign,
            is_ticket=True
        )
    transactions = models.Pledge.objects.all()
    for transaction in transactions:
        ticketItem = models.PurchaseItem.objects.filter(campaign=transaction.campaign).first()
        if ticketItem:
            purchase = models.PledgePurchase.objects.create(
                transaction=transaction,
                item=ticketItem,
                quantity=getattr(transaction,'count',0)
            )
            tickets = models.Ticket.objects.filter(pledge=transaction)
            for ticket in tickets:
                ticket.details = ticketItem
                ticket.save()


def reject_show(campaign_id, message):
    campaign = models.Campaign.objects.get(pk=campaign_id)

    campaign.is_redpine_approved = False
    campaign.save()

    #Send notifications to show's owner
    models.Notification.objects.create(
        profile=campaign.created_by.profile,
        subject_type=1,#CAMPAIGN
        text=message,
        campaign=campaign
    )


@background
def send_push_notification(notification_id):
    notification = models.Notification.objects.get(pk=notification_id)
    push = FCMNotification(settings.FCM_API_KEY)
    user = notification.profile.user
    tokens = [t.token for t in models.PushToken.objects.filter(user=user)]

    # i'm only implementing for campaigns, but you get the gist
    if notification.subject_type != models.Notification.CAMPAIGN:
        return

    message = {
        'registration_ids': tokens,
        'message_title': 'Campaign Updated',
        'message_body': notification.text,
    }

    if notification.campaign:
        # this will make it automatically jump to the campaign when
        # the notification is tapped.
        # see mobile repo's README.md for more info
        message['data_message'] = {
            'type': 'SHOW_HUB',
            'showId': notification.campaign.id,
        }

    push.notify_multiple_devices(**message)
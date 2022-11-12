from django.db import models
from django.db.models import Avg, Max, Min, Sum
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.contrib.gis.db.models import PointField
from django.contrib.gis.geos import Point
from django_extensions.db.models import TimeStampedModel
from django.utils.html import mark_safe
from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.utils.translation import ugettext as _
from django.conf import settings
from square import models as square_models
from core import mail, tasks
from internal import validators
from internal.models import ArchiveOnDelete 
from datetime import datetime, timedelta
import secrets
import html
import hashlib
import hmac
import json
import random
from urllib.parse import quote


NULL_BOOLEAN_CHOICES = [
	(None, 'null',),
	(True, 'true',),
	(False, 'false',),
]


##########
# FIELDS #
##########

def MONEY_FIELD(**kwargs):
	return models.DecimalField(max_digits=6, decimal_places=2, validators=[validators.non_negative], **kwargs)


def FIVE_STAR_FIELD(**kwargs):
	
	NULL = -1
	ONE_STAR = 0
	TWO_STAR = 1
	THREE_STAR = 2
	FOUR_STAR = 3
	FIVE_STAR = 4

	RATINGS = (
		(NULL,'NULL'),
		(ONE_STAR,'ONE_STAR'),
		(TWO_STAR,'TWO_STAR'),
		(THREE_STAR,'THREE_STAR'),
		(FOUR_STAR,'FOUR_STAR'),
		(FIVE_STAR,'FIVE_STAR')
	)

	return models.IntegerField(default=-1, choices=RATINGS, validators=[MinValueValidator(-1),MaxValueValidator(4)], **kwargs)


def build_anchor(url = None, label = None, target = '_blank', filename = None):
	if filename is None:
		download = ''
	else:
		download = ' download="{}" '.format(filename)

	if label is None:
		raise Exception('Need a label for the anchor!')

	if url is None:
		raise Exception('Need a URL for the anchor!')

	return mark_safe('<a href="{}" target="{}" {}>{}</a>'.format(url, target, download, label))


def get_admin_url_for_model(object, action = 'change', id = None):
	args = (id,) if id is not None else ()
	content_type = ContentType.objects.get_for_model(object.__class__)
	url = urlresolvers.reverse('admin:{}_{}_{}'.format(content_type.app_label, content_type.model, action), args=args)
	return url


##########
# MODELS #
##########

class Social(models.Model):
	class Meta:
		abstract = True

	website = models.URLField(blank=True, null=True, default=None)
	facebook = models.URLField(blank=True, null=True, default=None)
	twitter = models.URLField(blank=True, null=True, default=None)
	instagram = models.URLField(blank=True, null=True, default=None)
	spotify = models.URLField(blank=True, null=True, default=None)
	soundcloud = models.URLField(blank=True, null=True, default=None)
	bandcamp = models.URLField(blank=True, null=True, default=None)
	youtube = models.URLField(blank=True, null=True, default=None)


class Country(models.Model):
	name = models.CharField(max_length=100)

	class Meta:
		verbose_name_plural = 'Countries'

	def __str__(self):
		return self.name


class Province(models.Model):
	name = models.CharField(max_length=100)
	country = models.ForeignKey(Country, related_name='provinces')

	class Meta:
		verbose_name_plural = 'Provinces'

	def __str__(self):
		return self.name


class City(models.Model):
	name = models.CharField(max_length=100)
	province = models.ForeignKey(Province, related_name='cities')
	#location = PointField(null=True, blank=True, geography=True)

	class Meta:
		verbose_name_plural = 'Cities'

	def __str__(self):
		return self.name


class Profile(TimeStampedModel):
	user = models.OneToOneField(User, related_name='profile')
	referrer = models.ForeignKey(User, related_name='referrals', null=True, blank=True, default=None, help_text='The user who invited this user to RedPine, if any.')
	picture = models.ImageField(blank=True, null=True)
	birthdate = models.DateTimeField(null=True, blank=True, default=None)
	account_balance = MONEY_FIELD(null=True, blank=True, default=0.00)
	is_email_confirmed = models.BooleanField(default=False, help_text='Whether the user\'s email has been confirmed')
	is_alpha_user = models.BooleanField(default=False, help_text='Whether the user has reset their password for beta')
	is_ghost = models.BooleanField(default=False, help_text='Whether the account has been claimed or not.')
	email_confirmation_token = models.CharField(blank=True, null=True, max_length=32)
	password_reset_token = models.CharField(blank=True, null=True, max_length=16)

	receives_emails = models.BooleanField(default=True, help_text='Whether the user should recieve email notifications')
	
	#ARTIST ACCOUNT LEVELS
	is_artist = models.BooleanField(default=False, help_text='Does the user want to see artist sections of the app?')
	is_member_artist = models.BooleanField(default=False, help_text='Can the artist use member features?')
	is_ultimate_artist = models.BooleanField(default=False, help_text='Can the artist use ultimate features?')

	#VENUE ACCOUNT LEVELS
	is_venue = models.BooleanField(default=False, help_text='Does the user want to see venue sections of the app?')
	is_member_venue = models.BooleanField(default=False, help_text='Can the venue use member features?')
	is_ultimate_venue = models.BooleanField(default=False, help_text='Can the venue use ultimate features?')

	#ORGANIZER ACCOUNT LEVELS
	is_member_organizer = models.BooleanField(default=False, help_text='Can the venue use organizer features?')

	#FAN WELCOME TASKS
	welcome_add_profile_pic = models.BooleanField(default=False, help_text='Whether or not the user has added a profile pic.')
	welcome_view_my_tickets = models.BooleanField(default=False, help_text='Whether or not the user has checked out My Tickets.')

	#ARTIST WELCOME TASKS
	welcome_create_act = models.BooleanField(default=False, help_text='Whether or not the user has added an act, or was added to one.')
	welcome_add_act_socials = models.BooleanField(default=False, help_text='Whether or not the user has added socials to their act.')
	welcome_submit_booking_request = models.BooleanField(default=False, help_text='Whether or not the user has requested to book a venue.')

	#VENUE WELCOME TASKS
	welcome_create_venue = models.BooleanField(default=False, help_text='Whether or not the user has added a venue, or was added to one.')
	welcome_check_calendar = models.BooleanField(default=False, help_text='Whether or not the user has checked their calendar.')
	welcome_add_event = models.BooleanField(default=False, help_text='Whether or not the user has tried adding an event or hold for their venue.')
	welcome_approve_booking_request = models.BooleanField(default=False, help_text='Whether or not the user has approved a booking request.')

	def has_unread_notifications(self):
		return self.notifications.filter(is_read=False).count() > 0

	def referral_url(self):
		return '{}/register/email?referrer={}'.format(settings.REDPINE_WEBAPP_BASE_URL, self.user.id)

	def get_queryset(self):
		return super(Profile, self).get_queryset()

	def generate_email_confirmation_token(self):
		self.email_confirmation_token = secrets.token_hex(16)

	def generate_password_reset_token(self):
		self.password_reset_token = secrets.token_hex(8)

	def get_email_confirmation_url(self):
		return '{}/confirm-email?email={}&token={}'.format(settings.REDPINE_WEBAPP_BASE_URL, self.user.email, self.email_confirmation_token)

	def get_password_reset_url(self):
		return '{}/reset-password?email={}&token={}'.format(settings.REDPINE_WEBAPP_BASE_URL, self.user.email, self.password_reset_token)

	def tawk_hash(self):
		return hmac.new(settings.TAWK_API_KEY.encode(), msg=self.user.email.encode(), digestmod=hashlib.sha256).hexdigest()

	def __str__(self):
		return self.user.username


class NotificationManager(models.Manager):
	def create(self, *args, **kwargs):
		notification = super().create(*args, **kwargs)
		tasks.send_push_notification(notification.id)
		return notification


class Notification(TimeStampedModel):
	# NOTIFICATION TYPES
	SYSTEM = 0
	CAMPAIGN = 1
	VENUE = 2
	BAND = 3
	TICKETS = 4

	NOTIFICATION_TYPE_CHOICES = (
		(SYSTEM, 'SYSTEM'),
		(CAMPAIGN, 'CAMPAIGN'),
		(VENUE, 'VENUE'),
		(BAND, 'BAND'),
		(TICKETS, 'TICKETS'),
	)

	profile = models.ForeignKey('Profile', related_name='notifications')
	text = models.CharField(max_length=200)
	subject_type = models.IntegerField(choices=NOTIFICATION_TYPE_CHOICES, default=SYSTEM)
	is_read = models.BooleanField(default=False)
	created_date = models.DateTimeField(auto_now_add=True, null=True)

	band = models.ForeignKey('Band', blank=True, null=True, default=None)
	venue = models.ForeignKey('Venue', blank=True, null=True, default=None)
	campaign = models.ForeignKey('Campaign', blank=True, null=True, default=None)

	objects = NotificationManager()

	def link(self):
		if self.subject_type is type(self).CAMPAIGN:
			return settings.REDPINE_WEBAPP_URLS['SHOW_HUB'](self.campaign.id)
		elif self.subject_type is type(self).VENUE:
			return settings.REDPINE_WEBAPP_URLS['VENUES']()
		elif self.subject_type is type(self).BAND:
			return settings.REDPINE_WEBAPP_URLS['ACTS']()
		elif self.subject_type is type(self).TICKETS:
			return settings.REDPINE_WEBAPP_URLS['SHOW'](self.campaign.id)
		else:
			return None

	def get_queryset(self):
		return super(Notification, self).get_queryset().order_by('-created_date')


class Genre(TimeStampedModel):
	name = models.CharField(max_length=200)
	genres = models.ManyToManyField('Genre', through='GenreParent', related_name='children', help_text='The parent genres, if applicable.')

	def __str__(self):
		return self.name

	def root(self):#Returns the first root genre.
		if self.genres.count() == 0:
			return self
		else:
			return self.genres.first().root()
			

class GenreParent(TimeStampedModel):
	class Meta:
		verbose_name_plural = 'Genre Network'

	genre = models.ForeignKey(Genre, related_name='parents')
	parent = models.ForeignKey(Genre)

	def __str__(self):
		return self.parent.name + ' -> ' + self.genre.name


class Band(ArchiveOnDelete, TimeStampedModel, Social):#ie. Act
	name = models.CharField(max_length=200, db_index=True)
	short_bio = models.TextField(max_length=500)
	genres = models.ManyToManyField('Genre', related_name='bands', blank=True, help_text='The band\'s genre tags')
	hometown = models.ForeignKey('City', related_name='bands', blank=True, null=True)
	owner = models.ForeignKey(User, null=True, help_text='The user responsible for the band')
	picture = models.ImageField(null=True, blank=True)
	setlist = models.CharField(max_length=200, null=True, default=None)
	account_balance = MONEY_FIELD(null=True, blank=True, default=0.00)
	join_token = models.CharField(default=None, blank=True, null=True, max_length=32)
	is_redpine = models.BooleanField(default=True)
	is_available = models.BooleanField(default=False)
	current_city = models.ForeignKey('City', related_name='current_bands', blank=True, null=True, default=None)
	is_featured = models.BooleanField(default=False, help_text='Whether the band should be featured on our home page')
	created_date = models.DateTimeField(auto_now_add=True, null=True)

	class Meta:
		ordering = ['-id']

	def __str__(self):
		return self.name


class AdminMail(TimeStampedModel):
	class Meta:
		verbose_name_plural = 'Zee Mail Cannon'

	template = models.CharField(max_length=200)
	sender = models.ForeignKey(User, help_text='A user associated with the mail. (you)')
	recipient_email = models.CharField(max_length=200)
	data = JSONField(default='{}', null=True, blank=True)

	resend = models.BooleanField(default=False)

	def __str__(self):
		return self.recipient_email + ' (' + self.template + ')'

	def save(self, *args, **kwargs):
		if not self.pk or self.resend:
			mail.SEND_EMAIL[self.template](self.recipient_email, json.loads(self.data))
			self.resend = False

		return super().save(*args, **kwargs)

#Used for invitations to RedPine
class Invitation(TimeStampedModel):
	template = models.CharField(max_length=200)
	sender = models.ForeignKey(User, help_text='The user that sent the invitation')
	recipient_email = models.CharField(max_length=200)
	join_token = models.CharField(blank=True, null=True, max_length=32)
	is_successful = models.BooleanField(default=False, help_text='Whether the invited user actually signed up or not')
	data = JSONField(default='{}', null=True, blank=True)

	def __str__(self):
		return self.recipient_email + (' (Y)' if self.is_successful else ' (N)')

	def save(self, *args, **kwargs):
		if not self.pk and self.template == 'ACT_SHOW_INVITE':
			mail.SEND_EMAIL['ACT_SHOW_INVITE'](self.recipient_email, self.data)
		
		return super().save(*args, **kwargs)


class CampaignDocument(TimeStampedModel):
	name = models.CharField(blank=True,default='Document',max_length=200)
	document = models.FileField()
	campaign = models.ForeignKey('Campaign', related_name='documents')


class CampaignPhoto(TimeStampedModel):
	photo = models.ImageField()
	campaign = models.ForeignKey('Campaign', related_name='photos')


class CampaignMember(TimeStampedModel):
	class Meta:
		abstract = True
		ordering = ['-id']

	campaign = models.ForeignKey('Campaign')
	is_accepted = models.NullBooleanField(null=True, default=None)


class CampaignBand(CampaignMember):
	class Meta(CampaignMember.Meta):
		ordering = ['-start_time']

	band = models.ForeignKey('Band')
	is_headliner = models.BooleanField()
	is_application = models.NullBooleanField(null=True, default=False, help_text='Is the member applying to an opportunity?')
	start_time = models.DateTimeField(null=True, default=None, blank=True, help_text='The time when the act\'s performance will start.')

	was_application = None

	def __str__(self):
		return self.band.name

	def __init__(self, *args, **kwargs):
		super(CampaignBand, self).__init__(*args, **kwargs)
		self.was_application = self.is_application

	def save(self, *args, **kwargs):
		#self.full_clean()
		#Approved by organizer
		if self.is_application and not self.was_application:
			if self.band.owner and self.band.owner.profile.receives_emails:
				mail.open_lineup_act_accepted(email=self.band.owner.email, data={'band':self.band,'campaign':self.campaign})
		#Rejected by organizer
		elif self.is_application is False and self.was_application is None:
			if self.band.owner and self.band.owner.profile.receives_emails:
				mail.open_lineup_act_rejected(email=self.band.owner.email, data={'band':self.band,'campaign':self.campaign})
		
		return super(CampaignBand, self).save(*args, **kwargs)


class CampaignOrganization(CampaignMember):
	organization = models.ForeignKey('Organization')
	can_edit = models.BooleanField(default=True)

	def __str__(self):
		return self.organization.title

		
class Campaign(ArchiveOnDelete, TimeStampedModel):
	""" FUNDING TYPES """
	GOAL_AMOUNT = 0
	GOAL_COUNT = 1
	HYBRID = 2

	FUNDING_TYPE_CHOICES = (
		(GOAL_AMOUNT, 'GOAL_AMOUNT'),
		(GOAL_COUNT, 'GOAL_COUNT'),
		(HYBRID, 'HYBRID'),
	)

	""" SEATING TYPES """
	FIRST_COME_FIRST_SEATING = 0

	SEATING_TYPE_CHOICES = (
		(FIRST_COME_FIRST_SEATING, 'FIRST_COME_FIRST_SEATING'),
	)

	""" PAYOUT OPTIONS """
	ALL_TO_ORGANIZER = 0
	SPLIT_BY_ACT_SALES = 1
	ALL_TO_ORGANIZATION = 2

	PAYOUT_TYPE_CHOICES = (
		(ALL_TO_ORGANIZER, 'ALL_TO_ORGANIZER'),
		(SPLIT_BY_ACT_SALES, 'SPLIT_BY_ACT_SALES'),
		(ALL_TO_ORGANIZATION, 'ALL_TO_ORGANIZATION'),
	)

	DEFAULT_SERVICE_FEE = 15.00#%

	title = models.CharField(max_length=200, db_index=True)
	description = models.TextField(max_length=2000)
	goal_amount = MONEY_FIELD(null=True, blank=True)
	goal_count = models.IntegerField(default=0, help_text='Should not be 0 unless the show is direct-booked, even if the funding condition is GOAL_AMOUNT.')
	minimum_age = models.IntegerField(null=True, blank=True, default=0)
	funding_type = models.IntegerField(choices=FUNDING_TYPE_CHOICES, default=HYBRID)
	seating_type = models.IntegerField(choices=SEATING_TYPE_CHOICES, default=FIRST_COME_FIRST_SEATING)
	payout_type = models.IntegerField(choices=PAYOUT_TYPE_CHOICES, default=SPLIT_BY_ACT_SALES)
	funding_start = models.DateTimeField(null=True, blank=True)
	funding_end = models.DateTimeField()
	min_ticket_price = MONEY_FIELD()
	promoter_cut = models.DecimalField(max_digits=4, decimal_places=2, default=0.00, validators=[validators.non_negative])
	hashtag = models.CharField(max_length=50, null=True, blank=True)
	picture = models.ImageField(null=True, blank=True)
	is_open = models.BooleanField(default=False, help_text='Is the show a public opportunity?')
	is_hold = models.BooleanField(default=False, help_text='Has the venue put the show on hold?')
	is_open_mic = models.BooleanField(default=False, help_text='Is the show a public open mic?')
	is_venue_approved = models.NullBooleanField(default=None, help_text='Whether the venue has confirmed the show', choices=NULL_BOOLEAN_CHOICES)
	is_redpine_approved = models.NullBooleanField(default=True, help_text='Whether RedPine has approved the show to be sent to the venue', choices=NULL_BOOLEAN_CHOICES)
	is_successful = models.BooleanField(default=True, help_text='Whether the show has been fully funded or not')
	bands = models.ManyToManyField('Band', related_name='campaigns', through='CampaignBand')
	timeslot = models.ForeignKey('Timeslot', related_name='campaigns')
	organizations = models.ManyToManyField('Organization', related_name='campaigns', through='CampaignOrganization')
	third_party_tickets = models.URLField(blank=True, null=True, default=None, help_text='The URL for the event\'s non-redpine ticketing page.')

	service_fee = models.DecimalField(max_digits=4, decimal_places=2, default=DEFAULT_SERVICE_FEE, validators=[validators.non_negative])
	is_featured = models.BooleanField(default=False, help_text='Whether to include the show on the home page or not..')

	created_by = models.ForeignKey(User, help_text='The user who created the show')
	creator_organization = models.ForeignKey('Organization', related_name='created_campaigns', blank=True, null=True, default=None, help_text='The organization who requested the show, if any.')
	
	created_date = models.DateTimeField(auto_now_add=True, null=True)
	success_date = models.DateTimeField(null=True, blank=True)

	""" CHECKLIST """
	has_event_page = models.BooleanField(default=False, help_text='The artists have created an event page for the show')
	has_set_order = models.BooleanField(default=False, help_text='The artists have chosen a set order')
	has_door_plan = models.BooleanField(default=False, help_text='The artists and venue have agreed on how doors should be handled.')
	has_sound_plan = models.BooleanField(default=False, help_text='The artists and venue have agreed on how sound should be handled.')
	has_equipment_plan = models.BooleanField(default=False, help_text='The artists and venue are aware of their equipment responsibilities.')

	facebook_event = models.URLField(blank=True, null=True, default=None, help_text='The URL for the event\'s facebook page.')
	discuss_doors = models.TextField(max_length=2000, default='', blank=True)
	discuss_sound = models.TextField(max_length=2000, default='', blank=True)
	discuss_equipment = models.TextField(max_length=2000, default='', blank=True)
	
	""" ONLY TICKETS SHOWS """
	is_only_tickets = models.BooleanField(default=False, help_text='For campaigns which do not have a venue relationship.')

	""" CACHED AGGREGATES """
	total_count = models.IntegerField(null=True, default=None, blank=True, help_text='The cached ticket count. Should be "None" until after the show date.')
	total_raised = MONEY_FIELD(null=True, default=None, blank=True, help_text='The cached revenue total. Should be "None" until after the show date.')

	""" DOOR CODES """
	door_code = models.CharField(max_length=6, blank=True, null=True, unique=True)

	was_redpine_approved = None
	was_venue_approved = None
	was_hold = None

	class Meta:
		ordering = ['-id']

	def __str__(self):
		return self.title

	def __init__(self, *args, **kwargs):
		super(Campaign, self).__init__(*args, **kwargs)
		self.was_redpine_approved = self.is_redpine_approved
		self.was_venue_approved = self.is_venue_approved
		self.was_hold = self.is_hold

	def save(self, *args, **kwargs):
		self.full_clean()

		if self.door_code is None:
			self.door_code = self._generate_door_code()

		if self.is_hold and not self.was_hold:
			for band in self.bands.all():
				if band.owner and band.owner.profile.receives_emails:
					mail.booking_request_on_venue_hold(email=band.owner.email, data={'user':band.owner,'campaign':self})
		
		if self.is_redpine_approved and not self.was_redpine_approved:
			for manager in self.timeslot.venue.managers.all():
				Notification.objects.create(
					profile=manager.profile,
					subject_type=2,#VENUE
					text='Someone would like to play at your venue!',
					campaign=self
				)
				mail.show_requested(email=manager.email, data={'venue':self.timeslot.venue,'campaign':self}) 

			for band in self.bands.all():
				if band.owner and band.owner.profile.receives_emails:
					mail.booking_request_internally_approved(email=band.owner.email, data={'user':band.owner,'campaign':self})

		if self.is_venue_approved and not self.was_venue_approved:
			two_days_from_now = datetime.now() + timedelta(days=2)
			thirty_days_before_show = self.timeslot.start_time - timedelta(days=30)
			seven_days_before_show = self.timeslot.start_time - timedelta(days=7)
			two_days_before_show = self.timeslot.start_time - timedelta(days=2)
			one_day_after_show = self.timeslot.start_time + timedelta(days=1)
			thirty_days_after_show = self.timeslot.start_time + timedelta(days=30)

			tasks.promotion_reminder(self.id, schedule=two_days_from_now, queue='show_touchpoints_{}'.format(self.id))
			tasks.one_month_reminder(self.id, schedule=thirty_days_before_show, queue='show_touchpoints_{}'.format(self.id))
			tasks.one_week_reminder(self.id, schedule=seven_days_before_show, queue='show_touchpoints_{}'.format(self.id))
			tasks.day_of_summary(self.id, schedule=two_days_before_show, queue='show_touchpoints_{}'.format(self.id))
			tasks.payouts_reminder(self.id, schedule=one_day_after_show, queue='show_touchpoints_{}'.format(self.id))
			tasks.next_show_reminder(self.id, schedule=thirty_days_after_show, queue='show_touchpoints_{}'.format(self.id))

			tasks.create_reviews(self.id, schedule=one_day_after_show, queue='create_reviews_{}'.format(self.id))

		self.was_redpine_approved = self.is_redpine_approved
		self.was_venue_approved = self.is_venue_approved
		return super(Campaign, self).save(*args, **kwargs)

	def goal(self):
		if self.funding_type == type(self).GOAL_AMOUNT:
			return '{} {}'.format(self.goal_amount, self.timeslot.venue.currency)

		elif self.funding_type == type(self).GOAL_COUNT:
			return '{} sales'.format(self.goal_count)

	def tickets_sold(self):
		""" Returns the total number of tickets that have been purchased """
		count = self.total_count
		if count is None:
			count = Pledge.objects.filter(campaign=self,is_cancelled=False,is_processed=True).values_list('count').aggregate(sum=Sum('count'))['sum'] or 0
			count += AppCardTransaction.objects.filter(campaign=self).values_list('count').aggregate(sum=Sum('count'))['sum'] or 0
			count += AppCashTransaction.objects.filter(campaign=self).values_list('count').aggregate(sum=Sum('count'))['sum'] or 0
			if self.timeslot.end_time < datetime.now():
				self.total_count = count
				self.save()
		return count

	def total_earned(self):
		""" returns the total value of all purchases """
		total = self.total_raised
		if total is None:
			total = Pledge.objects.filter(campaign=self,is_cancelled=False,is_processed=True).values_list('total').aggregate(sum=Sum('total'))['sum'] or 0
			total += AppCardTransaction.objects.filter(campaign=self).values_list('total').aggregate(sum=Sum('total'))['sum'] or 0
			total += AppCashTransaction.objects.filter(campaign=self).values_list('total').aggregate(sum=Sum('total'))['sum'] or 0
			if self.timeslot.end_time < datetime.now():
				self.total_raised = total
				self.save()
		return total

	def check_if_successful(self):
		transactions = Pledge.objects.filter(campaign=self,is_cancelled=False,is_processing_failed=False)
		""" checks whether a campaign is fully funded """
		if self.funding_type == Campaign.GOAL_AMOUNT:
			total_earned = transactions.aggregate(sum=Sum('total'))['sum'] or 0
			return total_earned >= self.timeslot.asking_price

		elif self.funding_type == Campaign.GOAL_COUNT:
			count = transactions.aggregate(sum=Sum('count'))['sum'] or 0
			return count >= self.timeslot.min_headcount

		elif self.funding_type == Campaign.HYBRID:
			total_earned = transactions.aggregate(sum=Sum('total'))['sum'] or 0
			count = transactions.aggregate(sum=Sum('count'))['sum'] or 0
			return (total_earned >= self.timeslot.asking_price and count >= self.timeslot.min_headcount)
		else:
			raise Exception('campaign has unknown funding_type')

	def get_attendee_csv(self):
		transactions = Pledge.objects.filter(campaign=self, is_cancelled=False).order_by('user')
		rows = [['Ticket Number', 'First Name', 'Last Name', 'Going to See']]

		for transaction in transactions:
			for ticket in transaction.tickets.all():
				going_to_see_names = [band.band.name for band in transaction.bands.all()]
				going_to_see = ', '.join(going_to_see_names)
				row = [str(ticket.id), transaction.user.first_name, transaction.user.last_name, going_to_see]
				rows.append(row)
		rows.append([''])
		rows.append(['*This list excludes any door sales handled by the RedPine mobile app.'])

		return quote('\n'.join(line for line in [','.join(row) for row in rows]))

	def get_attendee_csv_anchor(self):
		""" This is used for adding a link in the admin panel """
		csv_data = self.get_attendee_csv()
		url = 'data:application/csv,{}'.format(csv_data)
		label = 'Get Attendee List'
		return build_anchor(url=url, label=label, target='_blank', filename='attendee-list.csv')

	def campaign_page(self):
		""" This is used for adding a link in the admin panel """
		url = settings.REDPINE_WEBAPP_URLS['SHOW'](self.id)
		return mark_safe('<a href="{}" target="_blank">View Campaign</a>'.format(url))

	def campaign_feed(self):
		""" This is used for adding a link in the admin panel """
		url = settings.REDPINE_WEBAPP_URLS['SHOW_HUB'](self.id)
		return mark_safe('<a href="{}" target="_blank">View Feed</a>'.format(url))

	def campaign_sales(self):
		""" This is used for adding a link in the admin panel """
		url = settings.REDPINE_WEBAPP_URLS['SHOW_STATS'](self.id)
		return mark_safe('<a href="{}" target="_blank">View Sales</a>'.format(url))

	def _generate_door_code(self):
		while True:
			code = ''.join([str(random.randint(0, 9)) for i in range(6)])
			if not Campaign.objects.filter(door_code=code).exists():
				break
		return code


class CampaignFeed(ArchiveOnDelete, TimeStampedModel):
	# ITEM TYPES
	NOTIFICATION = 0
	MESSAGE = 1

	ITEM_TYPES = (
		(NOTIFICATION, 'NOTIFICATION'),
		(MESSAGE, 'MESSAGE'),
	)

	campaign = models.ForeignKey('Campaign', related_name='feed')
	sender = models.ForeignKey(User, null=True, default=None)
	sent_notification = models.BooleanField(default=False)
	is_system = models.BooleanField(default=True)
	item_type = models.IntegerField(choices=ITEM_TYPES, default=NOTIFICATION)
	text = models.CharField(max_length=1000)
	created_date = models.DateTimeField(auto_now_add=True, null=True)


class TourCampaign(TimeStampedModel):
	campaign = models.ForeignKey('Campaign', on_delete=models.CASCADE)
	tour = models.ForeignKey('Tour', on_delete=models.CASCADE)

	class Meta:
		ordering = ['campaign__timeslot__start_time']


class Tour(TimeStampedModel):
	title = models.CharField(max_length=200, db_index=True)
	headliner = models.ForeignKey('Band')
	campaigns = models.ManyToManyField('Campaign', related_name='tours', through='TourCampaign')
	created_by = models.ForeignKey(User, related_name='tours')


class Transaction(TimeStampedModel):
	class Meta:
		abstract = True

	campaign = models.ForeignKey('Campaign', db_index=True)
	bands = models.ManyToManyField('CampaignBand', verbose_name='Going to see')
	total = MONEY_FIELD(verbose_name='Total purchase amount', help_text='The total amount that the user has spent')
	count = models.IntegerField(verbose_name='Number of tickets', help_text='The number of tickets the user will receive should the campaign succeed')
	redpine_fee = MONEY_FIELD(default=0.00, verbose_name='RedPine\'s fee', help_text='The amount that the user has paid to RedPine')
	payouts_processed = models.BooleanField(default=False, help_text='Whether or not the funds from this transaction have already been distributed to performers.')
	created_date = models.DateTimeField(auto_now_add=True, null=True)


class Pledge(Transaction):#Or "WebTransaction"
	user = models.ForeignKey(User, related_name='transactions')
	square_customer = models.ForeignKey(square_models.Customer, null=True)
	promoter = models.ForeignKey(User, related_name='ticket_sales', null=True, default=None, blank=True, help_text='The user recieving a promoter cut, if any.')
	is_cancelled = models.BooleanField(default=False)
	is_real = models.BooleanField(default=True, help_text='Pledges are created for direct-ticketed events, but they shouldn\'t be visible in the UI as such.')
	is_processed = models.BooleanField(default=False)
	is_processing_failed = models.BooleanField(default=False)

	def __str__(self):
		return self.user.username + " (" + str(self.total) + ") - " + self.campaign.title

	def stripe_customer_anchor(self):
		""" This is used for adding a link in the admin panel """
		url = get_admin_url_for_model(self.customer, id = self.customer.id)
		return build_anchor(url=url, label='View Customer', target='_blank')

	def user_anchor(self):
		""" This is used for adding a link in the admin panel """
		url = get_admin_url_for_model(self.user, id = self.user.id)
		return build_anchor(url=url, label=self.user.username, target='_blank')
	user_anchor.short_description = 'User'
	
	class Meta:
		verbose_name_plural = 'Transactions (Web)'


class AppTransaction(Transaction):
	processed_by = models.ForeignKey(User, on_delete=models.CASCADE, help_text='The user who processed the transaction')
	
	class Meta:
		abstract = True


class AppCardTransaction(AppTransaction):
	transaction_id = models.CharField(max_length=100, help_text='The transaction ID that was created in Square', null=True, blank=True)
	client_transaction_id = models.CharField(max_length=100, help_text='The client transaction ID that was created in Square', null=True, blank=True)
	
	class Meta:
		verbose_name_plural = 'Transactions (App) (Card)'


class AppCashTransaction(AppTransaction):
	pass 
	
	class Meta:
		verbose_name_plural = 'Transactions (App) (Cash)'


class Purchase(TimeStampedModel):
	item = models.ForeignKey('PurchaseItem', on_delete=models.CASCADE, help_text='The specific item purchased.')
	quantity = models.IntegerField(help_text='The number of purchased items of this type.')

	class Meta:
		abstract = True


class PledgePurchase(Purchase):#ie. WebTransactionPurchase
	transaction = models.ForeignKey(Pledge, related_name='purchases')


class AppCardTransactionPurchase(Purchase):
	transaction = models.ForeignKey(AppCardTransaction, related_name='purchases')


class AppCashTransactionPurchase(Purchase):
	transaction = models.ForeignKey(AppCashTransaction, related_name='purchases')
	

class PurchaseItem(TimeStampedModel):
	name = models.CharField(max_length=200)
	description = models.TextField(max_length=500, null=True, blank=True)
	price = MONEY_FIELD(help_text='The amount to charge for this item')
	quantity = models.IntegerField(default=100, help_text='The number of this item available for sale.', validators=[validators.non_negative])
	campaign = models.ForeignKey(Campaign, related_name='purchase_options', on_delete=models.CASCADE)
	is_ticket = models.BooleanField(default=False)
	is_hidden = models.BooleanField(default=False)

	def __str__(self):
		return str(self.name) + " (" + str(self.price) + ") - " + str(self.campaign.title)


class Ticket(TimeStampedModel):
	def generate_ticket_code():
		return secrets.token_hex(8)

	code = models.CharField(max_length=16, help_text='The unique ticket code', default=generate_ticket_code)
	pledge = models.ForeignKey('Pledge', related_name='tickets')
	details = models.ForeignKey('PurchaseItem', null=True, blank=True, default=None)
	attended = models.BooleanField(default=False)

	def __str__(self):
		return str(self.details)


class Scan(TimeStampedModel):
	""" represents a time when a Ticket was scanned by the mobile app """
	ticket = models.ForeignKey(Ticket, related_name='scans')


class OrganizationManager(TimeStampedModel):
	organization = models.ForeignKey('Organization', on_delete=models.CASCADE)
	manager = models.ForeignKey(User, on_delete=models.CASCADE)


class OrganizationBand(TimeStampedModel):
	organization = models.ForeignKey('Organization', on_delete=models.CASCADE)
	band = models.ForeignKey('Band')

	is_accepted = models.NullBooleanField(null=True, default=None, help_text='Has the relation been confirmed by the act?')
	is_application = models.NullBooleanField(null=True, default=None, help_text='Has the relation been confirmed by the organization?')


class Organization(ArchiveOnDelete, TimeStampedModel, Social):
	title = models.CharField(max_length=200, db_index=True)
	description = models.TextField(max_length=5000, null=True, blank=True)
	address = models.CharField(max_length=200)
	account_balance = MONEY_FIELD(null=True, blank=True, default=0.00)
	city = models.ForeignKey('City', related_name='organizations', blank=True, null=True)
	postal_code = models.CharField(max_length=20)
	location = PointField()
	picture = models.ImageField()
	badge = models.ImageField(null=True,blank=True)
	managers = models.ManyToManyField(User, related_name='organizations', through='OrganizationManager')
	bands = models.ManyToManyField('Band', related_name='organizations', through='OrganizationBand')

	created_date = models.DateTimeField(auto_now_add=True, null=True)
	
	def __str__(self):
		return self.title if self.title else ''


class VenueManager(TimeStampedModel):
	venue = models.ForeignKey('Venue', on_delete=models.CASCADE)
	manager = models.ForeignKey(User, on_delete=models.CASCADE)


class Venue(ArchiveOnDelete, TimeStampedModel, Social):
	# CURRENCIES
	CAD = 'CAD'
	USD = 'USD'

	CURRENCY_CHOICES = (
		(CAD, 'CAD'),
		(USD, 'USD'),
	)

	title = models.CharField(max_length=200, db_index=True)
	description = models.TextField(max_length=5000, null=True, blank=True)
	capacity = models.IntegerField(null=True, blank=True)
	address = models.CharField(max_length=200, blank=True, null=True)
	city = models.ForeignKey('City', related_name='venues', blank=True, null=True)
	postal_code = models.CharField(max_length=20, blank=True, null=True)
	location = PointField(geography=True, blank=True, null=True)
	picture = models.ImageField(blank=True, null=True)
	managers = models.ManyToManyField(User, related_name='venues', through='VenueManager')
	currency = models.CharField(choices=CURRENCY_CHOICES, default=CAD, help_text='The currency that the venue operates in', max_length=3)

	genres = models.ManyToManyField('Genre', related_name='venues', blank=True, help_text='The venue\'s genre tags')

	before_booking_info = models.TextField(max_length=5000, default='', blank=True, help_text='Extra info which an act should know before booking the venue. (Markdown)')

	has_fast_reply = models.BooleanField(default=False, help_text='Whether or not the venue replies to messages in a timely manner..')
	is_featured = models.BooleanField(default=False, help_text='Whether to include the venue on the home page or not..')
	is_hidden = models.BooleanField(default=False, help_text='Whether to include the venue in search results or not..')
	is_non_redpine_default = models.BooleanField(default=False, help_text='For ticketed events where the venue is unknown. Like Highlander, there can only be one.')
	is_promotion = models.BooleanField(default=False, help_text='Whether or not RedPine is offering a promotion for bookings.')

	#AMENITIES
	has_wifi = models.BooleanField(default=False)
	is_accessible_by_transit = models.BooleanField(default=False)
	has_atm_nearby = models.BooleanField(default=False)
	has_free_parking_nearby = models.BooleanField(default=False)
	has_paid_parking_nearby = models.BooleanField(default=False)
	is_wheelchair_friendly = models.BooleanField(default=False)
	allows_smoking = models.BooleanField(default=False)
	allows_all_ages = models.BooleanField(default=False)
	has_stage = models.BooleanField(default=False)
	has_microphones = models.BooleanField(default=False)
	has_drum_kit = models.BooleanField(default=False)
	has_piano = models.BooleanField(default=False)
	has_wires_and_cables = models.BooleanField(default=False)
	has_front_load_in = models.BooleanField(default=False)
	has_back_load_in = models.BooleanField(default=False)
	has_soundtech = models.BooleanField(default=False)
	has_lighting = models.BooleanField(default=False)
	has_drink_tickets = models.BooleanField(default=False)
	has_meal_vouchers = models.BooleanField(default=False)
	has_merch_space = models.BooleanField(default=False)
	has_cash_box = models.BooleanField(default=False)
	has_float_cash = models.BooleanField(default=False)

	created_date = models.DateTimeField(auto_now_add=True, null=True)

	class Meta:
		ordering = ['-id']

	def __str__(self):
		return self.title
 

class VenueStats(TimeStampedModel):
	class Meta:
		verbose_name_plural = 'Venue Stats'

	venue = models.OneToOneField(Venue, related_name='stats')

	def historical_headcounts(self):
		today = datetime.now()
		one_week_ago = today - timedelta(days=7)
		two_weeks_ago = today - timedelta(days=14)
		one_month_ago = today - timedelta(days=30)
		two_months_ago = today - timedelta(days=60)

		def headcount_total(period_start, period_end):
			query = {
				'campaign__timeslot__venue': self.venue,
				'campaign__is_venue_approved': True, 
				'campaign__is_redpine_approved': True,
				'campaign__timeslot__start_time__gte': period_start,
				'campaign__timeslot__start_time__lte': period_end
			}

			count = Pledge.objects.filter(**query, is_cancelled=False).values_list('count').aggregate(sum=Sum('count'))['sum'] or 0
			count += AppCardTransaction.objects.filter(**query).values_list('count').aggregate(sum=Sum('count'))['sum'] or 0
			count += AppCashTransaction.objects.filter(**query).values_list('count').aggregate(sum=Sum('count'))['sum'] or 0
			return count

		week_one = headcount_total(one_week_ago, today)
		week_two = headcount_total(two_weeks_ago, one_week_ago)

		month_one = headcount_total(one_month_ago, today)
		month_two = headcount_total(two_months_ago, one_month_ago)

		return {
			'last_week': week_one,
			'last_week_change': week_one - week_two,
			'last_month': month_one,
			'last_month_change': month_one - month_two
		}

class Timeslot(TimeStampedModel):
	class ERRORS:
		OVERLAP = 'A timeslot already exists during this time'
		BOOKED = 'Cannot modify a booked timeslot'
		END_BEFORE_START = 'Timeslot cannot end before it starts'
		END_EQUALS_START = 'Timeslot cannot end when it starts'

	venue = models.ForeignKey(Venue, related_name='timeslots', on_delete=models.CASCADE, null=True)
	asking_price = MONEY_FIELD(default=0.00)
	min_headcount = models.IntegerField(validators=[validators.non_negative], default=0)
	start_time = models.DateTimeField()
	end_time = models.DateTimeField()
	booked = models.BooleanField(default=False)
	created_date = models.DateTimeField(auto_now_add=True, null=True)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.was_booked = self.booked

	def __str__(self):
		return '{} - {} at {}'.format(self.start_time, self.end_time, self.venue)

	def check_if_overlaps_another(self):
		overlap = Timeslot.objects.filter(models.Q(venue=self.venue) & models.Q(models.Q(start_time__lte=self.start_time, end_time__gte=self.end_time) | models.Q(start_time__gte=self.start_time, end_time__lte=self.end_time))).exclude(id=self.id).exclude(booked=False)
		if overlap.count() > 0:
			raise ValidationError(Timeslot.ERRORS.OVERLAP)

	def check_if_end_is_before_start(self):
		if self.end_time < self.start_time:
			raise ValidationError(Timeslot.ERRORS.END_BEFORE_START)

	def check_if_end_equals_start(self):
		if self.end_time == self.start_time:
			raise ValidationError(Timeslot.ERRORS.END_EQUALS_START)

	def raise_if_booked(self):
		if self.was_booked:
			raise ValidationError(Timeslot.ERRORS.BOOKED)

	def clean(self):
		self.check_if_overlaps_another()
		self.check_if_end_is_before_start()
		self.check_if_end_equals_start()

	def save(self, *args, **kwargs):
		self.clean()
		super().save(*args, **kwargs)

	def delete(self, *args, **kwargs):
		self.raise_if_booked()
		super().delete(*args, **kwargs)


class Opening(TimeStampedModel):
	title = models.CharField(max_length=200, default='Opening')
	campaign = models.ForeignKey(Campaign, related_name='opportunities', help_text='The associated open campaign, if applicable.', null=True, blank=True, default=None)
	timeslot = models.ForeignKey(Timeslot, related_name='openings')
	is_open = models.BooleanField(default=False)
	extra_details = models.TextField(max_length=2000, null=True, blank=True, default='Details of this offer have not been publicized. Discuss your arrangement using the Show Hub, upon acceptance.')
	created_date = models.DateTimeField(auto_now_add=True, null=True)

	def __str__(self):
		return '{} - {} at {}'.format(self.timeslot.start_time, self.timeslot.end_time, self.timeslot.venue)


class Event(TimeStampedModel):
	venue = models.ForeignKey(Venue, related_name='events', on_delete=models.CASCADE)
	title = models.CharField(max_length=200, default='Event')
	event_type = models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(3)], default=0)
	start_time = models.DateTimeField()
	end_time = models.DateTimeField()

	def __str__(self):
		return '{} -> {} - {} at {}'.format(self.title,self.start_time, self.end_time, self.venue)


class BookingRequest(TimeStampedModel):
	user = models.ForeignKey(User, related_name='booking_requests', help_text='The user who submitted the request')
	organization = models.ForeignKey(Organization, related_name='booking_requests', default=None, null=True, blank=True, help_text='The organization that submitted the request, if any.')
	venue = models.ForeignKey(Venue, null=True, related_name='requests', on_delete=models.CASCADE, help_text='The venue which is being requested')
	campaign = models.ForeignKey(Campaign, blank=True, null=True, default=None, related_name='first_request')
	followed_up = models.BooleanField(default=False)
	created_date = models.DateTimeField(auto_now_add=True, null=True)
	when = models.TextField(max_length=2000, blank=True, null=True, help_text='When do you want to play?')
	who = models.TextField(max_length=2000, blank=True, null=True, help_text='Who do you want to play with?')
	extra_details = models.TextField(max_length=2000, blank=True, null=True, help_text='Anything else we should know?')

	def campaign_feed(self):
		""" This is used for adding a link in the admin panel """
		if self.campaign:
			url = '{}/campaigns/{}/hub'.format(settings.REDPINE_WEBAPP_BASE_URL, self.campaign.id)
			return mark_safe('<a href="{}" target="_blank">View Feed</a>'.format(url))
		return ''

	def __str__(self):
		if self.followed_up:
			return self.user.email
		else:
			return 'Contact ' + self.user.email


class Subscription(ArchiveOnDelete, TimeStampedModel):
	class Meta:
		abstract = True

	user = models.ForeignKey(User, null=True, blank=True)
	subscribed_date = models.DateTimeField(auto_now_add=True, null=True)


class AccountSubscription(Subscription):
	ARTIST = 'ARTIST'
	VENUE = 'VENUE'
	ORGANIZER = 'ORGANIZER'

	ACCOUNT_TYPES = (
		(ARTIST, 'ARTIST'),
		(VENUE, 'VENUE'),
		(ORGANIZER, 'ORGANIZER'),
	)

	MEMBER = 'MEMBER'
	ULTIMATE = 'ULTIMATE'

	PRODUCT_NAMES = (
		(MEMBER, 'MEMBER'),
		(ULTIMATE, 'ULTIMATE'),
	)

	amount = MONEY_FIELD()
	account_type = models.CharField(choices=ACCOUNT_TYPES, max_length=9)
	product_name = models.CharField(choices=PRODUCT_NAMES, help_text='What level was purchased?',max_length=8)
	square_customer = models.ForeignKey(square_models.Customer, null=True)
	is_processed = models.BooleanField(default=False)
	is_cancelled = models.BooleanField(default=False)
	is_processing_failed = models.BooleanField(default=False)

	def __str__(self):
		return str(self.amount)+' ('+self.user.email+') '+self.product_name+' '+self.account_type
		
	def save(self, *args, **kwargs):
		profile = self.user.profile
		if self.account_type == 'ARTIST' and not self.is_cancelled:
			if self.product_name == 'MEMBER':
				profile.is_artist=True
				profile.is_member_artist=True
			elif self.product_name == 'ULTIMATE':
				profile.is_artist=True
				profile.is_member_artist=True
				profile.is_ultimate_artist=True
		elif self.is_cancelled:
			if self.product_name == 'MEMBER':
				profile.is_member_artist=False
			elif self.product_name == 'ULTIMATE':
				profile.is_member_artist=False
				profile.is_ultimate_artist=False
		
		if self.account_type == 'VENUE' and not self.is_cancelled:
			if self.product_name == 'MEMBER':
				profile.is_venue=True
				profile.is_member_venue=True
			elif self.product_name == 'ULTIMATE':
				profile.is_venue=True
				profile.is_member_venue=True
				profile.is_ultimate_venue=True
		elif self.is_cancelled:
			if self.product_name == 'MEMBER':
				profile.is_member_venue=False
			elif self.product_name == 'ULTIMATE':
				profile.is_member_venue=False
				profile.is_ultimate_venue=False

		if self.account_type == 'ORGANIZER' and not self.is_cancelled:
			if self.product_name == 'MEMBER':
				profile.is_member_organizer=True
				profile.is_member_artist=True
				profile.is_artist=True
				profile.is_member_venue=True
				profile.is_venue=True
		elif self.is_cancelled:
			if self.product_name == 'MEMBER':
				profile.is_member_organizer=False
				profile.is_member_artist=False
				profile.is_member_venue=False
		profile.save()
		return super(AccountSubscription, self).save(*args, **kwargs)


class BandSubscription(Subscription):
	class Meta:
		verbose_name_plural = 'Subscriptions (Bands)'

	band = models.ForeignKey(Band, related_name='subscribers')

class OrganizationSubscription(Subscription):
	class Meta:
		verbose_name_plural = 'Subscriptions (Organizations)'

	organization = models.ForeignKey(Organization, related_name='subscribers')

class VenueSubscription(Subscription):
	class Meta:
		verbose_name_plural = 'Subscriptions (Venues)'

	venue = models.ForeignKey(Venue, related_name='subscribers')


class Review(ArchiveOnDelete, TimeStampedModel):
	class Meta:
		abstract = True

	campaign = models.ForeignKey(Campaign, blank=True, null=True, on_delete=models.CASCADE, help_text='The event for which the review applies.')
	overall = FIVE_STAR_FIELD()
	comment = models.TextField(max_length=2000, blank=True, null=True, help_text='Additional comments for the review.')
	is_completed = models.BooleanField(default=False)
	is_responded = models.BooleanField(default=False)
	created_date = models.DateTimeField(auto_now_add=True, null=True)
	completed_date = models.DateTimeField(blank=True, null=True)
	public_response = models.TextField(max_length=2000, default=None, blank=True, null=True, help_text='A public response to the review.')
	private_response = models.TextField(max_length=2000, default=None, blank=True, null=True, help_text='A private response to the review - just for the reviewer.')

class BandReview(Review):
	class Meta:
		abstract = True

	draw = FIVE_STAR_FIELD(help_text='Did the band accurately represent their draw?')
	communication = FIVE_STAR_FIELD(help_text='Did the band communicate effectively when required?')
	ease_of_working = FIVE_STAR_FIELD(help_text='Was the band easy to work with?')

class VenueReview(Review):
	class Meta:
		abstract = True

	equipment = FIVE_STAR_FIELD(help_text='Did the venue accurately represent the variety and quality of their equipment?')
	communication = FIVE_STAR_FIELD(help_text='Did the venue communicate effectively when required?')
	ease_of_working = FIVE_STAR_FIELD(help_text='Was the venue easy to work with?')

class BandToBandReview(BandReview):
	band = models.ForeignKey(Band, related_name='reviews_by_bands', on_delete=models.CASCADE)
	reviewer = models.ForeignKey(Band, related_name='band_reviews', on_delete=models.CASCADE)
	
	class Meta:
		verbose_name_plural = 'Reviews (Band > Band)'

class BandToVenueReview(VenueReview):
	venue = models.ForeignKey(Venue, related_name='reviews_by_bands', on_delete=models.CASCADE)
	reviewer = models.ForeignKey(Band, related_name='venue_reviews', on_delete=models.CASCADE)
	
	class Meta:
		verbose_name_plural = 'Reviews (Band > Venue)'

class VenueToBandReview(BandReview):
	band = models.ForeignKey(Band, related_name='reviews_by_venues', on_delete=models.CASCADE)
	reviewer = models.ForeignKey(Venue, related_name='band_reviews',on_delete=models.CASCADE)
	
	class Meta:
		verbose_name_plural = 'Reviews (Venue > Band)'

class Hint(TimeStampedModel):
	text = models.CharField(max_length=500)

	def __str__(self):
		return self.text


class Payment(models.Model):
	class Meta:
		abstract = True

	amount = MONEY_FIELD()
	paid = models.BooleanField(default=False)

#ORGANIZATION OR REDPINE TRANSFERS FUNDS TO ACT
#SOURCES: ORGANIZATION PAYOUT, SPLIT_BY_ACT_SALES SHOWS
class ActPayment(ArchiveOnDelete,TimeStampedModel,Payment):
	band = models.ForeignKey('Band')
	campaign = models.ForeignKey('Campaign', null=True, blank=True, default=None)
	organization = models.ForeignKey('Organization', null=True, blank=True, default=None)

	def __str__(self):
		if self.paid:
			return '{} ({}) - {}'.format(self.band.name,self.amount,self.campaign.title if self.campaign else self.organization.title)

#RECORD OF A PAYMENT TO AN ORGANIZATION
#SOURCES: ALL_TO_ORGANIZATION SHOWS
class OrganizationPayment(ArchiveOnDelete,TimeStampedModel,Payment):
	organization = models.ForeignKey('Organization')
	campaign = models.ForeignKey('Campaign')

	def __str__(self):
		if self.paid:
			return '{} ({}) - {}'.format(self.organization.title,self.amount,self.campaign.title)

#RECORD OF A PAYMENT TO A USER
#SOURCES: ALL_TO_ORGANIZER SHOWS, PROMOTER CUTS
class UserPayment(ArchiveOnDelete,TimeStampedModel,Payment):
	band = models.ForeignKey('Band', null=True, blank=True, default=None, help_text='"None" if RedPine pays.')
	campaign = models.ForeignKey('Campaign', null=True, blank=True, default=None, help_text='Populated if the payment is directly from a show.')
	user = models.ForeignKey(User)

	def __str__(self):
		if self.paid:
			return self.user.email + ' was paid ' + ' -> $' + str(self.amount)

#USER REQUEST FOR PAYOUT
class PaymentRequest(ArchiveOnDelete,TimeStampedModel,Payment):
	user = models.ForeignKey(User, related_name='payments')

	def __str__(self):
		if self.paid:
			return self.user.email + ' was paid ' + ' -> $' + str(self.amount)
		else:
			return 'Need to pay -> ' + self.user.email + ': $' + str(self.amount)


class Reward(ArchiveOnDelete,TimeStampedModel,models.Model):
	SIGNUP = 0     
	FIRST_SHOW = 1

	REWARD_TYPES = (
		(SIGNUP, 'SIGNUP'),
		(FIRST_SHOW, 'FIRST_SHOW'),
	)

	amount = MONEY_FIELD(default=0.00)
	subject = models.ForeignKey(User, help_text="The user who must complete the task for rewards to be paid out.", on_delete=models.CASCADE)
	recipient = models.ForeignKey(User, help_text="The user who recieves the reward.", related_name="rewards", on_delete=models.CASCADE)
	reward_type = models.IntegerField(choices=REWARD_TYPES, default=SIGNUP)
	is_completed = models.BooleanField(default=True)

	def __str__(self):
		return '${} {} paid to {} upon {} of {}'.format(str(self.amount), str('was' if self.is_completed else 'will be'),str(self.recipient), str(self.REWARD_TYPES[self.reward_type][1]), str(self.subject))


class GlobalSettings(models.Model):
	homepage_picture = models.ImageField(blank=True, null=True, help_text="The image to display on the homepage. Set to 'None' for a random venue.")
	feed_picture = models.ImageField(blank=True, null=True, help_text="The image to display on the feed.")

	class Meta:
		verbose_name_plural = 'Global Settings'
		ordering = ['-id']

	def __str__(self):
		return 'Settings Configuration'
		

class SurveyQuestion(TimeStampedModel):
	text = models.CharField(max_length=500)

	def __str__(self):
		return self.text
		

class SurveyResponse(TimeStampedModel):
	user = models.ForeignKey(User)
	question = models.ForeignKey('SurveyQuestion', related_name='responses')
	response = models.NullBooleanField(default=None, choices=NULL_BOOLEAN_CHOICES)

	def __str__(self):
		if self.response:
			return self.user.username + ' (y) to ' + self.question.text
		else:
			return self.user.username + ' (n) to ' + self.question.text


class NavigationFeedback(TimeStampedModel):
	created_by = models.ForeignKey(User, null=True, blank=True, default=None)
	category = models.CharField(max_length=100, default='')
	text = models.CharField(max_length=5000, default='')

	def __str__(self):
		return self.text


class JobRunnerCheckin(TimeStampedModel):
	""" 
	This model is just here so the job runner can pick up the last instance & save it, so
	we know it's still alive..
	"""
	pass


class PushToken(TimeStampedModel):
	created_at = models.DateTimeField(auto_now_add=True)
	token = models.CharField(max_length=200, unique=True)
	user = models.ForeignKey(User)
from django.db import models
from django.contrib.auth.models import User
from django_extensions.db.models import TimeStampedModel
from django.contrib.gis.db.models import PointField
from timezone_field import TimeZoneField
from datetime import datetime, timedelta


################
# HELPER STUFF #
################

NULL_BOOLEAN_CHOICES = [
    (None, 'null',),
    (True, 'true',),
    (False, 'false',),
]

def MONEY_FIELD(**kwargs):
    return models.DecimalField(max_digits=6, decimal_places=2, **kwargs)


class ArchiveableManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(archived=False) 


class ArchiveOnDelete(models.Model):
    objects = ArchiveableManager()
    all_objects = models.Manager()
    archived = models.BooleanField(default=False)

    def delete(self, *args, **kwargs):
        self.archived = True
        self.save()

    class Meta:
        abstract = True


####################
# DIMENSION TABLES #
####################


class Country(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'countries'

    def __str__(self):
        return self.name


class Province(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=100)
    province = models.ForeignKey(Province, related_name='cities', null=True)
    country = models.ForeignKey(Country, related_name='cities', null=True)

    core_id = models.IntegerField(null=True, help_text='/Core id value. Helps for generating the dataset.')

    class Meta:
        verbose_name_plural = 'Cities'

    def __str__(self):
        return self.name


class Campaign(ArchiveOnDelete, TimeStampedModel):

    # FUNDING TYPES
    GOAL_AMOUNT = 0
    GOAL_COUNT = 1
    HYBRID = 2

    FUNDING_TYPE_CHOICES = (
        (GOAL_AMOUNT, 'GOAL_AMOUNT'),
        (GOAL_COUNT, 'GOAL_COUNT'),
        (HYBRID, 'HYBRID'),
    )

    # SEATING TYPES
    FIRST_COME_FIRST_SEATING = 0

    SEATING_TYPE_CHOICES = (
        (FIRST_COME_FIRST_SEATING, 'FIRST_COME_FIRST_SEATING'),
    )

    title = models.CharField(max_length=200, null=True)
    goal_amount = MONEY_FIELD(null=True, blank=True)
    goal_count = models.IntegerField(default=0)
    funding_type = models.IntegerField(choices=FUNDING_TYPE_CHOICES, default=HYBRID)
    seating_type = models.IntegerField(choices=SEATING_TYPE_CHOICES, default=FIRST_COME_FIRST_SEATING)
    min_ticket_price = MONEY_FIELD(null=True)
    funding_start = models.DateTimeField(null=True, blank=True)
    funding_end = models.DateTimeField(null=True)
    is_open = models.BooleanField(default=False, help_text='Whether the campaign bands may change or not')
    is_venue_approved = models.NullBooleanField(default=None, help_text='Whether the venue has confirmed the campaign', choices=NULL_BOOLEAN_CHOICES)
    is_successful = models.BooleanField(default=False, help_text='Whether the campaign has been fully funded or not')

    created_by = models.ForeignKey(User, null=True, related_name='campaigns', help_text='The user who created the campaign')
    created_date = models.DateTimeField(null=True, default=None)
    success_date = models.DateTimeField(null=True, blank=True)

    core_id = models.IntegerField(null=True, help_text='/Core id value. Helps for generating the dataset.')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Venue(ArchiveOnDelete, TimeStampedModel):

    # CURRENCIES
    CAD = 'cad'
    USD = 'usd'

    CURRENCY_CHOICES = (
        (CAD, 'CAD'),
        (USD, 'USD'),
    )

    title = models.CharField(max_length=200, null=True)
    capacity = models.IntegerField(null=True)
    address = models.CharField(max_length=200, null=True)
    city = models.ForeignKey(City, related_name='venues', blank=True, null=True)
    postal_code = models.CharField(max_length=20, null=True)
    location = PointField(null=True)
    currency = models.CharField(choices=CURRENCY_CHOICES, default=CAD, help_text='The currency that the venue operates in', max_length=3)
    timezone = TimeZoneField(default='America/Toronto')
    
    core_id = models.IntegerField(null=True, help_text='/Core id value. Helps for generating the dataset.')

    def __str__(self):
        return self.title

    def utcoffset(self):
        delta = self.timezone.utcoffset(datetime.utcnow())
        hour_offset = delta.days * 24 + delta.seconds / 60 / 60
        return hour_offset


class Timeslot(TimeStampedModel):

    venue = models.ForeignKey(Venue, related_name='timeslots', null=True, on_delete=models.CASCADE)
    asking_price = MONEY_FIELD(null=True)
    min_headcount = models.IntegerField(null=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    booked = models.BooleanField(default=False)
    created_date = models.DateTimeField(null=True, default=None)

    core_id = models.IntegerField(null=True, help_text='/Core id value. Helps for generating the dataset.')

    def __str__(self):
        return '{} - {} at {}'.format(self.start_time, self.end_time, self.venue)

    def venue_start_time(self):
        if self.start_time is None: return None
        return self.start_time + timedelta(hours=self.venue.utcoffset())

    def venue_end_time(self):
        if self.end_time is None: return None
        return self.end_time + timedelta(hours=self.venue.utcoffset())

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)


class Band(ArchiveOnDelete, TimeStampedModel):
    name = models.CharField(max_length=200)
    created_by = models.ForeignKey(User, null=True, blank=True, related_name='bands', on_delete=models.CASCADE, help_text='The user that created the band')
    picture = models.ImageField(null=True, blank=True)

    core_id = models.IntegerField(null=True, help_text='/Core id value. Helps for generating the dataset.')

    def __str__(self):
        return self.name


###############
# FACT TABLES #
###############

class Campaign_Fact(ArchiveOnDelete, TimeStampedModel):
	campaign = models.ForeignKey(Campaign, null=True, on_delete=models.CASCADE)
	timeslot = models.ForeignKey(Timeslot, null=True, on_delete=models.CASCADE)
	venue = models.ForeignKey(Venue, null=True, on_delete=models.CASCADE)
	band = models.ForeignKey(Band, null=True, on_delete=models.CASCADE)
	timeslot_listed = models.DateTimeField(null=True)
	campaign_start = models.DateTimeField(null=True)
	campaign_success = models.DateTimeField(null=True)
	is_successful = models.NullBooleanField(null=True, choices=NULL_BOOLEAN_CHOICES)
	goal_count = models.IntegerField(null=True, blank=True)
	gross_sales = MONEY_FIELD(null=True, blank=True)


class Pledge_Fact(ArchiveOnDelete, TimeStampedModel):
	campaign = models.ForeignKey(Campaign, null=True, on_delete=models.CASCADE)
	timeslot = models.ForeignKey(Timeslot, null=True, on_delete=models.CASCADE)
	venue = models.ForeignKey(Venue, null=True, on_delete=models.CASCADE)
	band = models.ForeignKey(Band, null=True, on_delete=models.CASCADE)
	user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
	total = MONEY_FIELD(null=True, blank=True)
	count = models.IntegerField(null=True)
	is_processed = models.BooleanField(default=False)
	is_cancelled = models.BooleanField(default=False)
	created_date = models.DateTimeField(null=True, default=None)


class Timeslot_Fact(ArchiveOnDelete, TimeStampedModel):
    timeslot = models.ForeignKey(Timeslot, null=True, on_delete=models.CASCADE)
    venue = models.ForeignKey(Venue, null=True, on_delete=models.CASCADE)
    asking_price = MONEY_FIELD(null=True)
    min_headcount = models.IntegerField(null=True)
    created_date = models.DateTimeField(null=True)
    campaign = models.ForeignKey(Campaign, default=None, null=True, on_delete=models.CASCADE)
    campaign_success = models.DateTimeField(null=True)
    is_successful = models.NullBooleanField(null=True, choices=NULL_BOOLEAN_CHOICES)
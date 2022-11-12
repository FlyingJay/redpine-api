from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django_extensions.db.models import TimeStampedModel
from django.contrib.gis.db.models import PointField
from django.utils.html import mark_safe
from square import models as square_models
from internal import validators
from internal.models import ArchiveOnDelete 
from core.models import Genre, City
from datetime import timedelta, datetime


def MONEY_FIELD(**kwargs):
    return models.DecimalField(max_digits=6, decimal_places=2, validators=[validators.non_negative], **kwargs)


####################
# INCONCERT MODELS #
####################

class Subscription(TimeStampedModel):
    user = models.ForeignKey(User, null=True, blank=True, related_name='inconcert_subscriptions')
    square_customer = models.ForeignKey(square_models.Customer, null=True)
    
    is_processed = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    is_processing_failed = models.BooleanField(default=False)

    created_date = models.DateTimeField(auto_now_add=True)    


class Profile(TimeStampedModel):
    user = models.OneToOneField(User, related_name='inconcert_profile')
    referrer = models.ForeignKey(User, related_name='inconcert_referrals', null=True, blank=True, default=None, help_text='The user who invited this user to inConcert, if any.')

    premium_months = models.IntegerField(default=0)
    has_lifetime_membership = models.BooleanField(default=False)

    def eligible_for_lifetime_membership(self):
        return (datetime.now() - self.created).days < 7#days       

    def referral_count(self):
        return self.user.inconcert_referrals.count()

    def has_membership(self):
        return self.has_lifetime_membership or self.premium_months > 0

    def referral_url(self):
        return '{}/register?referrer={}'.format(settings.INCONCERT_WEBAPP_BASE_URL, self.user.id)

    def __str__(self):
        return self.user.email


class ContactInfo(models.Model):
    class Meta:
        abstract = True

    email = models.CharField(max_length=200, blank=True, null=True, default=None)
    phone = models.CharField(max_length=200, blank=True, null=True, default=None)

    facebook = models.URLField(blank=True, null=True, default=None)
    messenger = models.URLField(blank=True, null=True, default=None)
    twitter = models.URLField(blank=True, null=True, default=None)
    instagram = models.URLField(blank=True, null=True, default=None)
    spotify = models.URLField(blank=True, null=True, default=None)
    soundcloud = models.URLField(blank=True, null=True, default=None)
    bandcamp = models.URLField(blank=True, null=True, default=None)
    youtube = models.URLField(blank=True, null=True, default=None)
    website = models.URLField(blank=True, null=True, default=None)


class Venue(ArchiveOnDelete, TimeStampedModel, ContactInfo):
    name = models.CharField(max_length=200)
    picture = models.URLField(default=None, blank=True, null=True)
    description = models.CharField(max_length=10000, null=True, blank=True)
    genres = models.ManyToManyField(Genre, related_name='inconcert_venues', blank=True, help_text='The venue\'s genre tags')
    likes = models.IntegerField(default=None, blank=True, null=True, help_text='Computed like count.')

    location = PointField(geography=True, blank=True, null=True, help_text='A pair of location coordinates.')
    location_text = models.CharField(max_length=200, blank=True, null=True, help_text='Raw location text, as extracted.')

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    import_data = models.ForeignKey('VenueImport', default=None, null=True, blank=True, help_text='Raw fields from extraction.')

    def __str__(self):
        return self.name


class Artist(ArchiveOnDelete, TimeStampedModel, ContactInfo):
    #POPULARITY
    NO_INFO = 0
    SUPER_LOCAL = 1
    LOCAL = 2
    INDIE = 3
    POPULAR = 4
    LEGEND = 5

    name = models.CharField(max_length=200)
    picture = models.URLField(default=None, blank=True, null=True)
    description = models.CharField(max_length=10000, null=True, blank=True)
    genres = models.ManyToManyField(Genre, related_name='inconcert_artists', blank=True, help_text='The artist\'s genre tags')
    likes = models.IntegerField(default=None, blank=True, null=True, help_text='Computed like count.')

    location = PointField(geography=True, blank=True, null=True, help_text='A pair of location coordinates.')
    location_text = models.CharField(max_length=200, blank=True, null=True, help_text='Raw location text, as extracted.')

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    import_data = models.ForeignKey('ArtistImport', default=None, null=True, blank=True, help_text='Raw fields from extraction.')

    def __str__(self):
        return self.name


class Event(ArchiveOnDelete, TimeStampedModel):
    link = models.URLField(blank=True, null=True, default=None, help_text='Link to facebook event.')

    artists = models.ManyToManyField('Artist', related_name='events', blank=True, help_text='The event\'s performer(s)')
    venues = models.ManyToManyField('Venue', related_name='events', blank=True, help_text='The event\'s venue(s)')

    name = models.CharField(max_length=200, default=None, null=True, blank=True, help_text='Not used.')
    picture = models.URLField(default=None, blank=True, null=True, help_text='Not used.')
    description = models.CharField(max_length=10000, null=True, blank=True, help_text='Not used.')
    
    start = models.DateTimeField(default=None, null=True, blank=True, help_text='Not used.')
    end = models.DateTimeField(default=None, null=True, blank=True, help_text='Not used.')

    fans_went = models.IntegerField(default=None, blank=True, null=True, help_text='Count of fans who attended. Not used.')
    fans_interested = models.IntegerField(default=None, blank=True, null=True, help_text='Count of fans who showed interest. Not used.')

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name if self.name else self.link


class UserQuery(ArchiveOnDelete, TimeStampedModel):
    ARTIST = 0
    VENUE = 1

    MODELS = (
        (ARTIST, 'ARTIST'),
        (VENUE, 'VENUE'),
    )

    user = models.ForeignKey(User, null=True, default=None, related_name='queries', help_text='The user who submitted the request.')
    model = models.IntegerField(choices=MODELS, default=ARTIST)

    genre = models.ForeignKey(Genre, related_name='queries', null=True, default=None)
    city = models.ForeignKey(City, related_name='queries', null=True, default=None)
    name = models.CharField(max_length=200, null=True, default=None)
    results_count = models.IntegerField(null=True, default=None)


class VenueUpdate(ArchiveOnDelete, TimeStampedModel, ContactInfo):
    venue = models.ForeignKey(Venue, related_name='updates', help_text='The venue to be updated.')
    is_applied = models.BooleanField(default=False)

    name = models.CharField(max_length=200, default=None, blank=True, null=True)
    picture = models.URLField(default=None, blank=True, null=True)
    description = models.CharField(max_length=10000, default=None, null=True, blank=True)
    location_text = models.CharField(max_length=200, default=None, blank=True, null=True)
    genres = models.ManyToManyField(Genre, blank=True, help_text='The venue\'s genre tags')

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.venue.name


class ArtistUpdate(ArchiveOnDelete, TimeStampedModel, ContactInfo):
    artist = models.ForeignKey(Artist, related_name='updates', help_text='The artist to be updated.')
    is_applied = models.BooleanField(default=False)

    name = models.CharField(max_length=200, default=None, blank=True, null=True)
    picture = models.URLField(default=None, blank=True, null=True)
    description = models.CharField(max_length=10000, default=None, null=True, blank=True)
    location_text = models.CharField(max_length=200, default=None, blank=True, null=True)
    genres = models.ManyToManyField(Genre, blank=True, help_text='The artist\'s genre tags')

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.artist.name


#####################
# IMPORT/ETL MODELS #
#####################

class EventImport(TimeStampedModel):
    name = models.TextField(default="", null=True, blank=True)
    profile_link = models.TextField(default="", null=True, blank=True)
    event_link = models.TextField(default="", null=True, blank=True)

    is_imported = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "(Import) Events"


class ArtistImport(TimeStampedModel):
    name = models.TextField(default="", null=True, blank=True)
    page_types = models.TextField(default="", null=True, blank=True)
    likes = models.TextField(default="", null=True, blank=True)
    page_created = models.TextField(default="", null=True, blank=True)
    facebook = models.TextField(default="", null=True, blank=True)
    instagram = models.TextField(default="", null=True, blank=True)
    twitter = models.TextField(default="", null=True, blank=True)
    spotify = models.TextField(default="", null=True, blank=True)
    soundcloud = models.TextField(default="", null=True, blank=True)
    bandcamp = models.TextField(default="", null=True, blank=True)
    youtube = models.TextField(default="", null=True, blank=True)
    email = models.TextField(default="", null=True, blank=True)
    website = models.TextField(default="", null=True, blank=True)
    phone = models.TextField(default="", null=True, blank=True)
    image = models.TextField(default="", null=True, blank=True)
    address = models.TextField(default="", null=True, blank=True)
    story = models.TextField(default="", null=True, blank=True)
    about = models.TextField(default="", null=True, blank=True)
    price_range = models.TextField(default="", null=True, blank=True)
    artists_we_also_like = models.TextField(default="", null=True, blank=True)
    general_information = models.TextField(default="", null=True, blank=True)
    public_transit = models.TextField(default="", null=True, blank=True)
    founding_date = models.TextField(default="", null=True, blank=True)
    impressum = models.TextField(default="", null=True, blank=True)
    attire = models.TextField(default="", null=True, blank=True)
    culinary_team = models.TextField(default="", null=True, blank=True)
    mission = models.TextField(default="", null=True, blank=True)
    company_overview = models.TextField(default="", null=True, blank=True)
    products = models.TextField(default="", null=True, blank=True)
    awards = models.TextField(default="", null=True, blank=True)
    band_interests = models.TextField(default="", null=True, blank=True)
    personal_interests = models.TextField(default="", null=True, blank=True)
    general_manager = models.TextField(default="", null=True, blank=True)
    hometown = models.TextField(default="", null=True, blank=True)
    press_contact = models.TextField(default="", null=True, blank=True)
    booking_agent = models.TextField(default="", null=True, blank=True)
    affiliation = models.TextField(default="", null=True, blank=True)
    personal_information = models.TextField(default="", null=True, blank=True)
    genre = models.TextField(default="", null=True, blank=True)
    accessibility_info = models.TextField(default="", null=True, blank=True)
    biography = models.TextField(default="", null=True, blank=True)
    gender = models.TextField(default="", null=True, blank=True)
    network = models.TextField(default="", null=True, blank=True)
    misc = models.TextField(default="", null=True, blank=True)
    influences = models.TextField(default="", null=True, blank=True)
    current_location = models.TextField(default="", null=True, blank=True)
    record_label = models.TextField(default="", null=True, blank=True)
    band_members = models.TextField(default="", null=True, blank=True)
    members = models.TextField(default="", null=True, blank=True)
    release_date = models.TextField(default="", null=True, blank=True)
    season = models.TextField(default="", null=True, blank=True)
    plot_outline = models.TextField(default="", null=True, blank=True)
    schedule = models.TextField(default="", null=True, blank=True)
    directed_by = models.TextField(default="", null=True, blank=True)
    written_by = models.TextField(default="", null=True, blank=True)
    starring = models.TextField(default="", null=True, blank=True)

    is_imported = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "(Import) Artists"


class VenueImport(TimeStampedModel):
    name = models.TextField(default="", null=True, blank=True)
    page_types = models.TextField(default="", null=True, blank=True)
    likes = models.TextField(default="", null=True, blank=True)
    page_created = models.TextField(default="", null=True, blank=True)
    facebook = models.TextField(default="", null=True, blank=True)
    instagram = models.TextField(default="", null=True, blank=True)
    twitter = models.TextField(default="", null=True, blank=True)
    spotify = models.TextField(default="", null=True, blank=True)
    soundcloud = models.TextField(default="", null=True, blank=True)
    bandcamp = models.TextField(default="", null=True, blank=True)
    youtube = models.TextField(default="", null=True, blank=True)
    email = models.TextField(default="", null=True, blank=True)
    website = models.TextField(default="", null=True, blank=True)
    phone = models.TextField(default="", null=True, blank=True)
    image = models.TextField(default="", null=True, blank=True)
    address = models.TextField(default="", null=True, blank=True)
    story = models.TextField(default="", null=True, blank=True)
    about = models.TextField(default="", null=True, blank=True)
    price_range = models.TextField(default="", null=True, blank=True)
    artists_we_also_like = models.TextField(default="", null=True, blank=True)
    general_information = models.TextField(default="", null=True, blank=True)
    public_transit = models.TextField(default="", null=True, blank=True)
    founding_date = models.TextField(default="", null=True, blank=True)
    impressum = models.TextField(default="", null=True, blank=True)
    attire = models.TextField(default="", null=True, blank=True)
    culinary_team = models.TextField(default="", null=True, blank=True)
    mission = models.TextField(default="", null=True, blank=True)
    company_overview = models.TextField(default="", null=True, blank=True)
    products = models.TextField(default="", null=True, blank=True)
    awards = models.TextField(default="", null=True, blank=True)
    band_interests = models.TextField(default="", null=True, blank=True)
    personal_interests = models.TextField(default="", null=True, blank=True)
    general_manager = models.TextField(default="", null=True, blank=True)
    hometown = models.TextField(default="", null=True, blank=True)
    press_contact = models.TextField(default="", null=True, blank=True)
    booking_agent = models.TextField(default="", null=True, blank=True)
    affiliation = models.TextField(default="", null=True, blank=True)
    personal_information = models.TextField(default="", null=True, blank=True)
    genre = models.TextField(default="", null=True, blank=True)
    accessibility_info = models.TextField(default="", null=True, blank=True)
    biography = models.TextField(default="", null=True, blank=True)
    gender = models.TextField(default="", null=True, blank=True)
    network = models.TextField(default="", null=True, blank=True)
    misc = models.TextField(default="", null=True, blank=True)
    influences = models.TextField(default="", null=True, blank=True)
    current_location = models.TextField(default="", null=True, blank=True)
    record_label = models.TextField(default="", null=True, blank=True)
    band_members = models.TextField(default="", null=True, blank=True)
    members = models.TextField(default="", null=True, blank=True)
    release_date = models.TextField(default="", null=True, blank=True)
    season = models.TextField(default="", null=True, blank=True)
    plot_outline = models.TextField(default="", null=True, blank=True)
    schedule = models.TextField(default="", null=True, blank=True)
    directed_by = models.TextField(default="", null=True, blank=True)
    written_by = models.TextField(default="", null=True, blank=True)
    starring = models.TextField(default="", null=True, blank=True)

    is_imported = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "(Import) Venues"


from django.db import models
from django.contrib.auth.models import User
from django_extensions.db.models import TimeStampedModel
from django.contrib.gis.db.models import PointField
from django.utils.html import mark_safe


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


class Venue(ArchiveOnDelete, TimeStampedModel):
    core_id = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField(max_length=5000, null=True, blank=True)
    capacity = models.IntegerField(null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    city = models.ForeignKey('City', related_name='venues', blank=True, null=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    location = PointField(null=True, blank=True)
    primary_genre = models.ForeignKey('Genre', related_name='primary_venues', blank=True, null=True)
    secondary_genre = models.ForeignKey('Genre', related_name='secondary_venues', blank=True, null=True)

    email_address = models.CharField(max_length=200, blank=True, null=True, default=None)

    website = models.URLField(blank=True, null=True, default=None)
    facebook = models.URLField(blank=True, null=True, default=None)
    twitter = models.URLField(blank=True, null=True, default=None)
    instagram = models.URLField(blank=True, null=True, default=None)
    spotify = models.URLField(blank=True, null=True, default=None)
    soundcloud = models.URLField(blank=True, null=True, default=None)
    bandcamp = models.URLField(blank=True, null=True, default=None)
    youtube = models.URLField(blank=True, null=True, default=None)

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
    
    def __str__(self):
        return self.title

    def province(self):
        if self.city:
            if self.city.province:
                return self.city.province.name
        return 'n/a'

    def facebook_link(self):
        """ This is used for adding a link in the admin panel """
        if self.facebook:
            return mark_safe('<a href="{}" target="_blank">Facebook Page</a>'.format(self.facebook))
        return 'No facebook info.'

    def website_link(self):
        """ This is used for adding a link in the admin panel """
        if self.website:
            return mark_safe('<a href="{}" target="_blank">Visit Website</a>'.format(self.website))
        return 'No website.'

    def website_embed(self):
        """ This is used for adding a link in the admin panel """
        if self.website:
            return mark_safe('<iframe src="{}" width="95%" height="900px" frameBorder="0"/>'.format(self.website))
        return 'No website.'

class Genre(TimeStampedModel):
    core_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Country(models.Model):
    core_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Countries'

    def __str__(self):
        return self.name


class Province(models.Model):
    core_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, related_name='provinces')

    class Meta:
        verbose_name_plural = 'Provinces'

    def __str__(self):
        return self.name


class City(models.Model):
    core_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=100)
    province = models.ForeignKey(Province, related_name='cities')

    class Meta:
        verbose_name_plural = 'Cities'

    def __str__(self):
        return self.name
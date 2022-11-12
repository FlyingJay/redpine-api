import rest_framework_filters as filters
from django.contrib.auth.models import User
from core import models
from django.db.models import Q
from datetime import datetime


class GenreFilter(filters.FilterSet):
    like = filters.CharFilter(name='like', method='filter_like')

    def filter_like(self, queryset, name, value):
        if queryset.model == models.Genre:
            return queryset.filter(Q(id=value) | Q(genres=value) | Q(genres__genres=value) | Q(genres__genres__genres=value))
        elif queryset.model == models.Campaign:
            return queryset.filter(Q(bands__genres=value) | Q(bands__genres__genres=value) | Q(bands__genres__genres__genres=value) | Q(bands__genres__genres__genres__genres=value))
        elif queryset.model == models.Opening:
            return queryset.filter(Q(timeslot__venue__genres=value) | Q(timeslot__venue__genres__genres=value) | Q(timeslot__venue__genres__genres__genres=value) | Q(timeslot__venue__genres__genres__genres__genres=value))
        else:
            return queryset.filter(Q(genres=value) | Q(genres__genres=value) | Q(genres__genres__genres=value) | Q(genres__genres__genres__genres=value))

    class Meta:
        model = models.Genre
        fields = { 
            'name': ['exact'],
        }


class CountryFilter(filters.FilterSet):
    class Meta:
        model = models.Country
        fields = {
            'id': ['exact','in'],
            'name': ['icontains']
        }


class ProvinceFilter(filters.FilterSet):
    country = filters.RelatedFilter(CountryFilter, queryset=models.Country.objects.all())

    class Meta:
        model = models.Province
        fields = {
            'id': ['exact','in'],
            'name': ['icontains']
        }


class CityFilter(filters.FilterSet):
    province = filters.RelatedFilter(ProvinceFilter, queryset=models.Province.objects.all())

    class Meta:
        model = models.City
        fields = {
            'id': ['exact','in'],
            'name': ['icontains'],
        }


class ProfileFilter(filters.FilterSet):
    class Meta:
        model = models.Profile
        fields = {
            'is_artist': ['exact'],
            'is_venue': ['exact']
        }


class UserFilter(filters.FilterSet):
    profile = filters.RelatedFilter(ProfileFilter, queryset=models.Profile.objects.all())
    name = filters.CharFilter(name='name', method='filter_name')

    def filter_name(self, queryset, name, value):
      return queryset.filter(Q(first_name__icontains=value) | Q(last_name__icontains=value))
    
    class Meta:
        model = User
        fields = {
            'id': ['exact', 'in', 'startswith'],
            'email': ['exact']
        }


class OrganizationFilter(filters.FilterSet):
    managers = filters.RelatedFilter(UserFilter, queryset=User.objects.all())
    city = filters.RelatedFilter(CityFilter, queryset=models.City.objects.all())

    class Meta:
        model = models.Organization
        fields = {
            'id': ['exact'],
            'title': ['icontains']
        }


class VenueFilter(filters.FilterSet):
    managers = filters.RelatedFilter(UserFilter, queryset=User.objects.all())
    city = filters.RelatedFilter(CityFilter, queryset=models.City.objects.all())
    genres = filters.RelatedFilter(GenreFilter, queryset=models.Genre.objects.all())

    class Meta:
        model = models.Venue
        fields = {
            'title': ['icontains'],
            'is_featured': ['exact'],
            'is_promotion': ['exact'],
            'is_hidden': ['exact'],
            'capacity': ['gt', 'gte', 'lt', 'lte'],
            
            'has_wifi': ['exact'],
            'is_accessible_by_transit': ['exact'],
            'has_atm_nearby': ['exact'],
            'has_free_parking_nearby': ['exact'],
            'has_paid_parking_nearby': ['exact'],
            'is_wheelchair_friendly': ['exact'],
            'allows_smoking': ['exact'],
            'allows_all_ages': ['exact'],
            'has_stage': ['exact'],
            'has_microphones': ['exact'],
            'has_drum_kit': ['exact'],
            'has_piano': ['exact'],
            'has_wires_and_cables': ['exact'],
            'has_soundtech': ['exact'],
            'has_lighting': ['exact'],
            'has_drink_tickets': ['exact'],
            'has_meal_vouchers': ['exact'],
            'has_merch_space': ['exact'],
            'has_cash_box': ['exact'],
            'has_float_cash': ['exact'],
            'has_fast_reply': ['exact']
        }


class TimeslotFilter(filters.FilterSet):
    venue = filters.RelatedFilter(VenueFilter, queryset=models.Venue.objects.all())

    class Meta:
        model = models.Timeslot
        fields = {
            'id': ['exact'],
            'venue': ['exact'],
            'start_time': ['gt', 'gte', 'lt', 'lte'],
            'end_time': ['gt', 'gte', 'lt', 'lte'],
            'asking_price': ['gt', 'gte', 'lt', 'lte'],
            'booked': ['exact'],
        }


class OpeningFilter(filters.FilterSet):
    timeslot = filters.RelatedFilter(TimeslotFilter, queryset=models.Timeslot.objects.all())

    class Meta:
        model = models.Opening
        fields = {
            'id': ['in', 'exact'],
            'title': ['icontains'],
            'is_open': ['exact'],
        }


class EventFilter(filters.FilterSet):
    venue = filters.RelatedFilter(VenueFilter, queryset=models.Venue.objects.all())

    class Meta:
        model = models.Event
        fields = { 
            'id': ['exact'],
            'start_time': ['gt', 'gte', 'lt', 'lte'],
            'end_time': ['gt', 'gte', 'lt', 'lte'],
            'event_type': ['exact','in'],
        }


class BandFilter(filters.FilterSet):
    hometown = filters.RelatedFilter(CityFilter, queryset=models.City.objects.all())
    genres = filters.RelatedFilter(GenreFilter, queryset=models.Genre.objects.all())
    owner = filters.RelatedFilter(UserFilter, queryset=models.User.objects.all())

    class Meta:
        model = models.Band
        fields = {
            'id': ['in', 'exact'],
            'owner': ['exact'],
            'is_featured': ['exact'],
            'name': ['icontains'],
            'current_city': ['in', 'exact'],
            'is_redpine': ['exact'],
        }


class CampaignFilter(filters.FilterSet):
    bands = filters.RelatedFilter(BandFilter, queryset=models.Band.objects.all())
    organizations = filters.RelatedFilter(OrganizationFilter, queryset=models.Organization.objects.all())
    timeslot = filters.RelatedFilter(TimeslotFilter, queryset=models.Timeslot.objects.all())
    is_venue_approved = filters.ChoiceFilter(null_label='null', choices=((True, 'true',), (False, 'false',),))

    status = filters.CharFilter(name='status', method='filter_status')
    invitations = filters.CharFilter(name='invitations', method='filter_invitations')
    accepted_band = filters.CharFilter(name='accepted_band', method='filter_accepted_band')

    def filter_invitations(self, queryset, name, value):
        if int(value):
            campaigns = models.CampaignBand.objects.filter(band__owner__id=value,is_accepted=None)
            campaign_ids = [c['campaign'] for c in campaigns.values('campaign')]
            return queryset.filter(id__in=campaign_ids)
        else: 
            return queryset

    def filter_accepted_band(self, queryset, name, value):
        if int(value):
            campaigns = models.CampaignBand.objects.filter(band__id=value,is_accepted=True)
            campaign_ids = [c['campaign'] for c in campaigns.values('campaign')]
            return queryset.filter(id__in=campaign_ids)
        else: 
            return queryset

    def filter_status(self, queryset, name, value):
        PENDING_APPROVAL = 1
        REDPINE_APPROVED = 2
        VENUE_APPROVED = 3
        IN_PROGRESS = 4
        FINISHED = 5

        if int(value) == PENDING_APPROVAL:
            return queryset.filter(Q(is_redpine_approved=None) | Q(is_venue_approved=None),timeslot__end_time__gte=datetime.now())
        elif int(value) == REDPINE_APPROVED:
            return queryset.filter(is_redpine_approved=True,timeslot__end_time__gte=datetime.now())
        elif int(value) == VENUE_APPROVED:
            return queryset.filter(is_venue_approved=True,timeslot__end_time__gte=datetime.now())
        elif int(value) == IN_PROGRESS:
            return queryset.filter(is_redpine_approved=True,is_venue_approved=True,timeslot__end_time__gte=datetime.now())
        elif int(value) == FINISHED:
            return queryset.filter(is_redpine_approved=True,is_venue_approved=True,timeslot__end_time__lte=datetime.now())
        else: 
            return queryset

    class Meta:
        model = models.Campaign
        fields = {
            'id': ['in', 'exact'],
            'is_featured': ['exact'],
            'is_successful': ['exact'], 
            'funding_end': ['gte', 'gt', 'lt'],
            'title': ['icontains'],
            'created_by': ['exact'],
            'is_venue_approved': ['exact'],
            'is_open': ['exact'],
            'is_open_mic': ['exact'],
            'min_ticket_price': ['gte', 'lte'],
            'promoter_cut': ['gte', 'lte']
        }


class CampaignFeedFilter(filters.FilterSet):
    campaign = filters.RelatedFilter(CampaignFilter, queryset=models.Campaign.objects.all())
    
    class Meta:
        model = models.CampaignFeed
        fields = {
            'created_date': ['gt']
        }


class WebTransactionFilter(filters.FilterSet):
    user = filters.RelatedFilter(UserFilter, queryset=User.objects.all())
    promoter = filters.RelatedFilter(UserFilter, queryset=User.objects.all())
    campaign = filters.RelatedFilter(CampaignFilter, queryset=models.Campaign.objects.all(), distinct=True)

    class Meta:
        model = models.Pledge
        fields = {
            'id': ['in', 'exact'],
            'is_cancelled': ['exact'],
            'is_processed': ['exact'],
        }


class TicketFilter(filters.FilterSet):
    pledge = filters.RelatedFilter(WebTransactionFilter, queryset=models.Pledge.objects.all())
    
    class Meta:
        model = models.Ticket
        fields = {
            'pledge': ['exact']
        }


class BookingRequestFilter(filters.FilterSet):
    user = filters.RelatedFilter(UserFilter, queryset=User.objects.all())
    venue = filters.RelatedFilter(VenueFilter, queryset=models.Venue.objects.all())
    
    class Meta:
        model = models.BookingRequest
        fields = {
            'id': ['in', 'exact'],
        }


class TourFilter(filters.FilterSet):
    class Meta:
        model = models.Tour
        fields = {
            'id': ['exact','in',],
            'title': ['icontains',],
            'headliner': ['exact',],
            'created_by': ['exact',],
        }


class TourCampaignFilter(filters.FilterSet):
    tour = filters.RelatedFilter(TourFilter, queryset=models.Tour.objects.all())
    campaign = filters.RelatedFilter(CampaignFilter, queryset=models.Campaign.objects.all())
    
    class Meta:
        model = models.TourCampaign
        fields = {
            'id': ['in', 'exact'],
        }


class CampaignBandFilter(filters.FilterSet):
    band = filters.RelatedFilter(BandFilter, queryset=models.Band.objects.all())
    campaign = filters.RelatedFilter(CampaignFilter, queryset=models.Campaign.objects.all())
    
    class Meta:
        model = models.CampaignBand
        fields = {
            'id': ['in', 'exact'],
            'is_accepted': ['exact',],
            'campaign': ['exact','in',],
            'band': ['exact','in',],
        }


class OrganizationBandFilter(filters.FilterSet):
    band = filters.RelatedFilter(BandFilter, queryset=models.Band.objects.all())
    organization = filters.RelatedFilter(OrganizationFilter, queryset=models.Organization.objects.all())
    
    class Meta:
        model = models.OrganizationBand
        fields = {
            'id': ['in', 'exact'],
            'organization': ['exact','in',],
            'band': ['exact','in',],
            'is_accepted': ['exact',],
            'is_application': ['exact',]
        }


class RewardFilter(filters.FilterSet):
    subject = filters.RelatedFilter(UserFilter, queryset=User.objects.all())
    recipient = filters.RelatedFilter(UserFilter, queryset=User.objects.all())
    
    class Meta:
        model = models.Reward
        fields = {
            'id': ['in', 'exact'],
            'recipient': ['exact'],
            'is_completed': ['exact'],
            'reward_type': ['exact'],
        }


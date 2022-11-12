from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from rest_framework import serializers
from expander import ExpanderSerializerMixin #https://github.com/silverlogic/djangorestframework-expander
from drf_extra_fields import fields as drf_extra_fields, geo_fields
from .models import *
from core import fields
from directmessages.models import Message


class CountrySerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = [
            'id',
            'name'
        ]


class ProvinceSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = [
            'id', 
            'name',
            'country'
        ]

        expandable_fields = {
            'country': CountrySerializer
        }


class CitySerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    location = geo_fields.PointField(required=False)

    class Meta:
        model = City
        fields = [
            'id',
            'name',
            'province',
            'location'
        ]

        expandable_fields = {
            'province': ProvinceSerializer
        }


class CreateAccountSubscriptionSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = AccountSubscription
        fields = [
            'id',
            'user',
            'square_customer',
            'account_type',
            'product_name',
            'amount',
            'is_processed'
        ]


class AccountSubscriptionSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = AccountSubscription
        fields = [
            'id',
            'user',
            'account_type',
            'product_name',
            'amount',
            'square_cutomer',
            'is_processed',
            'is_cancelled',
            'subscribed_date'
        ]


class BandSubscriptionSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = BandSubscription
        fields = [
            'id',
            'user',
            'band',
            'subscribed_date'
        ]


class OrganizationSubscriptionSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = OrganizationSubscription
        fields = [
            'id',
            'user',
            'organization',
            'subscribed_date'
        ]


class VenueSubscriptionSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = VenueSubscription
        fields = [
            'id',
            'user',
            'venue',
            'subscribed_date'
        ]


class CampaignDocumentSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    document = fields.Base64FileField(required=True)

    class Meta:
        model = CampaignDocument
        fields = (
            'id',
            'name',
            'document',
            'campaign',
        )


class CampaignPhotoSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = CampaignPhoto
        fields = (
            'id',
            'photo',
        )


class CreateWebTransactionSerializer(serializers.ModelSerializer):
    token = serializers.CharField()
    promoter = serializers.PrimaryKeyRelatedField(required=False, queryset=User.objects.all())

    class Meta:
        model = Pledge
        fields = [
            'id',
            'total',
            'count',
            'campaign',
            'bands',
            'token',
            'promoter',
        ]

        read_only_fields = [
            'token'
        ]


class UserPrivilegedSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
        ]


class UserGhostSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'password',
            'email',
            'first_name',
            'last_name',
        ]


class NotificationSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    band = serializers.PrimaryKeyRelatedField(required=False, queryset=Band.objects.all())
    venue = serializers.PrimaryKeyRelatedField(required=False, queryset=Venue.objects.all())
    campaign = serializers.PrimaryKeyRelatedField(required=False, queryset=Campaign.objects.all())

    class Meta:
        model = Notification
        fields = [
            'id',
            'profile',
            'text',
            'subject_type',
            'is_read',
            'band',
            'venue',
            'campaign',
            'link',
            'created_date'
        ]

        read_only_fields = [
            'id',
            'profile',
            'text',
            'subject_type',
            'is_read',
            'band',
            'venue',
            'campaign'
        ]


class ProfileSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    picture = drf_extra_fields.Base64ImageField(required=False)

    class Meta:
        model = Profile
        fields = [
            'id',
            'is_artist',
            'is_member_artist',
            'is_ultimate_artist',
            'is_venue',
            'is_member_venue',
            'is_ultimate_venue',
            'is_member_organizer',
            'is_email_confirmed',
            'picture',
        ]


class ProfilePrivilegedSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    picture = drf_extra_fields.Base64ImageField(required=False)
    birthdate = serializers.DateTimeField(required=False)
    tawk_hash = serializers.CharField(read_only=True, max_length=64)
    notifications = NotificationSerializer(many=True, read_only=True)

    welcome_add_profile_pic = serializers.BooleanField(required=False)
    welcome_view_my_tickets = serializers.BooleanField(required=False)
    welcome_create_act = serializers.BooleanField(required=False)
    welcome_add_act_socials = serializers.BooleanField(required=False)
    welcome_submit_booking_request = serializers.BooleanField(required=False)
    welcome_create_venue = serializers.BooleanField(required=False)
    welcome_check_calendar = serializers.BooleanField(required=False)
    welcome_add_event = serializers.BooleanField(required=False)
    welcome_approve_booking_request = serializers.BooleanField(required=False)

    class Meta:
        model = Profile
        fields = [
            'id',
            'is_artist',
            'is_member_artist',
            'is_ultimate_artist',
            'is_venue',
            'is_member_venue',
            'is_ultimate_venue',
            'is_member_organizer',
            'is_email_confirmed',
            'picture',
            'account_balance',
            'is_email_confirmed',
            'birthdate',
            'tawk_hash',
            'notifications',
            'has_unread_notifications',
            'referral_url',

            'welcome_add_profile_pic',
            'welcome_view_my_tickets',
            'welcome_create_act',
            'welcome_add_act_socials',
            'welcome_submit_booking_request',
            'welcome_create_venue',
            'welcome_check_calendar',
            'welcome_add_event',
            'welcome_approve_booking_request'
        ]

        read_only_fields = [
            'is_email_confirmed',
            'has_unread_notifications',
            'referral_url'
        ]


class UserSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    profile = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all())

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'profile'
        ]

        expandable_fields = {
            'profile': ProfileSerializer
        }


class GenreSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = [
            'id',
            'name',
            'parents',
        ]


class AdminMailSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = [
            'id',
            'sender',
            'recipient_email',
            'template',
            'data',
            'resend'
        ]


class InvitationSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = [
            'id',
            'template',
            'sender',
            'recipient_email',
            'join_token',
            'is_successful',
            'data'
        ]


class BandSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    short_bio = serializers.CharField(required=False)
    hometown = serializers.PrimaryKeyRelatedField(required=False, queryset=City.objects.all())
    current_city = serializers.PrimaryKeyRelatedField(required=False, queryset=City.objects.all())
    owner = serializers.PrimaryKeyRelatedField(required=False, queryset=User.objects.all())
    picture = drf_extra_fields.Base64ImageField(required=False)
    setlist = serializers.CharField(required=False)
    is_redpine = serializers.BooleanField(required=False)
    is_available = serializers.BooleanField(required=False)
    website = serializers.URLField(required=False, allow_blank=True)
    facebook = serializers.URLField(required=False, allow_blank=True)
    twitter = serializers.URLField(required=False, allow_blank=True)
    instagram = serializers.URLField(required=False, allow_blank=True)
    spotify = serializers.URLField(required=False, allow_blank=True)
    soundcloud = serializers.URLField(required=False, allow_blank=True)
    bandcamp = serializers.URLField(required=False, allow_blank=True)
    youtube = serializers.URLField(required=False, allow_blank=True)
    
    class Meta:
        model = Band
        fields = [
            'id',
            'name',
            'short_bio',
            'genres',
            'hometown',
            'current_city',
            'owner',
            'picture',
            'setlist',
            'is_redpine',
            'is_available',
            'website',
            'facebook',
            'twitter',
            'instagram',
            'spotify',
            'soundcloud',
            'bandcamp',
            'youtube'
        ]

        expandable_fields = {
            'hometown': CitySerializer,
            'genres': (GenreSerializer, (), { 'many': True })
        }


class BandToBandReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = BandToBandReview
        fields = [
            'id',
            'campaign',
            'overall',
            'comment',
            'is_completed',
            'is_responded',
            'created_date',
            'completed_date',
            'public_response',
            'private_response',

            'band',
            'draw',
            'communication',
            'ease_of_working',
            'reviewer'
        ]

        expandable_fields = {
            'reviewer': BandSerializer
        }


class BandToVenueReviewSerializer(serializers.ModelSerializer):
   class Meta:
        model = BandToVenueReview
        fields = [
            'id',
            'campaign',
            'overall',
            'comment',
            'is_completed',
            'is_responded',
            'created_date',
            'completed_date',
            'public_response',
            'private_response',

            'venue',
            'equipment',
            'communication',
            'ease_of_working',
            'reviewer'
        ]

        expandable_fields = {
            'reviewer': BandSerializer
        }


class VenueToBandReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueToBandReview
        fields = [
            'id',
            'campaign',
            'overall',
            'comment',
            'is_completed',
            'is_responded',
            'created_date',
            'completed_date',
            'public_response',
            'private_response',

            'band',
            'draw',
            'communication',
            'ease_of_working',
            'reviewer'
        ]


class OrganizationManagerSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = OrganizationManager
        fields = [
            'id',
            'manager'
        ]

        expandable_fields = {
            'manager': UserSerializer
        }


class VenueManagerSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = VenueManager
        fields = [
            'id',
            'manager'
        ]

        expandable_fields = {
            'manager': UserSerializer
        }


class EventSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    start_time = serializers.DateTimeField(required=False)
    end_time = serializers.DateTimeField(required=False)

    class Meta:
        model = Event
        fields = [
            'id',
            'venue',
            'title',
            'event_type',
            'start_time',
            'end_time'
        ]


class OrganizationBandSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all(), required=False)
    band = serializers.PrimaryKeyRelatedField(queryset=Band.objects.all(), required=False)
    
    class Meta:
        model = OrganizationBand
        fields = [ 
            'id',
            'organization',
            'band',
            'is_accepted',
            'is_application'
        ]

        expandable_fields = {
            'band': BandSerializer
        }


class OrganizationSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    picture = drf_extra_fields.Base64ImageField(required=False)
    badge = fields.Base64FileField(required=False)
    location = geo_fields.PointField(required=False)
    subscribers = serializers.SerializerMethodField()
    
    def get_subscribers(self,obj):
        if 'request' in self.context and isinstance(self.context['request'].user, int): 
            qs = OrganizationSubscription.objects.filter(user=self.context['request'].user)
            serializer = OrganizationSubscriptionSerializer(qs, many=True)
            return serializer.data
        return None

    class Meta:
        model = Organization
        fields = [
            'id',
            'title',
            'description',
            'address',
            'account_balance',
            'picture',
            'badge',
            'website',
            'facebook',
            'twitter',
            'soundcloud',
            'instagram',
            'youtube',
            'managers',
            'city',
            'location',
            'postal_code',
            'subscribers',
            'bands'
        ]

        read_only_fields = [
            'location'
        ]

        expandable_fields = {
            'city': CitySerializer,
            'managers': (OrganizationManagerSerializer, 
                      (), 
                      {'source': 'organizationmanager_set', 'read_only': True, 'many': True},),
            'bands': (OrganizationBandSerializer, 
                      (), 
                      {'source': 'organizationband_set', 'many': True},)
        }


class OrganizationUpdateSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    picture = drf_extra_fields.Base64ImageField(required=False)
    badge = drf_extra_fields.Base64ImageField(required=False)
    location = geo_fields.PointField(required=False)

    class Meta:
        model = Organization
        fields = [
            'id',
            'title',
            'description',
            'address',
            'postal_code',
            'picture',
            'badge',
            'website',
            'facebook',
            'twitter',
            'soundcloud',
            'instagram',
            'youtube',
            'managers',
            'city',
            'location'
        ]

        read_only_fields = [
            'location',
            'city',
            'managers'
        ]

        expandable_fields = {
            'city': CitySerializer
        }


class OrganizationCreateSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    picture = drf_extra_fields.Base64ImageField(required=False)
    badge = drf_extra_fields.Base64ImageField(required=False)
    location = geo_fields.PointField(required=False)

    class Meta:
        model = Organization
        fields = [
            'id',
            'title',
            'description',
            'address',
            'postal_code',
            'picture',
            'badge',
            'managers',
            'city',
            'location'
        ]

        read_only_fields = [
            'location',
            'city',
            'managers'
        ]

        expandable_fields = {
            'city': CitySerializer
        }


class GetOrganizationBandSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all(), required=False)
    band = serializers.PrimaryKeyRelatedField(queryset=Band.objects.all(), required=False)
    
    class Meta:
        model = OrganizationBand
        fields = [ 
            'id',
            'organization',
            'band',
            'is_accepted',
            'is_application'
        ]

        expandable_fields = {
            'band': BandSerializer,
            'organization': OrganizationSerializer
        }


class VenueStatsSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = VenueStats
        fields = [
            'venue',
            'historical_headcounts'
        ]

        read_only_fields = [
            'venue',
            'historical_headcounts'
        ]


class VenueSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    picture = drf_extra_fields.Base64ImageField(required=False)
    location = geo_fields.PointField(required=False)
    subscribers = serializers.SerializerMethodField()
    
    def get_subscribers(self,obj):
        if 'request' in self.context and isinstance(self.context['request'].user, int): 
            qs = VenueSubscription.objects.filter(user=self.context['request'].user)
            serializer = VenueSubscriptionSerializer(qs, many=True)
            return serializer.data
        return None

    class Meta:
        model = Venue
        fields = [
            'id',
            'title',
            'description',
            'capacity',
            'address',
            'picture',
            'website',
            'facebook',
            'twitter',
            'soundcloud',
            'instagram',
            'youtube',
            'managers',
            'city',
            'location',
            'currency',
            'postal_code',
            'events',
            'is_promotion',
            'is_hidden',
            'has_fast_reply',
            'is_non_redpine_default',
            'genres',
            'subscribers',
            'stats',
            'before_booking_info',

            'has_wifi',
            'is_accessible_by_transit',
            'has_atm_nearby',
            'has_free_parking_nearby',
            'has_paid_parking_nearby',
            'is_wheelchair_friendly',
            'allows_smoking',
            'allows_all_ages',
            'has_stage',
            'has_microphones',
            'has_drum_kit',
            'has_piano',
            'has_wires_and_cables',
            'has_front_load_in',
            'has_back_load_in',
            'has_soundtech',
            'has_lighting',
            'has_drink_tickets',
            'has_meal_vouchers',
            'has_merch_space',
            'has_cash_box',
            'has_float_cash'
        ]

        read_only_fields = [
            'location'
        ]

        expandable_fields = {
            'city': CitySerializer,
            'stats': VenueStatsSerializer,
            'genres': (GenreSerializer, (), { 'many': True }),
            'events': (EventSerializer, (), { 'many': True }),
            'managers': (VenueManagerSerializer, 
                      (), 
                      { 'source': 'venuemanager_set', 'read_only': True, 'many': True },),
            'reviews_by_bands': (BandToVenueReviewSerializer, (), { 'many': True }),
            'band_reviews': (VenueToBandReviewSerializer, (), { 'many': True })
        }


class VenueUpdateSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    picture = drf_extra_fields.Base64ImageField(required=False)
    location = geo_fields.PointField(required=False)
    website = serializers.URLField(required=False, allow_blank=True)
    facebook = serializers.URLField(required=False, allow_blank=True)
    twitter = serializers.URLField(required=False, allow_blank=True)
    instagram = serializers.URLField(required=False, allow_blank=True)
    youtube = serializers.URLField(required=False, allow_blank=True)

    class Meta:
        model = Venue
        fields = [
            'id',
            'title',
            'description',
            'capacity',
            'address',
            'postal_code',
            'picture',
            'website',
            'facebook',
            'twitter',
            'instagram',
            'youtube',
            'managers',
            'city',
            'location',
            'currency',
            'genres',
        ]

        read_only_fields = [
            'location',
            'city',
            'managers',
            'currency'
        ]

        expandable_fields = {
            'city': CitySerializer,
            'genres': (GenreSerializer, (), { 'many': True })
        }

class VenueCreateSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    picture = drf_extra_fields.Base64ImageField(required=False)
    location = geo_fields.PointField(required=False)

    class Meta:
        model = Venue
        fields = [
            'id',
            'title',
            'description',
            'capacity',
            'address',
            'postal_code',
            'picture',
            'managers',
            'city',
            'location',
            'currency',
        ]

        read_only_fields = [
            'location',
            'city',
            'managers',
            'currency'
        ]

        expandable_fields = {
            'city': CitySerializer
        }


class TimeslotSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    venue = serializers.PrimaryKeyRelatedField(queryset=Venue.objects.all(), required=False)
    start_time = serializers.DateTimeField(required=False)
    end_time = serializers.DateTimeField(required=False)
    asking_price = serializers.DecimalField(max_digits=6, decimal_places=2, required=False)
    min_headcount = serializers.IntegerField(required=False)

    class Meta:
        model = Timeslot
        fields = [
            'id',
            'venue',
            'asking_price',
            'min_headcount',
            'start_time',
            'end_time',
            'booked'
        ]

        read_only_fields = [
            'booked'
        ]

        expandable_fields = {
            'venue': VenueSerializer
        }


class CampaignBandSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    campaign = serializers.PrimaryKeyRelatedField(queryset=Campaign.objects.all(), required=False)
    band = serializers.PrimaryKeyRelatedField(queryset=Band.objects.all(), required=False)
    is_accepted = serializers.NullBooleanField(required=False)
    is_application = serializers.NullBooleanField(required=False)
    is_headliner = serializers.BooleanField(required=False)
    start_time = serializers.DateTimeField(required=False)
    
    class Meta:
        model = CampaignBand
        fields = [
            'id',
            'is_headliner',
            'is_application',
            'band',
            'campaign',
            'is_accepted',
            'start_time'
        ]

        expandable_fields = {
            'band': BandSerializer
        }


class CampaignOrganizationSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    campaign = serializers.PrimaryKeyRelatedField(queryset=Campaign.objects.all(), required=False)
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all(), required=False)
    can_edit = serializers.BooleanField(required=False)
    is_accepted = serializers.NullBooleanField(required=False)
    
    class Meta:
        model = CampaignBand
        fields = [
            'id',
            'organization',
            'campaign',
            'can_edit',
            'is_accepted'
        ]

        expandable_fields = {
            'organization': OrganizationSerializer
        }


class PurchaseItemSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, required=False)
    quantity = serializers.IntegerField(required=False)
    campaign = serializers.PrimaryKeyRelatedField(queryset=Campaign.objects.all(), required=False)
    is_ticket = serializers.BooleanField(required=False)
    is_hidden = serializers.BooleanField(required=False)

    class Meta:
        model = PurchaseItem
        fields = [
            'id',
            'name',
            'description',
            'price',
            'quantity',
            'campaign',
            'is_ticket',
            'is_hidden'
        ]


class CampaignFeedSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = CampaignFeed
        fields = [
            'id',
            'campaign',
            'sender',
            'is_system',
            'item_type',
            'text',
            'created_date',
            'sent_notification'
        ]

        expandable_fields = {
            'sender': UserSerializer
        }


class CampaignSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    funding_start = serializers.DateTimeField(required=False)
    funding_end = serializers.DateTimeField(required=False)
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    picture = drf_extra_fields.Base64ImageField(required=False)

    class Meta:
        model = Campaign
        fields = (
            'id',
            'created_by',
            'title',
            'description',
            'funding_start',
            'funding_end',
            'hashtag',
            'picture',
            'is_venue_approved',
            'is_redpine_approved',
            'is_successful',
            'is_hold',
            'is_open',
            'is_open_mic',
            'bands',
            'organizations',
            'purchase_options',
            'timeslot',
            'funding_type',
            'payout_type',
            'goal_amount',
            'goal_count',
            'tickets_sold',
            'min_ticket_price',
            'minimum_age',
            'seating_type',
            'total_earned',
            'feed',
            'has_event_page',
            'has_set_order',
            'has_door_plan',
            'has_sound_plan',
            'has_equipment_plan',
            'is_only_tickets',
            'third_party_tickets',
            'promoter_cut',
            'service_fee',
            'facebook_event',
            'discuss_doors',
            'discuss_sound',
            'discuss_equipment'
        )

        expandable_fields = {
            'bands': (CampaignBandSerializer, 
                      (), 
                      {'source': 'campaignband_set', 'read_only': True, 'many': True},),
            'organizations': (CampaignOrganizationSerializer, 
                      (), 
                      {'source': 'campaignorganization_set', 'read_only': True, 'many': True},),
            'timeslot': TimeslotSerializer,
            'documents': (CampaignDocumentSerializer, (), {'many': True}),
            'photos': (CampaignPhotoSerializer, (), {'many': True}),
            'purchase_options': (PurchaseItemSerializer, (), {'many': True}),
            'feed': (CampaignFeedSerializer, (), {'many': True}),
        }

        read_only_fields = [
            'tickets_sold'
        ]

class CampaignCreateSerializer(serializers.Serializer):
    is_open_mic = serializers.BooleanField(required=False)
    
    class Meta:
        fields = (
            'id',
            'title',
            'description',
            'funding_type',
            'funding_start',
            'funding_end',
            'is_venue_approved',
            'is_open',
            'is_open_mic',
            'venue',
            'start_time',
            'end_time',
            'frequency',
            'frequency_count'
        )

    class CampaignCreate(object):
        def __init__(self, **kwargs):
            for field in self.Meta.fields:
                setattr(self, field, kwargs.get(field, None))

    def create(self, validated_data):
        return CampaignCreate(id=None, **validated_data)


class CampaignUpdateSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    title = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    hashtag = serializers.CharField(required=False)
    picture = drf_extra_fields.Base64ImageField(required=False)
    is_hold = serializers.BooleanField(required=False)
    is_open = serializers.BooleanField(required=False)
    is_open_mic = serializers.BooleanField(required=False)
    is_successful = serializers.BooleanField(required=False)
    funding_start = serializers.DateTimeField(required=False)
    funding_end = serializers.DateTimeField(required=False)
    has_event_page = serializers.BooleanField(required=False)
    has_set_order = serializers.BooleanField(required=False)
    has_door_plan = serializers.BooleanField(required=False)
    has_sound_plan = serializers.BooleanField(required=False)
    has_equipment_plan = serializers.BooleanField(required=False)
    third_party_tickets = serializers.URLField(required=False, allow_blank=True)
    promoter_cut = serializers.DecimalField(max_digits=4, decimal_places=2, required=False)
    facebook_event = serializers.URLField(required=False)
    discuss_doors = serializers.CharField(required=False)
    discuss_sound = serializers.CharField(required=False)
    discuss_equipment = serializers.CharField(required=False)

    class Meta:
        model = Campaign
        fields = (
            'id',
            'title',
            'description',
            'hashtag',
            'picture',
            'is_hold',
            'is_open',
            'is_open_mic',
            'is_successful',
            'funding_start',
            'funding_end',
            'has_event_page',
            'has_set_order',
            'has_door_plan',
            'has_sound_plan',
            'has_equipment_plan',
            'third_party_tickets',
            'promoter_cut',
            'facebook_event',
            'discuss_doors',
            'discuss_sound',
            'discuss_equipment'
        )


class OpeningSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    timeslot = serializers.PrimaryKeyRelatedField(queryset=Timeslot.objects.all())
    campaign = serializers.PrimaryKeyRelatedField(queryset=Campaign.objects.all(), required=False)

    class Meta:
        model = Opening
        fields = [
            'id',
            'title',
            'campaign',
            'timeslot',
            'is_open',
            'extra_details'
        ]

        expandable_fields = {
            'campaign': CampaignSerializer,
            'timeslot': TimeslotSerializer
        }


class TourSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    title = serializers.CharField(required=False)
    headliner = serializers.PrimaryKeyRelatedField(queryset=Band.objects.all(), required=False)
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        model = Tour
        fields = [
            'id',
            'title',
            'campaigns',
            'headliner',
            'created_by'
        ]

        expandable_fields = {
            'campaigns': (CampaignSerializer, (), {'many': True}),
        }


class TourCampaignSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = TourCampaign
        fields = [
            'id',
            'tour',
            'campaign'
        ]

        expandable_fields = {
            'campaign': CampaignSerializer,
            'tour': TourSerializer
        }


class WebTransactionPurchaseSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = PledgePurchase
        fields = [
            'id',
            'item',
            'quantity'
        ]

        expandable_fields = {
            'item': PurchaseItemSerializer
        }


class WebTransactionSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Pledge
        fields = [
            'id',
            'total',
            'redpine_fee',
            'count',
            'campaign',
            'bands',
            'is_cancelled',
            'is_processed',
            'is_processing_failed',
            'promoter',
            'purchases'
        ]

        read_only_fields = [
            'count',
            'total',
            'campaign',
            'bands',
            'purchases'
        ]

        expandable_fields = {
            'purchases': (WebTransactionPurchaseSerializer, (), {'many': True},), 
            'bands': (CampaignBandSerializer, (), {'many': True},),
            'campaign': CampaignSerializer, 
            'user': UserSerializer
        }


class ScanSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Scan
        fields = [
            'ticket',
            'created',
        ]


class TicketSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            'id',
            'code',
            'pledge',
            'details',
            'scans',
        ]

        expandable_fields = {
            'pledge': WebTransactionSerializer,
            'details': PurchaseItemSerializer,
            'scans': (ScanSerializer, (), {'many': True},),
        }


class GuestListSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            'id',
            'pledge',
            'details',
            'scans',
            'attended'
        ]

        expandable_fields = {
            'pledge': WebTransactionSerializer,
            'details': PurchaseItemSerializer,
            'scans': (ScanSerializer, (), {'many': True},),
        }


class UpdateGuestListSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            'attended'
        ]


class BookingRequestSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = BookingRequest
        fields = [
            'user',
            'organization',
            'venue',
            'when',
            'who',
            'extra_details'
        ]


class CreateBandSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    hometown = serializers.PrimaryKeyRelatedField(required=False, queryset=City.objects.all())
    owner = serializers.PrimaryKeyRelatedField(required=False, queryset=User.objects.all())
    picture = drf_extra_fields.Base64ImageField(required=False)
    is_redpine = serializers.BooleanField(required=False)
    is_available = serializers.BooleanField(required=False)
    website = serializers.URLField(required=False, allow_blank=True)
    facebook = serializers.URLField(required=False, allow_blank=True)
    twitter = serializers.URLField(required=False, allow_blank=True)
    instagram = serializers.URLField(required=False, allow_blank=True)
    spotify = serializers.URLField(required=False, allow_blank=True)
    soundcloud = serializers.URLField(required=False, allow_blank=True)
    bandcamp = serializers.URLField(required=False, allow_blank=True)
    youtube = serializers.URLField(required=False, allow_blank=True)    
    join_token = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Band
        fields = [
            'id',
            'name',
            'short_bio',
            'genres',
            'hometown',
            'owner',
            'is_redpine',
            'is_available',
            'owner',
            'picture',
            'website',
            'facebook',
            'twitter',
            'instagram',
            'spotify',
            'soundcloud',
            'bandcamp',
            'youtube',
            'join_token'
        ]


class GetBandSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    picture = drf_extra_fields.Base64ImageField(required=False)
    subscribers = serializers.SerializerMethodField()
    
    def get_subscribers(self,obj):
        if 'request' in self.context and isinstance(self.context['request'].user, int): 
            qs = BandSubscription.objects.filter(user=self.context['request'].user)
            serializer = BandSubscriptionSerializer(qs, many=True)
            return serializer.data
        return None

    class Meta:
        model = Band
        fields = [
            'id',
            'name',
            'short_bio',
            'genres',
            'hometown',
            'current_city',
            'setlist',
            'account_balance',
            'is_redpine',
            'is_available',
            'owner',
            'picture',
            'join_token',
            'website',
            'facebook',
            'twitter',
            'instagram',
            'spotify',
            'soundcloud',
            'bandcamp',
            'youtube',
            'reviews_by_bands',
            'reviews_by_venues',
            'band_reviews',
            'venue_reviews',
            'subscribers'
        ]

        expandable_fields = {
            'hometown': CitySerializer,
            'current_city': CitySerializer,
            'genres': (GenreSerializer, (), { 'many': True }),
            'reviews_by_bands': (BandToBandReviewSerializer, (), { 'many': True }),
            'reviews_by_venues': (VenueToBandReviewSerializer, (), { 'many': True }),
            'band_reviews': (BandToBandReviewSerializer, (), { 'many': True }),
            'venue_reviews': (BandToVenueReviewSerializer, (), { 'many': True }),
            'organizations': (GetOrganizationBandSerializer, 
                              (), 
                              {'source': 'organizationband_set', 'read_only': True, 'many': True},),
        }


class JustTicketsSerializer(serializers.Serializer):
    class Meta:
        fields = [
            'title',
            'venue_name',
            'venue_address',
            'date',
            'performers',
            'ticket_price',
            'ticket_quantity',
            'doors_price',
            'doors_quantity',
            'organization'
        ]

    class JustTickets(object):
        def __init__(self, **kwargs):
            for field in ('title', 'venue_name', 'venue_address', 'date', 'performers', 'ticket_price', 'doors_price', 'ticket_quantity', 'doors_quantity','organization'):
                setattr(self, field, kwargs.get(field, None))

    def create(self, validated_data):
        return JustTickets(id=None, **validated_data)


class ShowRequestSerializer(serializers.Serializer):
    class Meta:
        fields = [
            'venue',
            'date',
            'performers',
            'extra_slots',
            'funding_type',
            'ticket_price',
            'doors_price',
            'extra_info',
            'organization',
            'is_open',
            'is_opening'
        ]

    class ShowRequest(object):
        def __init__(self, **kwargs):
            for field in ('venue', 'date', 'performers', 'extra_slots', 'funding_type', 'ticket_price', 'doors_price', 'extra_info', 'organization', 'is_open'):
                setattr(self, field, kwargs.get(field, None))

    def create(self, validated_data):
        return ShowRequest(id=None, **validated_data)


class SurveyResponseSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = SurveyResponse
        fields = [
            'id',
            'user',
            'question',
            'response'
        ]


class HintSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Hint
        fields = [
            'id',
            'text'
        ]


class ActPaymentSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = ActPayment
        fields = [
            'organization',
            'band',
            'amount'
        ]


class UserPaymentSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = UserPayment
        fields = [
            'user',
            'band',
            'amount'
        ]


class PaymentRequestSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = PaymentRequest
        fields = []


class GlobalSettingsSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    homepage_picture = drf_extra_fields.Base64ImageField(required=False)
    feed_picture = drf_extra_fields.Base64ImageField(required=False)

    class Meta:
        model = GlobalSettings
        fields = [
            'id',
            'homepage_picture',
            'feed_picture'
        ]


class RewardSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = [
            'id',
            'amount',
            'recipient',
            'reward_type',
            'is_completed'
        ]


class AppCashTransactionPurchaseSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = AppCashTransactionPurchase
        fields = [
            'item',
            'quantity'
        ]


class AppCashTransactionSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = AppCashTransaction
        fields = [
            'id',
            'total',
            'count',
            'redpine_fee',
            'campaign',
            'bands',
            'processed_by',
            'purchases',
        ]

        read_only_fields = [
            'created_date',
            'purchases'
        ]

        expandable_fields = {
            'purchases': (AppCashTransactionPurchaseSerializer, (), {'many': True},), 
            'bands': (CampaignBandSerializer, (), {'many': True},),
            'campaign': CampaignSerializer, 
            'processed_by': UserSerializer
        }


class AppCardTransactionPurchaseSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = AppCardTransactionPurchase
        fields = [
            'item',
            'quantity'
        ]


class AppCardTransactionSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = AppCardTransaction
        fields = [
            'id',
            'total',
            'count',
            'redpine_fee',
            'campaign',
            'bands',
            'processed_by',
            'purchases',
        ]

        read_only_fields = [
            'created_date',
            'purchases'
        ]

        expandable_fields = {
            'purchases': (AppCardTransactionPurchaseSerializer, (), {'many': True},), 
            'bands': (CampaignBandSerializer, (), {'many': True},),
            'campaign': CampaignSerializer, 
            'processed_by': UserSerializer
        }


class PushTokenSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = PushToken
        fields = [
            'token',
            'user'
        ]


class NavigationFeedbackSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = NavigationFeedback
        fields = [
            'created_by',
            'category',
            'text'
        ]


class MessageSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipient = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Message
        fields = [
            'id',
            'content',
            'sender',
            'recipient',
            'sent_at',
            'read_at',
            'unread'
        ]

        expandable_fields = {
            'sender': UserSerializer,
            'recipient': UserSerializer
        }
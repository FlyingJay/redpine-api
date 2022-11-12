from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from expander import ExpanderSerializerMixin
from rest_framework import serializers
from drf_extra_fields import fields as drf_extra_fields, geo_fields
from analysis.models import *
from analysis import fields


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
            'name'
        ]


class CitySerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = City
        fields = [
            'id',
            'name',
            'province',
            'country'
        ]

        expandable_fields = {
            'province': ProvinceSerializer,
            'country': CountrySerializer
        }


class CampaignSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    created_date = serializers.DateTimeField(required=False)
    funding_start = serializers.DateTimeField(required=False)
    funding_end = serializers.DateTimeField(required=False)
    success_date = serializers.DateTimeField(required=False)
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        model = Campaign
        fields = (
            'id',
            'created_by',
            'created_date',
            'success_date',
            'title',
            'funding_start',
            'funding_end',
            'is_venue_approved',
            'is_successful',
            'is_open',
            'is_open_mic',
            'funding_type',
            'goal_amount',
            'goal_count',
            'min_ticket_price',
            'seating_type',
        )

        read_only_fields = [
            'created_date'
        ]


class VenueSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    location = geo_fields.PointField()
    timezone = fields.TimeZoneField(required=False)
    utc_offset = fields.UTCOffsetField(read_only=True, source='timezone')

    class Meta:
        model = Venue
        fields = [
            'id',
            'title',
            'capacity',
            'address',
            'city',
            'location',
            'currency',
            'timezone',
            'utc_offset',
            'core_id'
        ]

        read_only_fields = [
            'location',
        ]

        expandable_fields = {
            'city': CitySerializer
        }


class TimeslotSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    created_date = serializers.DateTimeField(required=False)

    class Meta:
        model = Timeslot
        fields = [
            'id',
            'venue',
            'asking_price',
            'min_headcount',
            'start_time',
            'end_time',
            'booked',
            'created_date'
        ]

        read_only_fields = [
            'booked',
            'created_date'
        ]

        expandable_fields = {
            'venue': VenueSerializer
        }


class UserSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
        ]


class BandSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        model = Band
        fields = [
            'id',
            'name',
            'created_by',
            'core_id'
        ]

        expandable_fields = {
            'user': UserSerializer
        }


class RelatedBandSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    strength = serializers.SerializerMethodField()

    class Meta:
        model = Band
        fields = [
            'id',
            'name',
            'created_by',
            'picture',
            'core_id',
            'strength'
        ]

        expandable_fields = {
            'user': UserSerializer
        }

    def get_strength(self,obj):
        return obj.strength


class CampaignFactSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    timeslot_listed = serializers.DateTimeField(required=False)
    campaign_start = serializers.DateTimeField(required=False)
    campaign_success = serializers.DateTimeField(required=False)

    class Meta:
        model = Campaign_Fact
        fields = [
            'campaign',
            'timeslot',
            'venue',
            'band',
            'timeslot_listed',
            'campaign_start',
            'campaign_success',
            'is_successful',
            'goal_count',
            'gross_sales'
        ]

        expandable_fields = {
            'campaign': CampaignSerializer,
            'timeslot': TimeslotSerializer,
            'venue': VenueSerializer,
            'band': BandSerializer
        }


class PledgeFactSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    created_date = serializers.DateTimeField(required=False)

    class Meta:
        model = Pledge_Fact
        fields = [
            'campaign',
            'timeslot',
            'venue',
            'band',
            'user',
            'total',
            'count',
            'is_processed',
            'is_cancelled',
            'created_date'
        ]

        expandable_fields = {
            'campaign': CampaignSerializer,
            'timeslot': TimeslotSerializer,
            'venue': VenueSerializer,
            'band': BandSerializer,
            'user': UserSerializer
        }


class TimeslotFactSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    created_date = serializers.DateTimeField(required=False)
    campaign_success = serializers.DateTimeField(required=False)

    class Meta:
        model = Timeslot_Fact
        fields = [
            'timeslot',
            'venue',
            'asking_price',
            'min_headcount',
            'created_date',
            'campaign',
            'campaign_success',
            'is_successful'
        ]

        expandable_fields = {
            'timeslot': TimeslotSerializer,
            'campaign': CampaignSerializer,
            'venue': VenueSerializer
        }
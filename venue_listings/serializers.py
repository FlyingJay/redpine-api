from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from expander import ExpanderSerializerMixin
from rest_framework import serializers
from drf_extra_fields import fields as drf_extra_fields, geo_fields
from venue_listings.models import *


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
        

class CitySerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = City
        fields = [
            'id',
            'core_id',
            'name',
            'province',
        ]


class ProvinceSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = [
            'id',
            'core_id',
            'name',
            'country',
        ]


class CountrySerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = [
            'id',
            'core_id',
            'name',
        ]
        

class VenueSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    location = geo_fields.PointField(required=False)

    class Meta:
        model = Venue
        fields = [
            'id',
            'title',
            'description',
            'capacity',
            'address',
            'website',
            'facebook',
            'twitter',
            'soundcloud',
            'instagram',
            'youtube',
            'city',
            'location',
            'postal_code',
            'primary_genre',
            'secondary_genre',

            'email_address',

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


class VenueUpdateSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
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
            'website',
            'facebook',
            'twitter',
            'soundcloud',
            'instagram',
            'youtube',
            'city',
            'location'
        ]

        read_only_fields = [
            'location'
        ]


class VenueCreateSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
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
            'city',
            'location'
        ]

        read_only_fields = [
            'location'
        ]

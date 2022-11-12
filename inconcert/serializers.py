from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from expander import ExpanderSerializerMixin
from rest_framework import serializers
from drf_extra_fields import fields as drf_extra_fields, geo_fields
from core.serializers import GenreSerializer
from inconcert.models import *


class SubscriptionSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
	class Meta:
		model = Subscription
		fields = [
			'user',
			'square_customer',
			'is_processed',
			'is_cancelled',
			'is_processing_failed',
			'created_date'
		]


class ArtistSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
	picture = drf_extra_fields.Base64ImageField(required=False)
	location = geo_fields.PointField(required=False)

	class Meta:
		model = Artist
		fields = [
			'id',
			'name',
			'picture',
			'description',
			'genres',
			'location',
			'location_text',
			'email',
			'phone',
			'facebook',
			'messenger',
			'twitter',
			'instagram',
			'spotify',
			'soundcloud',
			'bandcamp',
			'youtube',
			'website'
		]

		read_only_fields = [
			'location'
		]

		expandable_fields = {
			'genres': (GenreSerializer, (), { 'many': True })
		}


class VenueSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
	picture = drf_extra_fields.Base64ImageField(required=False)
	location = geo_fields.PointField(required=False)

	class Meta:
		model = Venue
		fields = [
			'id',
			'name',
			'picture',
			'description',
			'genres',
			'location',
			'location_text',
			'email',
			'phone',
			'facebook',
			'messenger',
			'twitter',
			'instagram',
			'spotify',
			'soundcloud',
			'bandcamp',
			'youtube',
			'website'
		]

		read_only_fields = [
			'location'
		]

		expandable_fields = {
			'genres': (GenreSerializer, (), { 'many': True })
		}


class EventSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
	class Meta:
		model = Event
		fields = [
			'id',
			'link',
			'artists',
			'venues'
		]

		expandable_fields = {
			'artists': (ArtistSerializer, (), { 'many': True }),
			'venues': (VenueSerializer, (), { 'many': True })
		}


class ArtistUpdateSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
	picture = drf_extra_fields.Base64ImageField(required=False)

	class Meta:
		model = ArtistUpdate
		fields = [
			'id',
			'artist',
			'name',
			'picture',
			'genres',
			'location_text',
			'email',
			'phone',
			'facebook',
			'messenger',
			'twitter',
			'instagram',
			'spotify',
			'soundcloud',
			'bandcamp',
			'youtube',
			'website'
		]


class VenueUpdateSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
	picture = drf_extra_fields.Base64ImageField(required=False)

	class Meta:
		model = VenueUpdate
		fields = [
			'id',
			'venue',
			'name',
			'picture',
			'genres',
			'location_text',
			'email',
			'phone',
			'facebook',
			'messenger',
			'twitter',
			'instagram',
			'spotify',
			'soundcloud',
			'bandcamp',
			'youtube',
			'website'
		]


class ProfilePrivilegedSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
	class Meta:
		model = Profile
		fields = [
			'id',
			'referrer',
			'premium_months',
			'has_membership',
			'has_lifetime_membership',
			'referral_url',
			'referral_count',
			'eligible_for_lifetime_membership'
		]

		read_only_fields = [
			'referral_url',
			'referral_count'
		]


class UserSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
	class Meta:
		model = User
		fields = [
			'id',
			'email'
		]


class UserPrivilegedSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
	profile = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all())

	class Meta:
		model = User
		fields = [
			'id',
			'email',
			'profile'
		]

		expandable_fields = {
			'profile': ProfilePrivilegedSerializer
		}

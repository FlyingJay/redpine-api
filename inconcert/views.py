from django.shortcuts import render
from django.conf import settings
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext as _
from rest_framework import viewsets, response, generics, decorators, permissions as rest_framework_permissions, exceptions as rest_framework_exceptions
from internal.filters import gps_searchable
from internal.pagination import *
from core.models import Genre, City
from inconcert import tasks, permissions, exceptions
from inconcert.models import *
from inconcert.serializers import *
from inconcert.filters import *
from inconcert.exceptions import *
import square
import google
import json


class ERROR_STRINGS:
	REJECTED_BY_SQUARE = _('Square couldn\'t use the card info provided. Please try again, and check your card details (and postal code!) carefully.')

def mutable(request, value):
	if hasattr(request.data, '_mutable'):
		request.data._mutable = value


#########
# VIEWS #
#########

class SubscriptionViewSet(viewsets.ModelViewSet):
	queryset = Subscription.objects.all()
	serializer_class = SubscriptionSerializer

	def create(self, *args, **kwargs):
		request = self.request
		if request.user.is_anonymous():
			raise PermissionDenied()

		mutable(request, True)
		token = request.data.pop('token')
		request.data['user'] = request.user.id
		mutable(request, False)

		#Don't create a new subscription if one already exists.
		if Subscription.objects.filter(user=request.user,is_cancelled=False).count() > 0:
			return response.Response({}, status=200)

		#Create subscription
		super().create(request, *args, **kwargs)

		subscription = Subscription.objects.filter(user=request.user).order_by('created_date').first()
		customer = None
		try:
			customer = square.models.Customer.objects.create_customer(email=request.user.email, token=token)
			subscription.square_customer = customer
			subscription.save()

			customer.charge(
				amount=999, #9.99
				currency='CAD',#Expand to multi-currency (at least USA) soon. 
				metadata='U'+str(request.user.id)+' inconcert subscription',
				app='inConcert'
			)
			subscription.is_processed = True
			subscription.save()
		except:
			subscription.is_processing_failed = True
			subscription.save()
			raise exceptions.BadRequest(ERROR_STRINGS.REJECTED_BY_SQUARE)

		profile = Profile.objects.get(user=subscription.user)
		profile.premium_months += 1
		profile.save()

		renewal_date = datetime.now() + timedelta(days=30)
		tasks.renew_subscription(subscription.id, schedule=renewal_date)

		return response.Response(SubscriptionSerializer(subscription).data, status=200)


class ArtistViewSet(viewsets.ModelViewSet):
	queryset = Artist.objects.all()
	serializer_class = ArtistSerializer
	filter_class = ArtistFilter
	permission_classes = [
		rest_framework_permissions.IsAuthenticatedOrReadOnly
	]
	pagination_class = StandardResultsSetPagination

	def get_queryset(self):
		queryset = Artist.objects.filter(archived=False).prefetch_related('genres')
		queryset = gps_searchable(self,queryset,'location__dwithin')
		return queryset

	def list(self, request, *args, **kwargs):
		if self.request.user.is_anonymous():
			raise PermissionDenied()
	
		#Membership required.
		if not self.request.user.inconcert_profile.has_membership():
			return response.Response({'detail':'Membership is required.', 'status_code':420})

		genre = None
		try:
			genre = Genre.objects.get(pk=request.GET.get('genres__like',None))
		except:
			pass

		city = None
		try:
			city = City.objects.get(pk=request.GET.get('center',None))
		except:
			pass

		results = self.filter_queryset(self.get_queryset())
		UserQuery.objects.create(
			user=self.request.user,
			model=UserQuery.ARTIST,
			genre=genre,
			city=city,
			name=request.GET.get('name__icontains',None),
			results_count=results.count()
			)

		results = self.paginate_queryset(results)
		serializer = self.get_serializer(results, many=True)
		return response.Response({'results':serializer.data})


class VenueViewSet(viewsets.ModelViewSet):
	queryset = Venue.objects.all()
	serializer_class = VenueSerializer
	filter_class = VenueFilter
	permission_classes = [
		rest_framework_permissions.IsAuthenticatedOrReadOnly
	]
	pagination_class = StandardResultsSetPagination

	def get_queryset(self):
		queryset = Venue.objects.filter(archived=False).prefetch_related('genres')
		queryset = gps_searchable(self,queryset,'location__dwithin')
		return queryset

	def list(self, request, *args, **kwargs):
		if self.request.user.is_anonymous():
			raise PermissionDenied()
	
		#Membership required.
		if not self.request.user.inconcert_profile.has_membership():
			raise MembershipError()

		genre = None
		try:
			genre = Genre.objects.get(pk=request.GET.get('genres__like',None))
		except:
			pass
			
		city = None
		try:
			city = City.objects.get(pk=request.GET.get('center',None))
		except:
			pass

		results = self.filter_queryset(self.get_queryset())
		UserQuery.objects.create(
			user=self.request.user,
			model=UserQuery.VENUE,
			genre=genre,
			city=city,
			name=request.GET.get('name__icontains',None),
			results_count=results.count()
			)

		results = self.paginate_queryset(results)
		serializer = self.get_serializer(results, many=True)
		return response.Response({'results':serializer.data})


class EventViewSet(viewsets.ModelViewSet):
	queryset = Event.objects.all()
	serializer_class = EventSerializer
	filter_class = EventFilter
	permission_classes = [
		rest_framework_permissions.IsAuthenticatedOrReadOnly
	]


class ArtistUpdateViewSet(viewsets.ModelViewSet):
	queryset = ArtistUpdate.objects.all()
	serializer_class = ArtistUpdateSerializer
	permission_classes = [
		rest_framework_permissions.IsAuthenticatedOrReadOnly
	]


class VenueUpdateViewSet(viewsets.ModelViewSet):
	queryset = VenueUpdate.objects.all()
	serializer_class = VenueUpdateSerializer
	permission_classes = [
		rest_framework_permissions.IsAuthenticatedOrReadOnly
	]


class MeView(generics.RetrieveAPIView, generics.CreateAPIView):
	""" special view to load the requesting user's profile """
	def get(self, *args, **kwargs):
		user = self.request.user

		if user.is_anonymous():
			raise PermissionDenied()

		data = UserPrivilegedSerializer(user).data
		data['profile'] = None

		try:
			profile = Profile.objects.get(id=user.inconcert_profile.id)
			data['profile'] = ProfilePrivilegedSerializer(profile).data
		except Exception as e:
			print(e)
			pass

		return response.Response(data, status=200)


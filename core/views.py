from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ValidationError, PermissionDenied
from django.views.generic import TemplateView, View
from django.conf import settings
from django.template.response import TemplateResponse
from django.db.models import Q
from rest_framework import viewsets, response, generics, decorators, permissions as rest_framework_permissions, exceptions as rest_framework_exceptions
from django.utils.translation import ugettext as _
from directmessages.apps import Inbox
from directmessages.models import Message
from core import exceptions, tasks, helpers, filters, permissions, mail
from background_task.models import Task
from internal.filters import gps_searchable
from internal.pagination import *
from .serializers import *
from .models import *
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal 
import background_task
import square
import google
import re
import decimal
import math
import json
import urllib

google_client = google.GoogleClient(settings.GOOGLE_API_KEY)

#Pass an object into pprint to see attributes (debugging)
#from pprint import pprint


def mutable(request, value):
    if hasattr(request.data, '_mutable'):
        request.data._mutable = value


class ERROR_STRINGS:
    UPGRADE_ACCOUNT = _('A higher level account is required to perform this action.')
    CAMPAIGN_CONFIRM_PERMISSION_DENIED = _('You don\'t have permission to confirm this campaign.')
    TICKET_CODE_NOT_SUPPLIED = _('This parameter is required.')
    TICKET_CODE_INVALID = _('Ticket code invalid.')
    ADDRESS_NOT_FOUND = _('This address appears to be invalid.')
    INSUFFICIENT_FUNDS = _('The account does not have the required funds for this payment.')
    REJECTED_BY_SQUARE = _('Square couldn\'t use the card info provided. Please try again, and check your card details (and postal code!) carefully.')


###############
# MODEL VIEWS #
###############

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LargeResultsSetPagination 
    filter_class = filters.UserFilter


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    filter_fields = {
        'id': ('in', 'exact',),
    }

    def get_queryset(self):
        if self.request.user.is_anonymous():
            raise PermissionDenied()
        else: 
            return Notification.objects.filter(profile=self.request.user.profile).order_by('-created_date')

    @decorators.detail_route(methods=['get'])
    def unread_count(self, request, pk=None):
        unread_count = 0
        if self.request.user.profile:
            unread_count = self.request.user.profile.notifications.filter(is_read=False).count()
        
        return response.Response({'unread_count':unread_count}, status=200)

    @decorators.detail_route(methods=['post'])
    def read(self, request, pk=None):
        notification = Notification.objects.get(id=pk)

        notification.is_read = True
        notification.save()
        return response.Response({}, status=204)

    @decorators.detail_route(methods=['post'])
    def read_all(self, request, pk=None):
        notifications = self.request.user.profile.notifications.all().update(is_read=True)
        return response.Response({}, status=204)

    @decorators.detail_route(methods=['post'])
    def delete_all(self, request, pk=None):
        notifications = self.request.user.profile.notifications.all().delete()
        return response.Response({}, status=204)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = LargeResultsSetPagination 
    filter_class = filters.GenreFilter
    

class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    pagination_class = LargeResultsSetPagination 
    filter_class = filters.CityFilter

    def get_queryset(self):
        queryset = City.objects.all()
        queryset = gps_searchable(self,queryset,'location__dwithin')
        return queryset

    @decorators.detail_route(methods=['get'])
    def with_venues(self, request, pk=None):
        venue_cities = Venue.objects.all().values('city')
        cities_list = City.objects.filter(id__in=venue_cities) 

        serializer = self.get_serializer(cities_list, many=True)
        return response.Response({'results':serializer.data}, status=200)

    @decorators.detail_route(methods=['get'])
    def with_bands(self, request, pk=None):
        band_cities = Band.objects.all().values('hometown')
        cities_list = City.objects.filter(id__in=band_cities)

        serializer = self.get_serializer(cities_list, many=True)
        return response.Response({'results':serializer.data}, status=200)


class ProvinceViewSet(viewsets.ModelViewSet):
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer
    pagination_class = LargeResultsSetPagination 
    filter_class = filters.ProvinceFilter

    @decorators.detail_route(methods=['get'])
    def with_venues(self, request, pk=None):
        venue_cities = Venue.objects.all().values('city')
        venue_provinces = City.objects.filter(id__in=venue_cities).values('province')
        provinces_list = Province.objects.filter(id__in=venue_provinces)

        serializer = self.get_serializer(provinces_list, many=True)
        return response.Response({'results':serializer.data}, status=200)

    @decorators.detail_route(methods=['get'])
    def with_bands(self, request, pk=None):
        band_cities = Band.objects.all().values('hometown')
        band_provinces = City.objects.filter(id__in=band_cities).values('province')
        provinces_list = Province.objects.filter(id__in=band_provinces)

        serializer = self.get_serializer(provinces_list, many=True)
        return response.Response({'results':serializer.data}, status=200)


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    pagination_class = LargeResultsSetPagination 
    filter_class = filters.CountryFilter

    @decorators.detail_route(methods=['get'])
    def with_venues(self, request, pk=None):
        venue_cities = Venue.objects.all().values('city')
        venue_provinces = City.objects.filter(id__in=venue_cities).values('province')
        venue_countries = Province.objects.filter(id__in=venue_provinces).values('country')
        countries_list = Country.objects.filter(id__in=venue_countries)

        serializer = self.get_serializer(countries_list, many=True)
        return response.Response({'results':serializer.data}, status=200)

    @decorators.detail_route(methods=['get'])
    def with_bands(self, request, pk=None):
        band_cities = Band.objects.all().values('hometown')
        band_provinces = City.objects.filter(id__in=band_cities).values('province')
        band_countries = Province.objects.filter(id__in=band_provinces).values('country')
        countries_list = Country.objects.filter(id__in=band_countries)

        serializer = self.get_serializer(countries_list, many=True)
        return response.Response({'results':serializer.data}, status=200)


class BandViewSet(viewsets.ModelViewSet):
    queryset = Band.objects.all()
    filter_class = filters.BandFilter
    pagination_class = StandardResultsSetPagination
    permission_classes = [
        rest_framework_permissions.IsAuthenticatedOrReadOnly,
        permissions.BandPermission,
    ]

    def get_serializer_class(self):
        if self.action == 'update':
            return BandSerializer
        elif self.action == 'create':
            return CreateBandSerializer
        else:
            return GetBandSerializer

    def get_queryset(self):
        queryset = Band.objects.filter(archived=False).prefetch_related('genres').select_related('hometown__province__country')
        queryset = gps_searchable(self,queryset,'hometown__location__dwithin')
        return queryset

    def create(self, request, *args, **kwargs):
        user = request.user.id
        
        is_redpine = False
        if 'is_redpine' in request.data:
            is_redpine = request.data.get('is_redpine')        

        mutable(request, True)
        if is_redpine:
            request.data['owner'] = user
        request.data['join_token'] = secrets.token_hex(16)
        mutable(request, False)

        if is_redpine:
            acts_count = Band.objects.filter(owner=user).count()
            is_member_organizer = helpers.has_subscription(user,AccountSubscription.ORGANIZER,AccountSubscription.MEMBER)
            is_member_artist = helpers.has_subscription(user,AccountSubscription.ARTIST,AccountSubscription.MEMBER)
            is_ultimate_artist = helpers.has_subscription(user,AccountSubscription.ARTIST,AccountSubscription.ULTIMATE)
            #Free = 1, Member Artist = 3, Ultimate Artist or Organizer = Unlimited
            if acts_count > 0 and not is_member_artist and not is_member_organizer:
                raise rest_framework_exceptions.ValidationError({'detail': ERROR_STRINGS.UPGRADE_ACCOUNT})
            elif acts_count > 3 and not is_ultimate_artist and not is_member_organizer:
                raise rest_framework_exceptions.ValidationError({'detail': ERROR_STRINGS.UPGRADE_ACCOUNT})

        return super().create(request, *args, **kwargs)


    @decorators.detail_route(methods=['post'])
    def payout(self, request, pk=None):
        act = Band.objects.get(id=pk)

        PaymentRequest.objects.create(
            user=act.owner,
            amount=act.account_balance
            )        
        act.account_balance = 0.00
        act.save()

        return response.Response({}, status=204)


    @decorators.detail_route(methods=['get'])
    def share(self, request, pk=None):
        ua = request.META['HTTP_USER_AGENT']
        sharebot_matcher = re.compile('facebookexternalhit/[0-9]|Twitterbot|Pinterest|Google.*snippet')

        # if it's a sharebot, lets send them the meta shit they need
        if sharebot_matcher.search(ua):
            band = Band.objects.get(id=pk)
            data = {
                'full_path': request.get_full_path(),
                'band': band,
                'settings': settings
            }
            return TemplateResponse(request, 'act/share.html', data)

        # otherwise, redirect to the band page
        else:
            return redirect(settings.REDPINE_WEBAPP_URLS['ACT'](pk))


class TourCampaignViewSet(viewsets.ModelViewSet):
    queryset = TourCampaign.objects.all()
    serializer_class = TourCampaignSerializer
    filter_class = filters.TourCampaignFilter
    permission_classes = [
        rest_framework_permissions.IsAuthenticatedOrReadOnly,
    ]


class TourViewSet(viewsets.ModelViewSet):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    filter_class = filters.TourFilter

    def create(self, request, *args, **kwargs):
        user = self.request.user
        
        if user.is_anonymous():
            raise PermissionDenied()

        is_member_artist = helpers.has_subscription(user,AccountSubscription.ARTIST,AccountSubscription.MEMBER)
        is_member_organizer = helpers.has_subscription(user,AccountSubscription.ORGANIZER,AccountSubscription.MEMBER)

        if not is_member_artist and not is_member_organizer:
            raise rest_framework_exceptions.ValidationError({'detail': ERROR_STRINGS.UPGRADE_ACCOUNT})

        return super().create(request, *args, **kwargs)


class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.filter(archived=False,is_redpine_approved=True).prefetch_related('bands','organizations').select_related('timeslot__venue__city__province__country')
    filter_class = filters.CampaignFilter
    pagination_class = StandardResultsSetPagination 
    permission_classes = [
        rest_framework_permissions.IsAuthenticatedOrReadOnly,
        permissions.CampaignPermission
    ]

    def get_serializer_class(self):
        if self.action == 'update':
            return CampaignUpdateSerializer  
        else: 
            return CampaignSerializer

    def get_queryset(self):
        queryset = Campaign.objects.filter(
            Q(is_redpine_approved=True) | Q(created_by=self.request.user.id),
            archived=False
            ).prefetch_related('bands','organizations').select_related('timeslot__venue__city__province__country')
        queryset = gps_searchable(self,queryset,'timeslot__venue__city__location__dwithin')
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = CampaignCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        def add_organizations(campaign,organizations):
            if organizations is not None:
                for organization in organizations:
                    organization = Organization.objects.get(pk=organization)
                    campaign_organization = CampaignOrganization.objects.create(
                        campaign=campaign,
                        organization=organization,
                        is_accepted=True,
                        can_edit=True
                        )

        mutable(request, True)
        venue = Venue.objects.get(pk=request.data.pop('venue'))
        
        first_timeslot = {
            'venue': venue,
            'start_time': request.data.pop('start_time'),
            'end_time': request.data.pop('end_time')
        }

        frequency = int(request.data.pop('frequency', 0))
        frequency_count = int(request.data.pop('frequency_count', 1))

        request.data['created_by'] = request.user

        organizations = None
        if request.data.get('organizations', None) is not None:
            organizations = request.data.pop('organizations')
        mutable(request, False)

        if frequency_count == 0:
            raise rest_framework_exceptions.ValidationError({'detail': 'Number of created events cannot be 0.'})
        try: 
            if frequency == 0:
                mutable(request, True)
                request.data['timeslot'] = Timeslot.objects.create(**first_timeslot)
                mutable(request, False)
                campaign = Campaign.objects.create(**request.data)
                add_organizations(campaign,organizations)

            else:
                start_time = datetime.strptime(first_timeslot['start_time'].split('.')[0],'%Y-%m-%dT%H:%M:%S')
                end_time = datetime.strptime(first_timeslot['end_time'].split('.')[0],'%Y-%m-%dT%H:%M:%S')
                
                for i in range(frequency_count):
                    timeslot = first_timeslot

                    if frequency == 1:
                        timeslot['start_time'] = start_time + timedelta(days=i)
                        timeslot['end_time'] = end_time + timedelta(days=i)
                    elif frequency == 2:
                        timeslot['start_time'] = start_time + timedelta(weeks=i)
                        timeslot['end_time'] = end_time + timedelta(weeks=i)
                    elif frequency == 3:#BI-WEEKLY
                        timeslot['start_time'] = start_time + relativedelta(weeks=i*2)
                        timeslot['end_time'] = end_time + relativedelta(weeks=i*2)
                    elif frequency == 4:
                        timeslot['start_time'] = start_time + relativedelta(months=i)
                        timeslot['end_time'] = end_time + relativedelta(months=i)

                    mutable(request, True)
                    request.data['timeslot'] = Timeslot.objects.create(**timeslot)
                    request.data['funding_end'] = timeslot['end_time']
                    mutable(request, False)

                    campaign = Campaign.objects.create(**request.data)
                    add_organizations(campaign,organizations)

            price = decimal.Decimal(request.data['min_ticket_price'])
            PurchaseItem.objects.create(
                name='Standard Ticket' if price > 0 else 'RSVP',
                description="It\'ll get you in the door.",
                price=price,
                quantity=venue.capacity,
                campaign=campaign,
                is_ticket=True
            )

            return response.Response({}, status=200)

        except ValidationError as e:
            print(e)
            raise rest_framework_exceptions.ValidationError({'detail': e.message})

    def update(self, request, pk=None):
        if 'is_venue_approved' in request.data:
            mutable(request, True)
            request.data.pop('is_venue_approved')
            mutable(request, False)

        campaign = Campaign.objects.prefetch_related('bands__owner__profile').get(pk=pk)

        #Close any open opportunities
        if 'is_open' in request.data:
            is_open = request.data.get('is_open')
            if is_open is False:
                Opening.objects.filter(campaign=campaign).update(is_open=False)

        #Send notifications to acts
        for band in campaign.bands.all():
            if band.owner:
                Notification.objects.create(
                    profile=band.owner.profile,
                    subject_type=1,#CAMPAIGN
                    text='Your show details have changed!',
                    campaign=campaign
                )

        #Send notifications to venue managers
        if campaign.timeslot.venue:
            managers = campaign.timeslot.venue.managers.all()
            for manager in managers:
                Notification.objects.create(
                    profile=manager.profile,
                    subject_type=1,#CAMPAIGN
                    text='The details for a show at your venue have changed!',
                    campaign=campaign
                ) 

        try:
            return super().update(request, pk)

        except ValidationError as e:
            raise rest_framework_exceptions.ValidationError({'detail': e.message})

    @decorators.list_route(methods=['post'])
    def check_door_code(self, request):
        """ validate a door code """
        campaign_qs = Campaign.objects.filter(door_code=request.data.get('door_code'))
        if campaign_qs.exists():
            return response.Response({'campaign': campaign_qs.first().id}, status=200)
        return response.Response({}, status=400)

    @decorators.detail_route(methods=['get'])
    def door_code(self, request, pk=None):
        """ get a door code """
        campaign = Campaign.objects.get(pk=pk)
        door_code = campaign.door_code
        is_authorized = False
        user = request.user

        # if the user is a venue manager, they can create transaction
        if user.id in [m.id for m in campaign.timeslot.venue.managers.all()]:
            is_authorized = True
        # if the user owns a band as part of the campaign, they can create transaction
        if user.id in [band.owner.id for band in campaign.bands.all()]:
            is_authorized = True
        # if the user created the campaign, they can create transaction
        if Campaign.objects.filter(id=campaign.id,created_by=user.id).count() > 0:
            is_authorized = True

        if is_authorized:
            return response.Response({'door_code': door_code}, status=200)
        return response.Response({}, status=403)

    @decorators.detail_route(methods=['post'])
    def confirm(self, request, pk=None):
        campaign = Campaign.objects.get(id=pk)

        managers = campaign.timeslot.venue.managers.all()
        manager_ids = [m.id for m in managers]
        is_venue_manager = request.user.id in manager_ids

        if not is_venue_manager:
            raise rest_framework_exceptions.PermissionDenied(ERROR_STRINGS.CAMPAIGN_CONFIRM_PERMISSION_DENIED)
        
        campaign.is_venue_approved = True
        campaign.save()

        #Update tutorial event for the approving user
        Profile.objects.filter(id=request.user.id).update(welcome_approve_booking_request=True)

        #Send notifications to acts
        for band in campaign.bands.all():
            if band.owner:
                Notification.objects.create(
                    profile=band.owner.profile,
                    subject_type=1,#CAMPAIGN
                    text='Your show request has been accepted by the venue!',
                    campaign=campaign
                )
                if band.owner.profile.receives_emails:
                    mail.show_request_approved(email=band.owner.email, data={'user':band.owner,'venue':campaign.timeslot.venue,'campaign':campaign}) 

        band_subscribers = BandSubscription.objects.filter(band__in=campaign.bands.all()).only('user')
        organization_subscribers = OrganizationSubscription.objects.filter(organization__in=campaign.organizations.all()).only('user')
        venue_subscribers = VenueSubscription.objects.filter(venue=campaign.timeslot.venue).only('user')

        subscribers = []
        for band_subscriber in BandSubscription.objects.filter(band__in=campaign.bands.all()).only('user'):
            subscribers.append(band_subscriber.user.id)

        for organization_subscriber in OrganizationSubscription.objects.filter(organization__in=campaign.organizations.all()).only('user'):
            subscribers.append(organization_subscriber.user.id)

        for venue_subscriber in VenueSubscription.objects.filter(venue=campaign.timeslot.venue).only('user'):
            subscribers.append(venue_subscriber.user.id)

        subscriber_profiles = Profile.objects.filter(user__id__in=subscribers).distinct().prefetch_related('user')

        for profile in subscriber_profiles:
            Notification.objects.create(
                profile=profile,
                subject_type=Notification.TICKETS,
                text='One of your subscriptions added a show!',
                campaign=campaign
            )
            mail.new_active_show_by_subscription(email=profile.user.email, data={'campaign':campaign}) 

        #Close existing opening if it exists
        Opening.objects.filter(timeslot=campaign.timeslot).update(campaign=campaign,is_open=False)

        return response.Response({}, status=204)

    @decorators.detail_route(methods=['post'])
    def deny(self, request, pk=None):
        campaign = Campaign.objects.get(id=pk)

        managers = campaign.timeslot.venue.managers.all()
        manager_ids = [m.id for m in managers]
        is_venue_manager = request.user.id in manager_ids
        
        if not is_venue_manager:
            raise rest_framework_exceptions.PermissionDenied(ERROR_STRINGS.CAMPAIGN_CONFIRM_PERMISSION_DENIED)

        campaign.is_venue_approved = False
        campaign.save()

        #Send notifications to acts
        for band in campaign.bands.all():
            if band.owner:
                Notification.objects.create(
                    profile=band.owner.profile,
                    subject_type=1,#CAMPAIGN
                    text='Your show request was rejected by the venue.',
                    campaign=campaign
                )
                mail.show_request_rejected(email=band.owner.email, data={'user':band.owner,'campaign':campaign}) 

        return response.Response({}, status=204)

    @decorators.detail_route(methods=['post'])
    def book(self, request, pk=None):
        campaign = Campaign.objects.get(id=pk)
        
        Timeslot.objects.filter(id=campaign.timeslot.id).update(asking_price=decimal.Decimal(0.00), min_headcount=0)
        Campaign.objects.filter(id=pk).update(is_successful=True)

        return response.Response({}, status=204)

    @decorators.detail_route(methods=['get'])
    def share(self, request, pk=None):
        ua = request.META['HTTP_USER_AGENT']
        sharebot_matcher = re.compile('facebookexternalhit/[0-9]|Twitterbot|Pinterest|Google.*snippet')

        # if it's a sharebot, lets send them the meta shit they need
        if sharebot_matcher.search(ua):
            campaign = Campaign.objects.get(id=pk)
            data = {
                'full_path': request.get_full_path(),
                'image': campaign.image if campaign.image else settings.REDPINE_LOGO_URL,
                'campaign': campaign,
                'settings': settings
            }
            return TemplateResponse(request, 'campaign/share.html', data)

        # otherwise, redirect to the campaign page
        else:
            return redirect(settings.REDPINE_WEBAPP_URLS['SHOW'](pk))


class CampaignDocumentViewSet(viewsets.ModelViewSet):
    queryset = CampaignDocument.objects.all()
    serializer_class = CampaignDocumentSerializer
    permission_classes = [
        permissions.CampaignDocumentPermission
    ]

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class CampaignBandViewSet(viewsets.ModelViewSet):
    queryset = CampaignBand.objects.all().select_related('band')
    serializer_class = CampaignBandSerializer
    filter_class = filters.CampaignBandFilter
    permission_classes = [
        rest_framework_permissions.IsAuthenticatedOrReadOnly,
        permissions.CampaignBandPermission
    ]

    def create(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_anonymous():
            raise PermissionDenied()

        joined_another_show = CampaignBand.objects.filter(
            Q(campaign__is_redpine_approved=True) | Q(campaign__is_redpine_approved=None),
            band__owner=user,
            is_accepted=True,
            is_application=None,
            campaign__timeslot__start_time__gt=datetime.now()
            ).exclude(campaign__created_by=user).count() > 0

        is_member_organizer = helpers.has_subscription(user,AccountSubscription.ORGANIZER,AccountSubscription.MEMBER)
        is_member_artist = helpers.has_subscription(user,AccountSubscription.ARTIST,AccountSubscription.MEMBER)

        if joined_another_show and not is_member_artist and not is_member_organizer:
            raise rest_framework_exceptions.ValidationError({'detail': ERROR_STRINGS.UPGRADE_ACCOUNT})

        band = request.data['band']
        campaign = request.data['campaign']

        if isinstance(band, int) or isinstance(band, str):
            band = Band.objects.get(pk=int(band))
        
        if isinstance(campaign, int) or isinstance(campaign, str):
            campaign = Campaign.objects.get(pk=int(campaign))

        #Send out invite messages if not added by a member of the act. 
        is_invitation = band.owner and band.owner.id != user.id
        if is_invitation and band.owner.profile.receives_emails:
            mail.act_show_invite(email=band.owner.email, data={'campaign':campaign})
        
            Notification.objects.create(
                profile=band.owner.profile,
                subject_type=1,#CAMPAIGN
                text='{} has been invited to play {}!'.format(band.name,campaign.title),
                campaign=campaign
            )

        is_organizer = (Campaign.objects.filter(id=campaign.id,created_by=user.id).count() > 0)
        is_application = (band.owner and band.owner.id == user.id)
        if is_application and not is_organizer:
            mail.open_lineup_request_submitted(email=band.owner.email, data={'campaign':campaign})
            mail.open_lineup_request_recieved(email=campaign.created_by.email, data={'band':band,'campaign':campaign})

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class PurchaseItemViewSet(viewsets.ModelViewSet):
    queryset = PurchaseItem.objects.all()
    serializer_class = PurchaseItemSerializer
    permission_classes = [
        rest_framework_permissions.IsAuthenticatedOrReadOnly,
        permissions.PurchaseItemPermission
    ]

    def update(self, request, pk=None, *args, **kwargs):
        item = PurchaseItem.objects.get(pk=pk)

        if request.data.get('price',None) and PledgePurchase.objects.filter(item=item).count() > 0:
            quantity = item.quantity

            item.is_hidden = True
            item.quantity = 0
            item.save()

            item.pk = None
            item.is_hidden = False
            item.quantity = quantity
            item.save()
            return super().update(request, pk=item.id, *args, **kwargs)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        item = self.get_object()

        if PledgePurchase.objects.filter(item=item).count() > 0:
            item.is_hidden = True
            item.quantity = 0
            item.save()
            return HttpResponse({}, status=200)
        else:
            return super().destroy(self, request, *args, **kwargs)


class CampaignFeedViewSet(viewsets.ModelViewSet):
    queryset = CampaignFeed.objects.all()
    serializer_class = CampaignFeedSerializer
    filter_class = filters.CampaignFeedFilter
    
    def create(self, request, *args, **kwargs):
        min_email_delay = 180#seconds

        is_system = request.data['is_system']
        campaign_id = request.data['campaign']

        if not is_system:
            campaign = Campaign.objects.prefetch_related('bands__owner__profile').get(pk=campaign_id)
            last_email = CampaignFeed.objects.filter(campaign=campaign_id,is_system=False,sent_notification=True).values('created_date').order_by('-created_date').first()

            send_emails = (last_email is None or (datetime.now() - last_email['created_date']).seconds >= min_email_delay)

            #Send notifications to managers
            if campaign.timeslot.venue:
                managers = campaign.timeslot.venue.managers.prefetch_related('profile')
                for manager in managers:
                    if request.user != manager:
                        Notification.objects.create(
                            profile=manager.profile,
                            subject_type=1,#CAMPAIGN
                            text='You have new chat messages for {}'.format(campaign.title),
                            campaign=campaign
                        )
                        if send_emails and manager.profile.receives_emails:
                            mail.new_feed_message(email=manager.email, data={'user':request.user,'campaign':campaign})

            #Send notifications to acts
            for band in campaign.bands.all():
                if band.owner and request.user != band.owner:
                    Notification.objects.create(
                        profile=band.owner.profile,
                        subject_type=1,#CAMPAIGN
                        text='You have new chat messages for {}'.format(campaign.title),
                        campaign=campaign
                    )
                    if send_emails and band.owner.profile.receives_emails:
                        mail.new_feed_message(email=band.owner.email, data={'user':request.user,'campaign':campaign})

            if send_emails:
                mutable(request, True)
                request.data['sent_notification'] = True
                mutable(request, False)

        return super().create(request, *args, **kwargs)


class OrganizationBandViewSet(viewsets.ModelViewSet):
    queryset = OrganizationBand.objects.all().select_related('band')
    serializer_class = OrganizationBandSerializer 
    filter_class = filters.OrganizationBandFilter
    permission_classes = [
        rest_framework_permissions.IsAuthenticatedOrReadOnly,
        permissions.OrganizationBandPermission
    ]

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @decorators.detail_route(methods=['post'])
    def confirm(self, request, pk=None):
        organization_band = OrganizationBand.objects.get(id=pk)

        user_in_band = Band.objects.filter(owner=request.user,id=organization_band.band.id).count() > 0
        user_in_organization = Organization.objects.filter(managers=request.user, id=organization_band.organization.id).count() > 0

        if user_in_band:
            organization_band.is_accepted = True
        if user_in_organization:
            organization_band.is_application = True
        organization_band.save()

        return response.Response({}, status=204)

    @decorators.detail_route(methods=['post'])
    def deny(self, request, pk=None):
        organization_band = OrganizationBand.objects.get(id=pk)

        user_in_band = Band.objects.filter(owner=request.user,id=organization_band.band.id).count() > 0
        user_in_organization = Organization.objects.filter(managers=request.user, id=organization_band.organization.id).count() > 0
 
        if user_in_band:
            organization_band.is_accepted = False
        if user_in_organization:
            organization_band.is_application = False
        organization_band.save()
        
        return response.Response({}, status=204)


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.filter(archived=False)
    filter_class = filters.OrganizationFilter
    permission_classes = [
        rest_framework_permissions.IsAuthenticatedOrReadOnly,
        permissions.OrganizationPermission
    ]

    def get_serializer_class(self):
        if self.action == 'update':
            return OrganizationUpdateSerializer
        elif self.action == 'create':
            return OrganizationCreateSerializer
        else:
            return OrganizationSerializer

    def create(self, request, *args, **kwargs):
        try:
            address = request.data.get('address', '')
            geocoded = google_client.geocode(address)
            mutable(request, True)
            request.data['location'] = {
                'latitude': geocoded.location.x, 
                'longitude': geocoded.location.y
            }
            mutable(request, False)
        except google.GoogleNoResultsException:
            raise rest_framework_exceptions.ValidationError({'address': ERROR_STRINGS.ADDRESS_NOT_FOUND})

        res = super().create(request, *args, **kwargs)
        if res.status_code == 201:
            organization = Organization.objects.get(pk=res.data.get('id'))
            OrganizationManager.objects.create(manager=request.user, organization=organization)
        return res

    @decorators.detail_route(methods=['post'])
    def payout(self, request, pk=None):
        organization = Organization.objects.get(id=pk)

        PaymentRequest.objects.create(
            user=request.user,
            amount=organization.account_balance
            )        
        organization.account_balance = 0.00
        organization.save()

        return response.Response({}, status=204)


class VenueViewSet(viewsets.ModelViewSet):
    queryset = Venue.objects.filter(archived=False).prefetch_related('genres').select_related('city__province__country')
    filter_class = filters.VenueFilter
    pagination_class = StandardResultsSetPagination
    permission_classes = [
        rest_framework_permissions.IsAuthenticatedOrReadOnly,
        permissions.VenuePermission
    ]

    def get_serializer_class(self):
        if self.action == 'update':
            return VenueUpdateSerializer
        elif self.action == 'create':
            return VenueCreateSerializer
        else:
            return VenueSerializer

    def get_queryset(self):
        queryset = Venue.objects.filter(archived=False).prefetch_related('genres').select_related('city__province__country')
        queryset = gps_searchable(self,queryset,'city__location__dwithin')
        return queryset

    def create(self, request, *args, **kwargs):
        mutable(request, True)
        try:
            address = request.data.get('address', '')
            geocoded = google_client.geocode(address)
            request.data['location'] = {
                'latitude': geocoded.location.x, 
                'longitude': geocoded.location.y
            }
        except google.GoogleNoResultsException:
            raise rest_framework_exceptions.ValidationError({'address': ERROR_STRINGS.ADDRESS_NOT_FOUND})

        mutable(request, False)
        res = super().create(request, *args, **kwargs)
        venue = Venue.objects.get(pk=res.data.get('id'))
        VenueManager.objects.create(manager=request.user, venue=venue)
        VenueStats.objects.create(venue=venue)
        return res


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_class = filters.EventFilter
    permission_classes = [
        rest_framework_permissions.IsAuthenticatedOrReadOnly,
        permissions.EventPermission,
    ]

    def create(self, request, *args, **kwargs):
        mutable(request, True)
        frequency = int(request.data.pop('frequency'))
        frequency_count = int(request.data.pop('frequency_count'))
        mutable(request, False)

        if frequency_count == 0:
            raise rest_framework_exceptions.ValidationError({'detail': 'Number of created events cannot be 0.'})

        try: 
            if frequency == 0:
                res = super().create(request, *args, **kwargs)
            else:
                start_time = datetime.strptime(request.data['start_time'].split('.')[0],'%Y-%m-%dT%H:%M:%S')
                end_time = datetime.strptime(request.data['end_time'].split('.')[0],'%Y-%m-%dT%H:%M:%S')
                
                for i in range(frequency_count):
                    event = request
                    if frequency == 1:
                        event.data['start_time'] = start_time + timedelta(days=i)
                        event.data['end_time'] = end_time + timedelta(days=i)
                    elif frequency == 2:
                        event.data['start_time'] = start_time + timedelta(weeks=i)
                        event.data['end_time'] = end_time + timedelta(weeks=i)
                    elif frequency == 3:#BI-WEEKLY
                        event.data['start_time'] = start_time + relativedelta(weeks=i*2)
                        event.data['end_time'] = end_time + relativedelta(weeks=i*2)
                    elif frequency == 4:
                        event.data['start_time'] = start_time + relativedelta(months=i)
                        event.data['end_time'] = end_time + relativedelta(months=i)

                    res = super().create(event, *args, **kwargs)
            
            return res

        except ValidationError as e:
            raise rest_framework_exceptions.ValidationError({'detail': e.message})


class OpeningViewSet(viewsets.ModelViewSet):
    queryset = Opening.objects.all()
    serializer_class = OpeningSerializer
    filter_class = filters.OpeningFilter
    pagination_class = StandardResultsSetPagination
    permission_classes = [
        rest_framework_permissions.IsAuthenticatedOrReadOnly,
    ]

    def get_queryset(self):
        queryset = Opening.objects.all()
        queryset = gps_searchable(self,queryset,'timeslot__venue__city__location__dwithin')
        return queryset

    def create(self, request, *args, **kwargs):
        try:
            campaign = request.data.get('campaign')
            if campaign:
                Campaign.objects.filter(id=campaign).update(is_open=True)

            return super().create(request, *args, **kwargs)

        except ValidationError as e:
            raise rest_framework_exceptions.ValidationError({'detail': e.message})


class TimeslotViewSet(viewsets.ModelViewSet):
    queryset = Timeslot.objects.all()
    serializer_class = TimeslotSerializer
    filter_class = filters.TimeslotFilter
    permission_classes = [
        rest_framework_permissions.IsAuthenticatedOrReadOnly,
        permissions.TimeslotPermission,
    ]

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)

        except ValidationError as e:
            raise rest_framework_exceptions.ValidationError({'detail': e.message})

    def destroy(self, *args, **kwargs):
        try:
            return super().destroy(*args, **kwargs)

        except ValidationError as e:
            raise rest_framework_exceptions.ValidationError({'detail': e.message})

    def update(self, request, pk=None, *args, **kwargs):
        try:
            start_time = request.data.get('start_time')
            end_time = request.data.get('end_time')

            if start_time:
                start_time = start_time.split('.')[0]
                if 'T' in str(start_time):
                    start_time = datetime.strptime(start_time,'%Y-%m-%dT%H:%M:%S')
                else:
                    start_time = datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S')

                if end_time:
                    end_time = end_time.split('.')[0]
                    if 'T' in str(end_time):
                        end_time = datetime.strptime(end_time,'%Y-%m-%dT%H:%M:%S')
                    else:
                        end_time = datetime.strptime(end_time,'%Y-%m-%d %H:%M:%S')

                timeslot = Timeslot.objects.filter(id=pk).first()
                campaigns = Campaign.objects.filter(timeslot_id=pk)

                for campaign in campaigns:
                    Campaign.objects.filter(id=campaign.id).update(funding_end=end_time)

                    #Update the processing date for performer payout tasks
                    Task.objects.filter(task_name='core.tasks.pay_performers', queue='payouts_{}'.format(campaign.id)).update(run_at=end_time)

            return super().update(request, *args, **kwargs)

        except ValidationError as e:
            raise rest_framework_exceptions.ValidationError({'detail': e.message})


class WebTransactionViewSet(viewsets.ModelViewSet):
    queryset = Pledge.objects.filter(is_processing_failed=False).order_by('-campaign__timeslot__start_time')
    filter_class = filters.WebTransactionFilter
    permission_classes = [
        permissions.WebTransactionPermission,
        rest_framework_permissions.IsAuthenticatedOrReadOnly
    ]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateWebTransactionSerializer
        else:
            return WebTransactionSerializer

    def destroy(self, request, pk=None):
        transaction = self.get_object()

        if transaction.is_processed:
            raise exceptions.PermissionDenied()

        # Remove PledgePurchase objects and update quantities
        transactionItems = PledgePurchase.objects.filter(transaction=transaction)
        for transactionItem in transactionItems:
            mainItem = PurchaseItem.objects.get(pk=transactionItem.item.id)
            mainItem.quantity = mainItem.quantity + transactionItem.quantity
            mainItem.save()
            transactionItem.delete()

        transaction.is_cancelled = True
        transaction.save()

        mail.transaction_cancelled(email=transaction.user.email, data={'user':request.user, 'transaction':transaction})

        return HttpResponse({}, status=200)

    def create(self, request, *args, **kwargs):
        mutable(request, True)
        items = request.data.pop('items')
        quantities = request.data.pop('quantities')
        bands = request.data.pop('bands')
        mutable(request, False)

        campaign = Campaign.objects.get(pk=request.data.get('campaign'))
        
        total = decimal.Decimal(request.data.get('total'))
        promoter = User.objects.filter(pk=request.data.get('promoter',None)).first()
        customer = None

        #No square interaction required for RSVPs and/or free events.
        requires_payment = (request.data.get('token') or total > 0.00)
        if requires_payment:
            try:
                customer = square.models.Customer.objects.create_customer(email=request.user.email, token=request.data.get('token'))
            except:
                mail.transaction_failed(email=request.user.email, data={
                    'user': request.user,
                    'campaign': campaign
                })
                raise exceptions.BadRequest(ERROR_STRINGS.REJECTED_BY_SQUARE)

        purchase = {
            'user': request.user,
            'square_customer': customer,
            'campaign': campaign,
            'promoter': promoter,
            'redpine_fee': decimal.Decimal(request.data.get('total')) * (campaign.service_fee if campaign else Campaign.DEFAULT_SERVICE_FEE) / decimal.Decimal('100'),
            'total': total,
            'count': int(request.data.get('count')),
            'is_processed': not requires_payment,
            'is_real': not campaign.is_only_tickets
        }

        transaction = Pledge.objects.create(**purchase)
        transaction.bands = bands
        transaction.save()
    
        for i, quantity in enumerate(quantities):
            if int(quantity) > 0 :
                #Create tickets
                item = PurchaseItem.objects.get(pk=items[i])
                PledgePurchase.objects.create(transaction=transaction,item=item,quantity=quantity)
                for i in range(int(quantity)):
                    Ticket.objects.create(pledge=transaction,details=item)
                #Update available quantities
                item.quantity = item.quantity - int(quantity)
                item.save()

        try:
            transaction = tasks.process_transaction.now(transaction.id)
            serializer = WebTransactionSerializer(transaction)
            return response.Response(serializer.data, status=200)
        except Exception as e:
            print(e)
            raise e


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    pagination_class = StandardResultsSetPagination
    filter_class = filters.TicketFilter
    permission_classes = [ 
        rest_framework_permissions.IsAuthenticated,
        permissions.TicketPermission
    ]

    def get_queryset(self):
        return Ticket.objects.filter(pledge__user=self.request.user).prefetch_related('pledge__campaign__timeslot__venue__city__province__country').order_by('-pledge__campaign__timeslot__start_time','id')

    @decorators.list_route(methods=['post'], permission_classes=[rest_framework_permissions.AllowAny])
    def validate(self, request):
        code = request.data.get('code')

        if code is None:
            raise rest_framework_exceptions.ValidationError({'code': ERROR_STRINGS.TICKET_CODE_NOT_SUPPLIED})

        try:
            ticket = Ticket.objects.get(code=code)
        except:
            raise rest_framework_exceptions.NotFound(detail=ERROR_STRINGS.TICKET_CODE_INVALID)

        Scan.objects.create(ticket=ticket)
        serializer = self.get_serializer(ticket)
        return response.Response(serializer.data, status=200)


class GuestListViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    pagination_class = LargeResultsSetPagination
    filter_class = filters.TicketFilter
    permission_classes = [ 
        rest_framework_permissions.IsAuthenticated,
        permissions.GuestListPermission
    ]

    def get_queryset(self):
        return Ticket.objects.order_by('pledge__user__first_name','details__name')

    def get_serializer_class(self):
        if self.action == 'update':
            return UpdateGuestListSerializer
        else:
            return GuestListSerializer

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class BookingRequestViewSet(viewsets.ModelViewSet):
    queryset = BookingRequest.objects.all()
    serializer_class = BookingRequestSerializer
    filter_class = filters.BookingRequestFilter
    permission_classes = [ 
        rest_framework_permissions.IsAuthenticated,
        permissions.VenueRequestPermission
    ]

    def create(self, request, *args, **kwargs):
        try:    
            return super().create(request, *args, **kwargs)

        except ValidationError as e:
            raise rest_framework_exceptions.ValidationError({'detail': e.message})


class BandToBandReviewViewSet(viewsets.ModelViewSet):
    queryset = BandToBandReview.objects.all()
    serializer_class = BandToBandReviewSerializer

    filter_fields = {
        'id': ('exact',),
        'band': ('exact',),
        'reviewer': ('exact',),
    }

    def update(self, request, *args, **kwargs):
        if 'is_completed' in self.request.data:
            mutable(request, True)
            request.data['completed_date'] = datetime.now()
            mutable(request, False)
        return super().update(request, *args, **kwargs)


class BandToVenueReviewViewSet(viewsets.ModelViewSet):
    queryset = BandToVenueReview.objects.all()
    serializer_class = BandToVenueReviewSerializer

    filter_fields = {
        'id': ('exact',),
        'venue': ('exact',),
        'reviewer': ('exact',),
    }

    def update(self, request, *args, **kwargs):
        if 'is_completed' in self.request.data:
            mutable(request, True)
            request.data['completed_date'] = datetime.now()
            mutable(request, False)
        return super().update(request, *args, **kwargs)


class VenueToBandReviewViewSet(viewsets.ModelViewSet):
    queryset = VenueToBandReview.objects.all()
    serializer_class = VenueToBandReviewSerializer

    filter_fields = {
        'id': ('exact',),
        'band': ('exact',),
        'reviewer': ('exact',),
    }

    def update(self, request, *args, **kwargs):
        if 'is_completed' in self.request.data:
            mutable(request, True)
            request.data['completed_date'] = datetime.now()
            mutable(request, False)
        return super().update(request, *args, **kwargs)


class SurveyResponseViewSet(viewsets.ModelViewSet):
    queryset = SurveyResponse.objects.all()
    serializer_class = SurveyResponseSerializer

    def create(self, request, *args, **kwargs):
        user = request.data['user']
        question = request.data['question']
        answer = request.data['response']

        if SurveyResponse.objects.filter(user=user,question=question,response=answer).count() == 0:
            return super().create(request, *args, **kwargs)
        else:
            return response.Response({}, status=200)


class HintViewSet(viewsets.ModelViewSet):
    queryset = Hint.objects.all()
    serializer_class = HintSerializer
    permission_classes = [
        rest_framework_permissions.IsAuthenticatedOrReadOnly,
        permissions.HintPermission,
    ]


class AdminMailViewSet(viewsets.ModelViewSet):
    queryset = AdminMail.objects.all()
    serializer_class = AdminMailSerializer


class RewardViewSet(viewsets.ModelViewSet):
    queryset = Reward.objects.all()
    serializer_class = RewardSerializer
    filter_class = filters.RewardFilter
    permission_classes = [
        rest_framework_permissions.IsAuthenticatedOrReadOnly,
        permissions.RewardPermission,
    ]


class GlobalSettingsViewSet(viewsets.ModelViewSet):
    queryset = GlobalSettings.objects.all()
    serializer_class = GlobalSettingsSerializer


class InvitationViewSet(viewsets.ModelViewSet):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer


class NavigationFeedbackViewSet(viewsets.ModelViewSet):
    queryset = NavigationFeedback.objects.all()
    serializer_class = NavigationFeedbackSerializer


class AccountSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = AccountSubscription.objects.all()
    permission_classes = [
        permissions.IsOwnerPermission
    ]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateAccountSubscriptionSerializer
        else:
            return AccountSubscriptionSerializer

    def create(self, *args, **kwargs):
        request = self.request

        if request.user.is_anonymous():
            raise PermissionDenied()

        request.data['user'] = request.user.id

        #Don't create a new subscription if one already exists.
        if AccountSubscription.objects.filter(user=request.user,is_cancelled=False,account_type=request.data['account_type'],product_name=request.data['product_name']).count() > 0:
            return response.Response({}, status=200)

        mutable(request, True)
        token = request.data.pop('token')
        mutable(request, False)

        customer = None
        try:
            amount = int(request.data['amount'] * 100.00)
            customer = square.models.Customer.objects.create_customer(email=request.user.email, token=token)
            metadata = 'U'+str(request.user.id)+' '+request.data['account_type']+'-'+request.data['product_name']

            customer.charge(
                amount=amount, 
                currency='CAD',#Expand to multi-currency (at least USA) soon. 
                metadata=metadata
            )
        except:
            mail.subscription_failed(email=request.user.email, data={'user': request.user})
            raise exceptions.BadRequest(ERROR_STRINGS.REJECTED_BY_SQUARE)

        request.data['square_customer'] = customer.id
        request.data['is_processed'] = True

        #Cancel MEMBER subscription if the user is buying ULTIMATE
        if request.data['product_name'] == 'ULTIMATE':
            AccountSubscription.objects.filter(
                account_type=request.data['account_type'],
                product_name='MEMBER',
                is_cancelled=False,
                user=request.user
                ).update(is_cancelled=True)

        #Cancel ARTIST MEMBER and/or VENUE MEMBER subscription if the user is buying ORGANIZER MEMBER
        if request.data['account_type'] == 'ORGANIZER' and request.data['product_name'] == 'MEMBER':
            AccountSubscription.objects.filter(
                Q(account_type='ARTIST') | Q(account_type='VENUE'),
                product_name='MEMBER',
                is_cancelled=False,
                user=request.user
                ).update(is_cancelled=True)

        mail.subscription_success(email=request.user.email, data={
            'user': request.user,
            'account_type': request.data['account_type'],
            'product_name': request.data['product_name']
            })

        res = super().create(request, *args, **kwargs)

        today = datetime.now()
        renewal_date = today + timedelta(days=30)
        tasks.renew_subscription(res.data.get('id'), schedule=renewal_date)
        return res


class BandSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = BandSubscription.objects.all()
    serializer_class = BandSubscriptionSerializer
    permission_classes = [
        permissions.IsOwnerPermission
    ]

    filter_fields = {
        'user': ('exact',),
        'band': ('in', 'exact',),
    }

    def create(self, *args, **kwargs):
        #Don't create a new subscription for anon
        if self.request.user.is_anonymous():
            return response.Response({}, status=200)
        #Don't create a new subscription if one already exists.
        if BandSubscription.objects.filter(user=self.request.user, band=self.request.data['band']).count() > 0:
            return response.Response({}, status=200)
        return super().create(self.request, *args, **kwargs)

    def destroy(self, *args, **kwargs):
        BandSubscription.objects.filter(user=self.request.user).delete()
        return response.Response({}, status=200)


class OrganizationSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = OrganizationSubscription.objects.all()
    serializer_class = OrganizationSubscriptionSerializer

    filter_fields = {
        'user': ('exact',),
        'organization': ('in', 'exact',),
    }

    def create(self, *args, **kwargs):
        #Don't create a new subscription for anon
        if self.request.user.is_anonymous():
            return response.Response({}, status=200)
        #Don't create a new subscription if one already exists.
        if OrganizationSubscription.objects.filter(user=self.request.user, organization=self.request.data['organization']).count() > 0:
            return response.Response({}, status=200)
        return super().create(self.request, *args, **kwargs)

    def destroy(self, *args, **kwargs):
        OrganizationSubscription.objects.filter(user=self.request.user).delete()
        return response.Response({}, status=200)


class VenueSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = VenueSubscription.objects.all()
    serializer_class = VenueSubscriptionSerializer

    filter_fields = {
        'user': ('exact',),
        'venue': ('in', 'exact',),
    }

    def create(self, *args, **kwargs):
        #Don't create a new subscription for anon
        if self.request.user.is_anonymous():
            return response.Response({}, status=200)

        #Don't create a new subscription if one already exists.
        if VenueSubscription.objects.filter(user=self.request.user, venue=self.request.data['venue']).count() > 0:
            return response.Response({}, status=200)
        return super().create(self.request, *args, **kwargs)

    def destroy(self, *args, **kwargs):
        VenueSubscription.objects.filter(user=self.request.user).delete()
        return response.Response({}, status=200)


class ActPaymentViewSet(viewsets.ModelViewSet):
    queryset = ActPayment.objects.all()
    serializer_class = ActPaymentSerializer

    def create(self, *args, **kwargs):
        user = self.request.user

        if user.is_anonymous():
            raise PermissionDenied()

        band = Band.objects.get(id=self.request.data['band'])
        organization = Organization.objects.get(pk=self.request.data['organization'])
        amount = decimal.Decimal(self.request.data['amount'])

        if organization.account_balance < amount:
            raise rest_framework_exceptions.ValidationError(detail=ERROR_STRINGS.INSUFFICIENT_FUNDS)

        payment = ActPayment.objects.create(
            band=band,
            campaign=None,
            organization=organization,
            amount=amount
        )

        organization.account_balance -= amount
        band.account_balance += amount

        organization.save()
        band.save()

        payment.paid = True
        payment.save()

        return response.Response({}, status=200)


class PaymentRequestViewSet(viewsets.ModelViewSet):
    queryset = PaymentRequest.objects.all()
    serializer_class = PaymentRequestSerializer

    def create(self, *args, **kwargs):
        user = self.request.user

        if user.is_anonymous():
            raise PermissionDenied()

        if user.profile.account_balance < decimal.Decimal(10.00):
            raise rest_framework_exceptions.ValidationError(detail=ERROR_STRINGS.INSUFFICIENT_FUNDS)

        PaymentRequest.objects.create(
            user=user,
            amount=user.profile.account_balance
        )
        user.profile.account_balance = 0.00
        user.profile.save()

        # Send updated user to update UI
        data = UserPrivilegedSerializer(user).data
        try:
            profile = Profile.objects.get(id=user.profile.id)
            data['profile'] = ProfilePrivilegedSerializer(profile).data
        except Exception as e:
            print(e)
            pass

        return response.Response(data, status=200)


###################
# NON-MODEL VIEWS #
###################

#VERY SIMILAR TO SHOWREQUESTVIEW - CHECK BOTH WHEN MODIFYTING THIS.
class JustTicketsView(generics.RetrieveAPIView, generics.CreateAPIView):
    serializer_class = JustTicketsSerializer

    def create(self, *args, **kwargs):
        user = self.request.user

        if user.is_anonymous():
            raise PermissionDenied()

        data = self.request.data
        title = data['title']
        performers = data['performers']
        date = datetime.strptime(data['date'],'%Y-%m-%dT%H:%M:%S')
        ticket_quantity = int(data['ticket_quantity'])

        ticket_price = decimal.Decimal(data['ticket_price']) if data['ticket_price'] else 0.00
        doors_price = decimal.Decimal(data['doors_price']) if data['doors_price'] else 0.00

        #If the request was created by organization
        organization = data.get('organization', None)
        if organization:
            organization = Organization.objects.get(pk=organization)

        headliner = None
        for performer in performers:
            if performer['is_headliner'] and performer['is_redpine']:
                headliner = performer['name']

            if not performer['is_redpine']:
                # Create the act
                act = Band.objects.create(
                    name=performer['name'],
                    short_bio=performer['name'] + ' hasn\'t added a bio yet.',
                    is_redpine=False,
                    join_token=secrets.token_hex(16)
                )
                act.facebook = performer.get('facebook', None)
                act.twitter = performer.get('twitter', None)
                act.instagram = performer.get('instagram', None)
                act.spotify = performer.get('spotify', None)
                act.youtube = performer.get('youtube', None)
                act.soundcloud = performer.get('soundcloud', None)
                act.bandcamp = performer.get('bandcamp', None)
                act.save()

                performer['band'] = act.id

                if performer['is_headliner']: 
                    """ Only case where an act will be submitted with is_redpine=False and is_headliner=True
                    will be when the user submitted a request without being logged in - meaning they 
                    made an act as part of the Play a Show form. """
                    headliner = performer['name']
                    act.is_redpine = True
                    act.owner = user
                    act.save()

        venue_name = data['venue_name']
        venue_address = data['venue_address']
        venue = Venue.objects.create(title=venue_name,address=venue_address,is_hidden=True)

        start_time = date.replace(hour=19,minute=0)
        end_time = start_time + timedelta(hours=5)

        timeslot = Timeslot.objects.create(
            venue=venue, 
            asking_price=decimal.Decimal(0),
            min_headcount=0,
            start_time=start_time,
            end_time=end_time
        )

        # Create the campaign
        description = "It\'s going to be a great show!"

        campaign = Campaign.objects.create(
            title=title,
            description=description,
            goal_count=0,
            goal_amount=0.00,
            min_ticket_price=ticket_price if ticket_price < doors_price else doors_price,
            picture=None,
            is_open=False,
            timeslot=timeslot,
            funding_type=Campaign.ALL_TO_ORGANIZER,
            funding_start=None,
            funding_end=timeslot.end_time,
            is_successful=True,
            is_venue_approved=True,
            is_only_tickets=True,
            created_by=user
        )

        if decimal.Decimal(ticket_price) == decimal.Decimal(doors_price):
            PurchaseItem.objects.create(
                name="Standard Ticket" if ticket_price > 0 else "RSVP",
                description="It'll get you in the door.",
                price=ticket_price,
                quantity=ticket_quantity,
                campaign=campaign,
                is_ticket=True
            )
        else:
            if ticket_price > 0 or (ticket_price == 0 and doors_price > 0):
                PurchaseItem.objects.create(
                    name="Early Ticket" if ticket_price > 0 else "RSVP",
                    description="Bigger fans get cheaper tickets." if ticket_price > 0 else "Let them know you're attending.",
                    price=ticket_price,
                    quantity=ticket_quantity,
                    campaign=campaign,
                    is_ticket=True
                )
            PurchaseItem.objects.create(
                name="Standard Ticket" if doors_price > 0 else "RSVP",
                description="Just like you get at the door!" if doors_price > 0 else "Let them know you're attending.",
                price=doors_price,
                quantity=ticket_quantity,
                campaign=campaign,
                is_ticket=True
            )

        for performer in performers:
            act = Band.objects.get(pk=performer['band'])
            CampaignBand.objects.create(
                band=act,
                is_headliner=performer['is_headliner'],
                is_accepted=performer['is_accepted'],
                is_application=True,
                campaign=campaign
            )
            if not performer['is_headliner']:
                #Check if the invited act was just created.
                act_name = act.name
                for performer_ in performers:
                    if performer_['name'] == act_name and performer_['is_redpine'] is False:
                        # Send an email to the invited act.
                        Invitation.objects.create(
                            template='ACT_SHOW_INVITE',
                            sender=user,
                            recipient_email=performer_['email'],
                            join_token=act.join_token,
                            data={
                                "campaign":campaign.id,
                                "join_token":act.join_token
                            }
                        )
                #Send invitation if it's not the user's act
                if act.owner and act.owner.id != user.id:
                    if act.owner.profile.receives_emails:
                        mail.act_show_invite(email=act.owner.email, data={'campaign':campaign})
                    
                        Notification.objects.create(
                            profile=act.owner.profile,
                            subject_type=1,#CAMPAIGN
                            text='{} has been invited to play {}!'.format(act.name,campaign.title),
                            campaign=campaign
                        )
        if organization:
            CampaignOrganization.objects.create(
                organization=organization,
                campaign=campaign,
                is_accepted=True
            )

        return response.Response({}, status=200)


#VERY SIMILAR TO JUSTTICKETSVIEW - CHECK BOTH WHEN MODIFYTING THIS.
class ShowRequestView(generics.RetrieveAPIView, generics.CreateAPIView):
    permission_classes = [
        rest_framework_permissions.IsAuthenticatedOrReadOnly
    ]

    def create(self, request):
        serializer = ShowRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if user.is_anonymous():
            raise PermissionDenied()

        has_pending_request = Campaign.objects.filter(
            created_by=user,
            is_venue_approved=None,
            timeslot__start_time__gt=datetime.now()
            ).count() > 0

        is_member_artist = helpers.has_subscription(user,AccountSubscription.ARTIST,AccountSubscription.MEMBER)
        is_member_organizer = helpers.has_subscription(user,AccountSubscription.ORGANIZER,AccountSubscription.MEMBER)

        if has_pending_request and not is_member_artist and not is_member_organizer:
            raise rest_framework_exceptions.ValidationError({'detail': ERROR_STRINGS.UPGRADE_ACCOUNT})

        data = request.data

        venue = data['venue']
        performers = data['performers']
        extra_slots = data['extra_slots']
        extra_info = data['extra_info']
        payout_type = data['payout_type']
        is_open = data['is_open']

        has_ticket_price = data['ticket_price']
        has_doors_price = data['doors_price']
        ticket_price = decimal.Decimal(data['ticket_price']) if has_ticket_price else 0.00
        doors_price = decimal.Decimal(data['doors_price']) if has_doors_price else 0.00

        #If the request was created from an existing timeslot
        timeslot = data.get('timeslot', None)
        opening = None
        if timeslot:
            timeslot = Timeslot.objects.get(pk=timeslot['id'])
            venue = timeslot.venue
            date = timeslot.start_time
            opening = Opening.objects.filter(timeslot=timeslot).first()
        else:
            date = datetime.strptime(data['date'],'%Y-%m-%dT%H:%M:%S')

        #If the request was created by organization
        organization = data.get('organization', None)
        if organization:
            organization = Organization.objects.get(pk=organization)

        #Should have a value if a city was selected. 
        headliner = None
        for performer in performers:
            if performer['is_headliner']:
                headliner = performer['name']

            if not performer['is_redpine']:
                # Create the act
                act = Band.objects.create(
                    name=performer['name'],
                    short_bio=performer['name'] + ' hasn\'t added a bio yet.',
                    is_redpine=False,
                    join_token=secrets.token_hex(16)
                )
                act.facebook = performer.get('facebook', None)
                act.twitter = performer.get('twitter', None)
                act.instagram = performer.get('instagram', None)
                act.spotify = performer.get('spotify', None)
                act.youtube = performer.get('youtube', None)
                act.soundcloud = performer.get('soundcloud', None)
                act.bandcamp = performer.get('bandcamp', None)
                act.save()

                performer['band'] = act.id

                if performer['is_headliner']:
                    """
                    Only case where an act will be submitted with is_redpine=False and is_headliner=True
                    will be when the user submitted a request without being logged in - meaning they 
                    made an act as part of the Play a Show form.
                    """
                    act.owner = user
                    act.is_redpine = True
                    act.save()

        #If the show is part of a tour
        tour = data.get('tour', None)

        campaign = None
        if venue:
            if timeslot:
                #Campaign goals for existing timeslot
                goal_count = timeslot.min_headcount
                goal_amount = timeslot.asking_price
                funding_end = timeslot.end_time
            else:
                #Create a new timeslot
                venue = Venue.objects.get(id=venue['id'])

                start_time = date.replace(hour=19,minute=0)
                end_time = start_time + timedelta(hours=5)
        
                timeslot = Timeslot.objects.create(
                    venue=venue, 
                    asking_price=decimal.Decimal(0),
                    min_headcount=0,
                    start_time=start_time,
                    end_time=end_time
                )
                funding_end = timeslot.end_time

            # Create the campaign
            title = date.strftime("%B %d") + " at " + venue.title
            description = "It\'s going to be a great show!"

            #Extra title details where possible
            if opening:
                title = opening.title + " @ " + venue.title
                description = "Playing " + opening.title + "!"
            elif headliner:
                title = headliner + " @ " + venue.title
                
            campaign = Campaign.objects.create(
                title=title,
                description=description,
                goal_count=0,
                goal_amount=0.00,
                min_ticket_price=min(ticket_price,doors_price),
                picture=None,
                is_open=is_open,
                timeslot=timeslot,
                payout_type=payout_type,
                funding_start=None,
                funding_end=funding_end,
                created_by=user,
                is_successful=True,
                is_redpine_approved=None,
                creator_organization=organization
            )

            if has_ticket_price or has_doors_price:
                if decimal.Decimal(ticket_price) == decimal.Decimal(doors_price):
                    PurchaseItem.objects.create(
                        name="Standard Ticket" if ticket_price > 0 else "RSVP",
                        description="It'll get you in the door.",
                        price=ticket_price,
                        quantity=venue.capacity,
                        campaign=campaign,
                        is_ticket=True
                    )
                else:
                    if ticket_price > 0 or (ticket_price == 0 and doors_price > 0):
                        PurchaseItem.objects.create(
                            name="Early Ticket" if ticket_price > 0 else "RSVP",
                            description="Bigger fans get cheaper tickets." if ticket_price > 0 else "Let them know you're attending.",
                            price=ticket_price,
                            quantity=venue.capacity,
                            campaign=campaign,
                            is_ticket=True
                        )
                    PurchaseItem.objects.create(
                        name="Standard Ticket" if doors_price > 0 else "RSVP",
                        description="Just like you get at the door!" if doors_price > 0 else "Let them know you're attending.",
                        price=doors_price,
                        quantity=venue.capacity,
                        campaign=campaign,
                        is_ticket=True
                    )

            for performer in performers:
                act = Band.objects.get(pk=performer['band'])
                CampaignBand.objects.create(
                    band=act,
                    is_headliner=performer['is_headliner'],
                    is_accepted=performer['is_accepted'],
                    is_application=True,
                    campaign=campaign
                )
                if not performer['is_headliner']:
                    #Check if the invited act was just created.
                    act_name = act.name
                    for performer_ in performers:
                        if (performer_['name'] == act_name) and (performer_['is_redpine'] is False):
                            # Send an email to the invited act.
                            Invitation.objects.create(
                                template='ACT_SHOW_INVITE',
                                sender=user,
                                recipient_email=performer_['email'],
                                join_token = act.join_token,
                                data={
                                    "campaign":campaign.id,
                                    "join_token":act.join_token
                                }
                            )
                    #Send invitation if it's not the user's act
                    if act.owner and act.owner.id != user.id:
                        if act.owner.profile.receives_emails:
                            mail.act_show_invite(email=act.owner.email, data={'campaign':campaign})
                        
                            Notification.objects.create(
                                profile=act.owner.profile,
                                subject_type=1,#CAMPAIGN
                                text='{} has been invited to play {}!'.format(act.name,campaign.title),
                                campaign=campaign
                            )
            if organization:
                CampaignOrganization.objects.create(
                    organization=organization,
                    campaign=campaign,
                    is_accepted=True
                )
            if extra_info:
                CampaignFeed.objects.create(
                    campaign=campaign,
                    sender=user,
                    sent_notification=False,
                    is_system=False,
                    item_type=1,#MESSAGE
                    text=extra_info
                )
            if tour:
                tour = Tour.objects.get(pk=tour)
                TourCampaign.objects.create(
                    tour=tour,
                    campaign=campaign
                )
            mail.booking_recieved(email=user.email, data={'user':user})

        #Make a generic booking request
        act_string = ''
        for performer in performers:
            act_string += performer['name'] + ', \n '

        if is_open:
            act_string += ' and the show is open for applications to play.'

        if has_ticket_price:
            extra_details = 'Ticket Price: '+str(ticket_price)
        else:
            extra_details = 'No ticketing chosen.'

        if tour and not venue:
            extra_details += '\n Added as part of a tour but no venue was chosen. (So it hasn\'t actually been added yet)'

        extra_details += '\n'
        extra_details += extra_info

        BookingRequest.objects.create(
            user=user,
            venue=venue,
            campaign=campaign,
            when=date.strftime("%m %d %Y"),
            who=act_string,
            extra_details=extra_details,
            organization=organization
        )

        return response.Response({}, status=200)


class TaskView(generics.RetrieveAPIView):
    def get(self, *args, **kwargs):
        while background_task.tasks.tasks.run_next_task(None):
            pass

        return response.Response({}, status=200)


class MeView(generics.RetrieveAPIView, generics.CreateAPIView):
    """ special view to load the requesting user's profile """
    def get(self, *args, **kwargs):
        user = self.request.user

        if user.is_anonymous():
            raise PermissionDenied()

        data = UserPrivilegedSerializer(user).data
        data['profile'] = None

        try:
            profile = Profile.objects.get(id=user.profile.id)
            data['profile'] = ProfilePrivilegedSerializer(profile).data

        except Exception as e:
            print(e)
            pass

        return response.Response(data, status=200)

    def create(self, *args, **kwargs):
        user = self.request.user

        if user.is_anonymous():
            raise PermissionDenied()

        if 'profile' in self.request.data:
            profile_data = self.request.data.pop('profile')
            profile_serializer = ProfilePrivilegedSerializer(data=profile_data)
            profile_serializer.is_valid(raise_exception=True)
            profile = Profile.objects.filter(user=user).first()

            for key, val in profile_serializer.validated_data.items():
                setattr(profile, key, val)

            profile.save()

        return self.get(*args, **kwargs)


class EmailDebugView(TemplateView):
    def get_template_names(self):
        return 'mail/{}.html'.format(self.request.GET.get('template'))

    def get_context_data(self):
        return self.request.GET


class JobRunnerStatusView(generics.RetrieveAPIView):
    def get(self, *args, **kwargs):
        first = JobRunnerCheckin.objects.first()
        now = datetime.now()

        if first is None or (now - first.modified).seconds >= 90:
            return response.Response({}, status=500)

        return response.Response({}, status=200)


class AppCashTransactionViewSet(viewsets.ModelViewSet):
    permission_classes = [rest_framework_permissions.IsAuthenticated, permissions.AppTransactionPermission]
    serializer_class = AppCashTransactionSerializer
    queryset = AppCashTransaction.objects.all()

    def create(self, request, *args, **kwargs):
        get_array = lambda key: request.data.get(key) if request.data.get(key).__class__ == list else [request.data.get(key)]
        campaign = Campaign.objects.get(pk=request.data.get('campaign'))
        bands = [CampaignBand.objects.get(pk=id) for id in get_array('bands')]
        items = [PurchaseItem.objects.get(pk=id) for id in get_array('items')]
        quantities = [Decimal(q) for q in get_array('quantities')]
        total = sum([quantities[index] * item.price for index, item in enumerate(items)])
        redpine_fee = total * (campaign.service_fee / Decimal('100')) if campaign.service_fee > Decimal('0') else Decimal('0')
        count = sum([quantities[index] if item.is_ticket else 0 for index, item in enumerate(items)])

        mutable(request, True)
        request.data['total'] = round(total, 2)
        request.data['redpine_fee'] = round(redpine_fee, 2)
        request.data['count'] = count
        request.data['payouts_processed'] = False
        request.data['processed_by'] = request.user.id
        mutable(request, False)

        res = super().create(request, *args, **kwargs)
        transaction = AppCashTransaction.objects.get(pk=res.data.get('id'))
        purchases = [
            AppCashTransactionPurchase.objects.create(
                transaction=transaction,
                item=item,
                quantity=quantities[index]
            ) for index, item in enumerate(items)
        ]
        serializer = AppCashTransactionSerializer(transaction)
        return response.Response(serializer.data, status=201)


class AppCardTransactionViewSet(viewsets.ModelViewSet):
    permission_classes = [rest_framework_permissions.IsAuthenticated, permissions.AppTransactionPermission]
    serializer_class = AppCardTransactionSerializer
    queryset = AppCardTransaction.objects.all()

    def create(self, request, *args, **kwargs):
        get_array = lambda key: request.data.get(key) if request.data.get(key).__class__ == list else [request.data.get(key)]
        campaign = Campaign.objects.get(pk=request.data.get('campaign'))
        bands = [CampaignBand.objects.get(pk=id) for id in get_array('bands')]
        items = [PurchaseItem.objects.get(pk=id) for id in get_array('items')]
        quantities = [Decimal(q) for q in get_array('quantities')]
        total = sum([quantities[index] * item.price for index, item in enumerate(items)])
        redpine_fee = total * (campaign.service_fee / Decimal('100')) if campaign.service_fee > Decimal('0') else Decimal('0')
        count = sum([quantities[index] if item.is_ticket else 0 for index, item in enumerate(items)])

        mutable(request, True)
        request.data['total'] = round(total, 2)
        request.data['redpine_fee'] = round(redpine_fee, 2)
        request.data['count'] = count
        request.data['payouts_processed'] = False
        request.data['processed_by'] = request.user.id
        mutable(request, False)

        res = super().create(request, *args, **kwargs)
        transaction = AppCardTransaction.objects.get(pk=res.data.get('id'))
        purchases = [
            AppCardTransactionPurchase.objects.create(
                transaction=transaction,
                item=item,
                quantity=quantities[index]
            ) for index, item in enumerate(items)
        ]
        serializer = AppCardTransactionSerializer(transaction)
        return response.Response(serializer.data, status=201)

    @decorators.detail_route(methods=['post'], permission_classes=[
        rest_framework_permissions.IsAuthenticated,
        permissions.AppTransactionPermission
    ])
    def square_pos_callback(self, request, pk=None):
        # not sure why this isn't getting picked up as pk..
        match = re.search('([0-9]+)\/square_pos_callback', request.path)
        if match:
            obj_id = match.groups(1)[0]
            transaction = AppCardTransaction.objects.get(pk=obj_id)

        else:
            return response.Response({}, status=400)

        data = request.data

        transaction.transaction_id = data.get('transaction_id')
        transaction.client_transaction_id = data.get('client_transaction_id')
        transaction.save()
        return response.Response({}, status=204)


class SquarePOSCallbackView(generics.RetrieveAPIView):
    def get(self, *args, **kwargs):
        res = HttpResponse(None, status=302)
        status = None
        if self.request.GET.get('data', None):
            data = json.loads(self.request.GET.get('data'))
            status = data.get('status', None)
            if status == 'error':
                error_code = data.get('error_code', None)
                if error_code:
                    status = error_code

            elif status == 'ok':
                status = 'success__{}__{}'.format(data.get('transaction_id'), data.get('client_transaction_id'))

        if not status:
            status = 'unknown'

        location = 'redpinemusic://square-pos-callback/{}'.format(status)
        res['Location'] = location
        return res


class PushTokenViewSet(viewsets.ModelViewSet):
    permission_classes = [rest_framework_permissions.IsAuthenticated, permissions.PushTokenPermission]
    serializer_class = PushTokenSerializer
    queryset = PushToken.objects.all()

    def create(self, request, *args, **kwargs):
        mutable(request, True)
        request.data['user'] = request.user.id
        mutable(request, False)
        token = request.data['token']
        qs = PushToken.objects.filter(user=request.user, token=token)
        if qs.exists():
            serializer = PushTokenSerializer(qs.first())
            return response.Response(serializer.data, status=200)
        return super().create(request, *args, **kwargs)

    @decorators.list_route(methods=['delete'])
    def delete_by_token(self, request):
        PushToken.objects.filter(token=request.GET.get('token')).delete()
        return response.Response({}, status=204)


class MessagesViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().order_by('sent_at')
    serializer_class = MessageSerializer

    @decorators.detail_route(methods=['get'])
    def unread(self, request, pk=None):
        if self.request.user.is_anonymous():
            raise PermissionDenied()

        messages = Inbox.get_unread_messages(self.request.user)
        results = self.get_serializer(messages, many=True).data
        return response.Response({'results': results}, status=200)

    @decorators.detail_route(methods=['post'])
    def send(self, request, pk=None):
        recipient = self.request.data.get('recipient')
        text = self.request.data.get('text')

        try:
            user2 = User.objects.get(pk=recipient)
            Inbox.send_message(self.request.user, user2, text)    
            return response.Response({}, status=200)
        except Exception as e:
            print(e)
            return response.Response({'error':'Could not send.'}, status=500)
        
    @decorators.detail_route(methods=['post'])
    def read(self, request, pk=None):
        try:
            text = Inbox.read_message(pk)
            return response.Response({'text': text}, status=200)
        except Exception as e:
            print(e)
            return response.Response({'error':'Could not read.'}, status=500)
        
    @decorators.detail_route(methods=['post'])
    def read_formatted(self, request, pk=None):
        message = self.request.data.get('message')
        try:
            text = Inbox.read_message_formatted(message)
            return response.Response({'text': text}, status=200)
        except Exception as e:
            print(e)
            return response.Response({'error':'Could not read.'}, status=500)

    @decorators.detail_route(methods=['get'])
    def conversations(self, request, pk=None):
        conversations = Inbox.get_conversations(self.request.user)
        results = UserSerializer(conversations, many=True).data
        return response.Response({'results': results}, status=200)

    @decorators.detail_route(methods=['get'])
    def conversation(self, request, pk=None):
        keyword_args = dict(
            user1 = self.request.user,
            user2 = self.request.GET.get('recipient'),
            limit = self.request.GET.get('limit', None),#Optional
            reversed = self.request.GET.get('reversed', None),#Optional
            mark_read = self.request.GET.get('mark_read', None)#Optional
        )
        conversation = Inbox.get_conversation(**{k: v for k, v in keyword_args.items() if v is not None})
        results = self.get_serializer(conversation, many=True).data
        return response.Response({'results': results}, status=200)
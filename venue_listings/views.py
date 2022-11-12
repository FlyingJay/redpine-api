from django.shortcuts import render
from django.conf import settings
from django.core import serializers
from django.utils.translation import ugettext as _
from rest_framework import viewsets, response, generics, decorators, permissions as rest_framework_permissions, exceptions as rest_framework_exceptions
from venue_listings import permissions
from venue_listings.models import *
from venue_listings.serializers import *
import google
google_client = google.GoogleClient(settings.GOOGLE_API_KEY)


class ERROR_STRINGS:
    ADDRESS_NOT_FOUND = _('This address appears to be invalid.')
    REJECTED_BY_SQUARE = _('Square couldn\'t use the card info provided.')


def mutable(request, value):
    if hasattr(request.data, '_mutable'):
        request.data._mutable = value


class VenueViewSet(viewsets.ModelViewSet):
    permission_classes = [
        rest_framework_permissions.IsAuthenticatedOrReadOnly,
        permissions.VenuePermission
    ]
    queryset = Venue.objects.filter(archived=False).select_related('city__province__country','primary_genre','secondary_genre')

    def get_serializer_class(self):
        if self.action == 'update':
            return VenueUpdateSerializer
        elif self.action == 'create':
            return VenueCreateSerializer
        else:
            return VenueSerializer

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
        return super().create(request, *args, **kwargs)
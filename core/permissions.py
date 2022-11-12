from django.contrib.auth.models import User
from rest_framework import permissions
from django.db.models import Q
from core import models
import re


class user_is():
    def campaign_owner_or_band_or_venue_or_organization(campaign,user_id):
        return campaign.filter(
                Q(created_by=user_id) | 
                Q(bands__owner__id=user_id) | 
                Q(timeslot__venue__managers__id=user_id) | 
                Q(organizations__managers__id=user_id)).distinct().count() > 0


class IsOwnerPermission(permissions.BasePermission):
    """ Checks to see if the `.user` attribute of the associated model is actually the owner """

    def has_permission(self, request, view):
        # no idea why DRF is routing DELETE through here, it's really annoying
        return request.user.is_authenticated()

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class WebTransactionPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous():
            return False
        return True

    """ Prevents a user from updating any transaction """
    def has_object_permission(self, request, view, obj):
        if request.method == 'PUT':
            campaign = models.Campaign.objects.filter(id=obj.campaign.id)
            return user_is.campaign_owner_or_band_or_venue_or_organization(campaign,request.user.id)
        elif request.method == 'DELETE':
            return obj.user == request.user
        return True


class TicketPermission(permissions.BasePermission):
    """ Only allow users to access tickets which belong to them, and never modify / create """
    def has_permission(self, request, view):
        return request.method == 'GET'

    def has_object_permission(self, request, view, obj):
        return request.method == 'GET'


class GuestListPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method == 'GET' or request.method == 'PUT'


class MyProfilePermission(permissions.BasePermission):
    """ Only allow the profile owner access """
    def has_permission(self, request, view):
        return request.method == 'GET'

    def has_object_permission(self, request, view, obj):
        return request.method == 'GET'


class EventPermission(permissions.BasePermission):
    """ read only access if user is not venue manager """
    def has_permission(self, request, view):
        if request.method == 'POST':
            venue_id = int(request.data.get('venue', -1))
            return request.user.venues.filter(id=venue_id).count() > 0
        return True

    def has_object_permission(self, request, view, obj):
        return obj.venue.managers.filter(id=request.user.id).count() > 0


class TimeslotPermission(permissions.BasePermission):
    """ editable by venue managers and artists in the campaign """
    def has_permission(self, request, view):
        if request.method == 'POST':
            venue_id = int(request.data.get('venue', -1))
            return request.user.venues.filter(id=venue_id).count() > 0
        return True

    def has_object_permission(self, request, view, obj):
        if request.method == 'PUT' or request.method == 'DELETE':
            if models.Timeslot.objects.filter(id=obj.id, venue__managers__id=request.user.id).count() > 0:
                return True

            campaign = models.Campaign.objects.filter(timeslot=obj.id)
            return user_is.campaign_owner_or_band_or_venue_or_organization(campaign, request.user.id)
        return False


class BandPermission(permissions.BasePermission):
    """ only owner may delete, act members may edit """
    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return True
        else:
            is_owner = models.Band.objects.filter(Q(owner=request.user), id=obj.id).count() > 0
            return is_owner


class CampaignPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST' and request.user.is_anonymous():
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return True
        else:    
            campaign = models.Campaign.objects.filter(id=obj.id)
            return user_is.campaign_owner_or_band_or_venue_or_organization(campaign, request.user.id)


class CampaignDocumentPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        campaign = models.Campaign.objects.filter(id=obj.campaign.id)
        return user_is.campaign_owner_or_band_or_venue_or_organization(campaign, request.user.id)


class CampaignBandPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            campaign = models.Campaign.objects.filter(id=obj.campaign.id)
            return user_is.campaign_owner_or_band_or_venue_or_organization(campaign, request.user.id)
        else:
            return True

    def has_permission(self, request, view):
        if request.method == 'GET' or request.method == 'PUT':
            return True

        elif request.method == 'POST':
            campaign = models.Campaign.objects.filter(id=request.data.get('campaign', None))
            #ACTS MAY BE ADDED BY A NON-ORGANIZER IF THE SHOW IS OPEN
            if campaign.filter(is_open=True).count() > 0:
                return True
            #IF NOT, ONLY A SHOW MEMBER
            return user_is.campaign_owner_or_band_or_venue_or_organization(campaign, request.user.id)

        elif request.method == 'DELETE':
            return True #Handled in object permissions.
        return False


class OrganizationBandPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return True
        else:
            in_band = models.Band.objects.filter(owner=request.user, id=obj.band.id).count() > 0
            in_organization = models.Organization.objects.filter(managers=request.user, id=obj.organization.id).count() > 0
            return (in_band or in_organization)

    def has_permission(self, request, view):
        return True


class PurchaseItemPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return True
        elif request.method == 'POST' or request.method == 'PUT' or request.method == 'DELETE':
            purchase_item = models.PurchaseItem.objects.get(id=obj.id)
            campaign = models.Campaign.objects.filter(id=purchase_item.campaign.id)
            return user_is.campaign_owner_or_band_or_venue_or_organization(campaign, request.user.id)
        return False


class OrganizationPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return True
        else:
            return obj.managers.filter(id=request.user.id).count() > 0

    def has_permission(self, request, view):
        return True


class VenuePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return True
        else:
            return obj.managers.filter(id=request.user.id).count() > 0

    def has_permission(self, request, view):
        return True


class VenueRequestPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method == 'POST'

    def has_permission(self, request, view):
        return request.method == 'POST'


class HintPermission(permissions.BasePermission):
    """ read only access if user is not owner of the band """
    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return True
        return False


class RewardPermission(permissions.BasePermission):
    """ read only access if user is not owner of the band """
    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return True
        return False


class AppTransactionPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return False

    def has_permission(self, request, view):
        if request.method != 'POST':
            return False

        # not sure why this isn't getting picked up as an object...
        match = re.search('([0-9]+)\/square_pos_callback', request.path)
        if match:
            obj_id = match.groups(1)[0]
            transaction = models.AppCardTransaction.objects.get(pk=obj_id)
            campaign = transaction.campaign
        else:
            _campaign = models.Campaign.objects.filter(pk=request.data.get('campaign'))
            if not _campaign.exists(): return False
            campaign = _campaign.first()

        if 'door_code' in request.data:
            door_code_raw = request.data.pop('door_code') 
            door_code = door_code_raw[0] if type(door_code_raw) == list else door_code_raw
            if door_code == campaign.door_code and campaign.door_code is not None and door_code != '':
                return True

        campaign = models.Campaign.objects.filter(id=campaign.id)
        return user_is.campaign_owner_or_band_or_venue_or_organization(campaign, request.user.id)


class PushTokenPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return False

    def has_permission(self, request, view):
        if request.path == '/v1/push-tokens/delete_by_token/':
            token = request.GET.get('token', None)
            if not token: return False
            if request.method != 'DELETE': return False
            push_token = models.PushToken.objects.filter(token=token)
            if not push_token.exists(): return False
            push_token = push_token.first()
            if push_token.user != request.user: return False
            return True

        return request.method == 'POST'
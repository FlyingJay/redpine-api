from django.shortcuts import render
from django.conf import settings
from django.core import serializers
from django.utils.translation import ugettext as _
from rest_framework import viewsets, response, generics, decorators, permissions as rest_framework_permissions, exceptions as rest_framework_exceptions
from cover_bands import permissions
from cover_bands.models import *
from cover_bands.serializers import *
import google


def mutable(request, value):
    if hasattr(request.data, '_mutable'):
        request.data._mutable = value

class CoverLeadViewSet(viewsets.ModelViewSet):
    queryset = CoverLead.objects.all()
    serializer_class = CoverLeadSerializer
    permission_classes = [
        rest_framework_permissions.AllowAny
    ]
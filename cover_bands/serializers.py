from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from expander import ExpanderSerializerMixin
from rest_framework import serializers
from drf_extra_fields import fields as drf_extra_fields, geo_fields
from cover_bands.models import *


class CoverLeadSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = CoverLead
        fields = [
            'id',
            'email',
            'price',
            'message'
        ]


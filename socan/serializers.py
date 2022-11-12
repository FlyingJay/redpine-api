from rest_framework import serializers
from .models import *


class CreateVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Verification
        fields = [
            'id',
            'user',
            'number',
            'legal_name'
        ]


class GetVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Verification
        fields = [
            'id',
            'user',
            'number',
            'is_successful'
        ]

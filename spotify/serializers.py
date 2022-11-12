from rest_framework import serializers
from .models import *


class AuthSerializer(serializers.Serializer):
    redirect_uri = serializers.URLField()


class ConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpotifyConnection
        fields = [
            'id',
            'client_id',
            'access_token',
            'expiration_date'
        ]

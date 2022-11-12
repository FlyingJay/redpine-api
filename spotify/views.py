from rest_framework import generics, decorators, viewsets
from rest_framework.response import Response
from django.conf import settings
from core.auth import exceptions
from .spotify import SpotifyClient, SpotifyException
from .serializers import *
from .models import *


class ConnectionViewSet(viewsets.ModelViewSet):
    queryset = SpotifyConnection.objects.all()

    def get_serializer_class(self):
        return ConnectionSerializer if self.action == 'update' else AuthSerializer

    # Ensure that RedPine's spotify connection is up and running
    def create(self, request):
        serializer = AuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = request.data.get('code')
        redirect_uri = request.data.get('redirect_uri')

        client = SpotifyClient(settings.SPOTIFY_APP_ID, settings.SPOTIFY_APP_SECRET)
        connection = SpotifyConnection.objects.all().first()

        if code is not None:
            try:
                connection = client.login(code, redirect_uri)
            except Exception as e:
                raise SpotifyException('Spotify login failed')
        elif connection is not None:
            try:
                connection = client.refresh(connection)
            except Exception as e:
                raise SpotifyException('Spotify refresh failed')

        serializer = ConnectionSerializer(connection)
        return Response(serializer.data, status=200)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


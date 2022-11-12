from django.db import models

class SpotifyConnection(models.Model):
    client_id = models.CharField(max_length=500, null=True, default=None)
    access_token = models.CharField(max_length=500, null=True, default=None)
    refresh_token = models.CharField(max_length=500, null=True, default=None)
    expiration_date = models.DateTimeField(null=True, default=None)

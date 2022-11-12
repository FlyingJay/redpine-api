from django.conf import settings
from django.core.management import BaseCommand
from inconcert.models import *
from inconcert.helpers import count_likes_from_text
from django.contrib.gis.geos import Point
import google
import time 

google_client = google.GoogleClient(settings.GOOGLE_API_KEY)


class Command(BaseCommand):
    help = 'Load object coordinates from google API'

    def add_arguments(self, parser):
        parser.add_argument('--model', type=str)
        parser.add_argument('--delay', type=int)

    def handle(self, *args, **kwargs):
        model = kwargs['model']
        delay = kwargs['delay']

        objs = []
        if model == 'artist':
            objs = Artist.objects.filter(location=None,location_text__icontains='oronto')
        if model == 'venue':
            objs = Venue.objects.filter(location=None)

        for obj in objs:
            location = None
            try:
                geocoded = google_client.geocode(obj.location_text)
                location = Point(geocoded.location.y,geocoded.location.x)
            except google.GoogleNoResultsException:
                pass
            obj.location = location
            obj.save()
            time.sleep(delay)

        print("done.")
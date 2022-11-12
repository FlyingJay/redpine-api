from django.conf import settings
from django.core.management import BaseCommand
from inconcert.models import *
from inconcert.helpers import count_likes_from_text
from django.contrib.gis.geos import Point
import google
import time 

google_client = google.GoogleClient(settings.GOOGLE_API_KEY)


class Command(BaseCommand):
    help = 'Load import models into a useable format.'

    def add_arguments(self, parser):
        parser.add_argument('--model', type=str)
        parser.add_argument('--geocode', type=bool)
        parser.add_argument('--geocode_delay', type=int)

    def import_artists(self, geocode=True, geocode_delay=0):
        raw_artists = ArtistImport.objects.filter(is_imported=False)
        genres = Genre.objects.all()

        for artist in raw_artists:
            facebook = "https://www.facebook.com/{0}".format(artist.facebook)

            if Artist.objects.filter(facebook=facebook).count() == 0:
                location_text = artist.hometown
                if artist.address:
                    location_text = artist.address

                location = None
                #if geocode:
                #    try:
                #        time.sleep(geocode_delay)
                #        geocoded = google_client.geocode(location_text)
                #        location = Point(geocoded.location.y,geocoded.location.x)
                #    except google.GoogleNoResultsException:
                #        pass

                description = artist.story
                if artist.biography:
                    description = artist.biography

                new_artist = Artist.objects.create(
                    name=artist.name,
                    picture=None,#artist.image,
                    description=description[0:9999],
                    likes=count_likes_from_text(artist.likes),
                    location=location,
                    location_text=location_text[0:9999],
                    #Contact Info
                    email=artist.email,
                    phone=artist.phone,
                    facebook=facebook,
                    messenger="https://www.messenger.com/t/{0}".format(artist.facebook),
                    twitter=artist.twitter,
                    instagram=artist.instagram,
                    spotify=artist.spotify,
                    soundcloud=artist.soundcloud,
                    bandcamp=artist.bandcamp,
                    youtube=artist.youtube,
                    website=artist.website,
                    #Raw data
                    import_data=artist
                    )

                #Add genres
                for genre in genres:
                    if genre.name in artist.genre:
                        new_artist.genres.add(genre)
                new_artist.save()
            
            artist.is_imported = True
            artist.save()

    def import_venues(self, geocode=True, geocode_delay=0):
        raw_venues = VenueImport.objects.filter(is_imported=False)
        genres = Genre.objects.all()

        for venue in raw_venues:
            facebook = "https://www.facebook.com/{0}".format(venue.facebook)

            if Artist.objects.filter(facebook=facebook).count() == 0:
                location_text = venue.hometown
                if venue.address:
                    location_text = venue.address

                location = None
                #if geocode:
                #    try:
                #        time.sleep(geocode_delay)
                #        geocoded = google_client.geocode(location_text)
                #        location = Point(geocoded.location.y,geocoded.location.x)
                #    except google.GoogleNoResultsException:
                #        pass

                description = venue.story
                if venue.biography:
                    description = venue.biography

                new_venue = Venue.objects.create(
                    name=venue.name,
                    picture=None,#venue.image,
                    description=description[0:9999],
                    likes=count_likes_from_text(venue.likes),
                    location=location,
                    location_text=location_text[0:9999],
                    #Contact Info
                    email=venue.email,
                    phone=venue.phone,
                    facebook=facebook,
                    messenger="https://www.messenger.com/t/{0}".format(venue.facebook),
                    twitter=venue.twitter,
                    instagram=venue.instagram,
                    spotify=venue.spotify,
                    soundcloud=venue.soundcloud,
                    bandcamp=venue.bandcamp,
                    youtube=venue.youtube,
                    website=venue.website,
                    #Raw data
                    import_data=venue
                    )

            venue.is_imported = True
            venue.save()

    def import_events(self):
        raw_events = EventImport.objects.filter(is_imported=False)

        #FORMAT EVENT LINKS, IDEALLY DONE IN CSV BEFORE IMPORT
        #for raw_event in raw_events:
        #    if(raw_event.event_link.find('?')):
        #        raw_event.event_link = raw_event.event_link[0:raw_event.event_link.find('?')-1]
        #        raw_event.save()

        for raw_event in raw_events:
            performers = Artist.objects.filter(facebook=raw_event.profile_link)
            venues = Venue.objects.filter(facebook=raw_event.profile_link)  

            event = None
            events = Event.objects.filter(link=raw_event.event_link)#Should only get one

            if events.count() > 0:
                event = events.first()
            else:
                event = Event.objects.create(
                    link=raw_event.event_link
                )
           
            if performers.count() > 0:
                event.artists.add(*performers)
            
            if venues.count() > 0:
                event.venues.add(*venues)

            raw_event.is_imported = True
            raw_event.save()

    def import_venue_genres(self):
        venues = Venue.objects.all()
        for venue in venues:
            #if venue.genres.count() == 0:
            venue.genres.add(*Genre.objects.filter(inconcert_artists__events__venues=venue).distinct())
            venue.save()

    def handle(self, *args, **kwargs):
        model = kwargs['model']
        geocode = kwargs['geocode']
        geocode_delay = kwargs['geocode_delay']

        if model == 'artist':
            self.import_artists(geocode,geocode_delay)
        if model == 'venue':
            self.import_venues(geocode,geocode_delay)
        if model == 'event':
            self.import_events()
        if model == 'genre':
            self.import_venue_genres()
        elif model == 'all':
            self.import_artists()
            self.import_venues()
            self.import_events()
            self.import_venue_genres()

        print("done.")
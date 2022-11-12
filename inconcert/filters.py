import rest_framework_filters as filters
from core.models import Genre
from core.filters import GenreFilter
from .models import *

class ArtistFilter(filters.FilterSet):
    popularity = filters.CharFilter(name='popularity', method='filter_popularity')
    genres = filters.RelatedFilter(GenreFilter, queryset=Genre.objects.all())

    def filter_popularity(self, queryset, name, value):
    	if int(value) == Artist.SUPER_LOCAL: 
    		return queryset.filter(likes_lt=1000)
    	elif int(value) == Artist.LOCAL:
    		return queryset.filter(likes_gte=1000,likes_lt=10000)
    	elif int(value) == Artist.INDIE:
    		return queryset.filter(likes_gte=10000,likes_lt=50000)
    	elif int(value) == Artist.POPULAR:
    		return queryset.filter(likes_gte=50000,likes_lt=1000000)
    	elif int(value) == Artist.LEGEND:
    		return queryset.filter(likes_gte=1000000)
    	elif int(value) == Artist.NO_INFO:
    		return queryset.filter(likes__isnull=True)

    class Meta:
        model = Artist
        fields = {
            'id': ['in', 'exact'],
            'name': ['icontains'],
        }


class VenueFilter(filters.FilterSet):
    genres = filters.RelatedFilter(GenreFilter, queryset=Genre.objects.all())

    class Meta:
        model = Venue
        fields = {
            'name': ['icontains'],
        }


class EventFilter(filters.FilterSet):
    artists = filters.RelatedFilter(ArtistFilter, queryset=Artist.objects.all())
    venues = filters.RelatedFilter(VenueFilter, queryset=Venue.objects.all())

    class Meta:
        model = Event
        fields = {
            'id': ['in', 'exact'],
        }
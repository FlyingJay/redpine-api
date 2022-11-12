from .models import *

"""
modelAdmin -> current Model, sometimes used for Meta properties
request -> haven't needed it yet (permissions?)
queryset -> the set of model records on which to apply the action
"""
def update_artist(modelAdmin, request, queryset):
	for update in queryset.all():
		if not update.is_applied:
		    artist = Artist.objects.get(pk=update.artist.id)

		    if update.name:
		    	artist.name = update.name
		    if update.picture:
		    	artist.picture = update.picture
		    if update.description:
		    	artist.description = update.description
		    if update.location_text:
		    	artist.location_text = update.location_text
		    if update.genres.all().count() > 0:
		    	artist.genres.clear()
		    	for genre in update.genres.all():
		    		artist.genres.add(genre)

		    if update.email:
		    	artist.email = update.email
		    if update.phone:
		    	artist.phone = update.phone
		    if update.facebook:
		    	artist.facebook = update.facebook
		    if update.messenger:
		    	artist.messenger = update.messenger
		    if update.twitter:
		    	artist.twitter = update.twitter
		    if update.instagram:
		    	artist.instagram = update.instagram
		    if update.spotify:
		    	artist.spotify = update.spotify
		    if update.soundcloud:
		    	artist.soundcloud = update.soundcloud
		    if update.bandcamp:
		    	artist.bandcamp = update.bandcamp
		    if update.youtube:
		    	artist.youtube = update.youtube
		    if update.website:
		    	artist.website = update.website

		    update.is_applied = True
		    artist.save()
		    update.save()

update_artist.short_description = u"Apply Update(s)"


def update_venue(modelAdmin, request, queryset):
	for update in queryset.all():
		if not update.is_applied:
		    venue = Venue.objects.get(pk=update.venue.id)

		    if update.name:
		    	venue.name = update.name
		    if update.picture:
		    	venue.picture = update.picture
		    if update.description:
		    	venue.description = update.description
		    if update.location_text:
		    	venue.location_text = update.location_text
		    if update.genres.all().count() > 0:
		    	venue.genres.clear()
		    	for genre in update.genres.all():
		    		venue.genres.add(genre)

		    if update.email:
		    	venue.email = update.email
		    if update.phone:
		    	venue.phone = update.phone
		    if update.facebook:
		    	venue.facebook = update.facebook
		    if update.messenger:
		    	venue.messenger = update.messenger
		    if update.twitter:
		    	venue.twitter = update.twitter
		    if update.instagram:
		    	venue.instagram = update.instagram
		    if update.spotify:
		    	venue.spotify = update.spotify
		    if update.soundcloud:
		    	venue.soundcloud = update.soundcloud
		    if update.bandcamp:
		    	venue.bandcamp = update.bandcamp
		    if update.youtube:
		    	venue.youtube = update.youtube
		    if update.website:
		    	venue.website = update.website

		    update.is_applied = True
		    venue.save()
		    update.save()

update_venue.short_description = u"Apply Update(s)"


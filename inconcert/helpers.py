
from decimal import Decimal


#Convert strings ("1.2K", "14", "3.9M") to integer values.
def count_likes_from_text(text):
	if isinstance(text, int):
		return text
	elif text.rfind('K') > -1:
		return int(Decimal(text[:-1]) * Decimal(1000))
	elif text.rfind('M') > -1:
		return int(Decimal(text[:-1]) * Decimal(1000000))
	elif text.rfind('B') > -1:
		return int(Decimal(text[:-1]) * Decimal(1000000000))
	else:
		try:
			return int(text)
		except ValueError:
			return None
"""
#Determine venue genres by aggregating all performance genres.
def update_venue_genres(venue):
	genres = []
	for event in venue.events.prefetch_related('artists__genres').values('artists__genres')
		genres.concat(event['artists__genres'])

	#todo: test that this bs works
	venue.add(genres)
	venue.genres = venue.genres.distinct()
	venue.genres.save()
"""

#Get location coordinates from a location string.
def get_coordinates(location_string):
	
	return None


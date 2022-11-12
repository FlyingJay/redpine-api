from core import models
from venue_listings import models as v_models


def get_by_core_id(model,core_obj):
	core_id = core_obj
	if core_obj:
		core_id=core_obj.id

	data = None
	try:
		data = model.objects.filter(core_id=core_id).first()
	except:
		pass

	return data

def already_created(model,core_obj):
	core_id = core_obj
	if core_obj:
		core_id=core_obj.id

	if model.objects.filter(core_id=core_id).exists():
		return True
	
	return False


def initialize_locations():
	canada_id = 0
	
	#Add Canada
	canada = v_models.Country.objects.create(
		id=canada_id, 
		core_id=canada_id, 
		name='Canada'
		)

	#Add Provinces / Territories
	v_models.Province.objects.create(
		id=1, 
		core_id=1, 
		name='Ontario',
		country=canada
		)
	v_models.Province.objects.create(
		id=2, 
		core_id=2, 
		name='Quebec',
		country=canada
		)
	v_models.Province.objects.create(
		id=10, 
		core_id=10, 
		name='British Columbia',
		country=canada
		)
	v_models.Province.objects.create(
		id=9, 
		core_id=9, 
		name='Alberta',
		country=canada
		)
	v_models.Province.objects.create(
		id=8, 
		core_id=8, 
		name='Saskatchewan',
		country=canada
		)
	v_models.Province.objects.create(
		id=7, 
		core_id=7, 
		name='Manitoba',
		country=canada
		)
	v_models.Province.objects.create(
		id=6, 
		core_id=6, 
		name='New Brunswick',
		country=canada
		)
	v_models.Province.objects.create(
		id=5, 
		core_id=5, 
		name='Nova Scotia',
		country=canada
		)
	v_models.Province.objects.create(
		id=4, 
		core_id=4, 
		name='Prince Edward Island',
		country=canada
		)
	v_models.Province.objects.create(
		id=3, 
		core_id=3, 
		name='Newfoundland and Labrador',
		country=canada
		)
	v_models.Province.objects.create(
		id=11, 
		core_id=11, 
		name='Yukon',
		country=canada
		)
	v_models.Province.objects.create(
		id=12, 
		core_id=12, 
		name='Northwest Territories',
		country=canada
		)
	v_models.Province.objects.create(
		id=13, 
		core_id=13, 
		name='Nunavut',
		country=canada
		)

def update_from_core():
	for country in models.Country.objects.all():
		if not already_created(v_models.Country, country):
			v_models.Country.objects.create(
				core_id=country.id, 
				name=country.name
				)
		else:
			v_models.Country.objects.filter(core_id=country.id).update(
				name=country.name
				)


	for province in models.Province.objects.all().select_related('country'):
		if not already_created(v_models.Province, province):
			v_models.Province.objects.create(
				core_id=province.id, 
				name=province.name, 
				country=get_by_core_id(v_models.Country, province.country)
				)
		else:
			v_models.Province.objects.filter(core_id=province.id).update(
				name=province.name, 
				country=get_by_core_id(v_models.Country, province.country)
				)

	for city in models.City.objects.all().select_related('province__country'):
		if not already_created(v_models.City, city):
			v_models.City.objects.create(
				core_id=city.id,
				name=city.name,
				province=get_by_core_id(v_models.Province, city.province)
				)		
		else:
			v_models.City.objects.filter(core_id=city.id).update(
				name=city.name,
				province=get_by_core_id(v_models.Province, city.province)
				)

	for genre in models.Genre.objects.all():
		if not already_created(v_models.Genre, genre):
			v_models.Genre.objects.create(
				core_id=genre.id,
				name=genre.name
				)		
		else:
			v_models.Genre.objects.filter(core_id=genre.id).update(
				name=genre.name
				)

	for venue in models.Venue.objects.all():
		if not already_created(v_models.Venue, venue):
			v_models.Venue.objects.create(
				core_id=venue.id,

	            title=venue.title,
	            description=venue.description,
	            capacity=venue.capacity,
	            address=venue.address,
	            website=venue.website,
	            facebook=venue.facebook,
	            twitter=venue.twitter,
	            soundcloud=venue.soundcloud,
	            instagram=venue.instagram,
	            youtube=venue.youtube,
	            city=get_by_core_id(v_models.City, venue.city),
	            location=venue.location,
	            postal_code=venue.postal_code,
	            primary_genre=get_by_core_id(v_models.Genre, venue.primary_genre),
	            secondary_genre=get_by_core_id(v_models.Genre, venue.secondary_genre),

	            has_wifi=venue.has_wifi,
	            is_accessible_by_transit=venue.is_accessible_by_transit,
	            has_atm_nearby=venue.has_atm_nearby,
	            has_free_parking_nearby=venue.has_free_parking_nearby,
	            has_paid_parking_nearby=venue.has_paid_parking_nearby,
	            is_wheelchair_friendly=venue.is_wheelchair_friendly,
	            allows_smoking=venue.allows_smoking,
	            allows_all_ages=venue.allows_all_ages,
	            has_stage=venue.has_stage,
	            has_microphones=venue.has_microphones,
	            has_drum_kit=venue.has_drum_kit,
	            has_piano=venue.has_piano,
	            has_wires_and_cables=venue.has_wires_and_cables,
	            has_front_load_in=venue.has_front_load_in,
	            has_back_load_in=venue.has_back_load_in,
	            has_soundtech=venue.has_soundtech,
	            has_lighting=venue.has_lighting,
	            has_drink_tickets=venue.has_drink_tickets,
	            has_meal_vouchers=venue.has_meal_vouchers,
	            has_merch_space=venue.has_merch_space,
	            has_cash_box=venue.has_cash_box,
	            has_float_cash=venue.has_float_cash
				)
		else:
			v_models.Venue.objects.filter(core_id=venue.id).update(
	            title=venue.title,
	            description=venue.description,
	            capacity=venue.capacity,
	            address=venue.address,
	            website=venue.website,
	            facebook=venue.facebook,
	            twitter=venue.twitter,
	            soundcloud=venue.soundcloud,
	            instagram=venue.instagram,
	            youtube=venue.youtube,
	            city=get_by_core_id(v_models.City, venue.city),
	            location=venue.location,
	            postal_code=venue.postal_code,
	            primary_genre=get_by_core_id(v_models.Genre, venue.primary_genre),
	            secondary_genre=get_by_core_id(v_models.Genre, venue.secondary_genre),

	            has_wifi=venue.has_wifi,
	            is_accessible_by_transit=venue.is_accessible_by_transit,
	            has_atm_nearby=venue.has_atm_nearby,
	            has_free_parking_nearby=venue.has_free_parking_nearby,
	            has_paid_parking_nearby=venue.has_paid_parking_nearby,
	            is_wheelchair_friendly=venue.is_wheelchair_friendly,
	            allows_smoking=venue.allows_smoking,
	            allows_all_ages=venue.allows_all_ages,
	            has_stage=venue.has_stage,
	            has_microphones=venue.has_microphones,
	            has_drum_kit=venue.has_drum_kit,
	            has_piano=venue.has_piano,
	            has_wires_and_cables=venue.has_wires_and_cables,
	            has_front_load_in=venue.has_front_load_in,
	            has_back_load_in=venue.has_back_load_in,
	            has_soundtech=venue.has_soundtech,
	            has_lighting=venue.has_lighting,
	            has_drink_tickets=venue.has_drink_tickets,
	            has_meal_vouchers=venue.has_meal_vouchers,
	            has_merch_space=venue.has_merch_space,
	            has_cash_box=venue.has_cash_box,
	            has_float_cash=venue.has_float_cash
				)
	
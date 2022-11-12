from core import models
from analysis import models as a_models
from datetime import datetime, timedelta
import decimal

DEBUG = True
def error(e):
	if DEBUG: 
		print(e)
	else: 
		pass

# Clear /analysis data
def clear_analysis():
	a_models.Timeslot_Fact.objects.all().delete()
	a_models.Campaign_Fact.objects.all().delete()
	a_models.Pledge_Fact.objects.all().delete()
	a_models.Band.objects.all().delete()
	a_models.Timeslot.objects.all().delete()
	a_models.Venue.objects.all().delete()
	a_models.Campaign.objects.all().delete()
	a_models.City.objects.all().delete()
	a_models.Province.objects.all().delete()
	a_models.Country.objects.all().delete()

# Create default /analysis model entries to be used for unclean data
def initialize_clean_entries():
	unknown_country = a_models.Country.objects.create(name='unknown')
	unknown_province = a_models.Province.objects.create(name='unknown')
	a_models.City.objects.create(name='unknown',
		province=unknown_province,
		country=unknown_country,
		core_id=None
		)

# Takes a city from /core and finds the equivalent entry in /analysis.
def get_city(c):
	try:
		a_city = a_models.City.objects.get(core_id=c.id)	
	except:
		a_city = a_models.City.objects.get(core_id=None)

	if a_city:
		return a_city
	else:
		return None

# Takes a venue from /core and finds the equivalent entry in /analysis.
def get_venue(v):
	a_venue = a_models.Venue.objects.get(core_id=v.id)	

	if a_venue:
		return a_venue
	else:
		return None

# Takes a timeslot from /core and finds the equivalent entry in /analysis.
def get_timeslot(t):
	a_timeslot = a_models.Timeslot.objects.get(core_id=t.id)	

	if a_timeslot:
		return a_timeslot
	else:
		return None

# Takes a campaign from /core and finds the equivalent entry in /analysis.
def get_campaign(c):
	a_campaign = a_models.Campaign.objects.get(core_id=c.id)	

	if a_campaign:
		return a_campaign
	else:
		return None

# Load /core data into /analysis
def generate_analysis():
	clear_analysis()
	initialize_clean_entries()

	# LOCATION DIMENSION
	all_countries = models.Country.objects.all()

	for country in all_countries:
		new_country = a_models.Country.objects.create(name=country.name)

		for province in country.provinces.all():
			new_province = a_models.Province.objects.create(name=province.name)

			for city in province.cities.all():
				a_models.City.objects.create(
					name=city.name,
					province=new_province,
					country=new_country,
					core_id=city.id
					)

	# VENUE DIMENSION
	all_venues = models.Venue.objects.all()
	for v in all_venues:
		a_models.Venue.objects.create(
			title=v.title,
			capacity=v.capacity,
			address=v.address,
			city=get_city(v.city),
			postal_code=v.postal_code,
			location=v.location,
			currency=v.currency,
			timezone=v.timezone,
			core_id=v.id
			)

	all_timeslots = models.Timeslot.objects.all()
	for t in all_timeslots:
		try:
			a_venue = a_models.Venue.objects.filter(
				title=t.venue.title,
				city=get_city(t.venue.city)
			).first()

			# TIMESLOT DIMENSION
			new_timeslot = a_models.Timeslot.objects.create(
				venue=a_venue,
				asking_price=t.asking_price,
				min_headcount=t.min_headcount,
				start_time=t.start_time,
				end_time=t.end_time,
				booked=t.booked,
				created_date=t.created_date,
				core_id=t.id
			)

			# TIMESLOT FACT
			a_models.Timeslot_Fact.objects.create(
				timeslot=new_timeslot,
				venue=a_venue,
				asking_price=t.asking_price,
				min_headcount=t.min_headcount,
				created_date=t.created_date,
				campaign=None,
				campaign_success=None,
				is_successful=None
			)
		except Exception as e: 
			error(e)
		
	# CAMPAIGN DIMENSION
	all_campaigns = models.Campaign.objects.all()
	for c in all_campaigns:
		try: 
			a_models.Campaign.objects.create(
				title=c.title,
				goal_amount=c.goal_amount,
				goal_count=c.goal_count,
				funding_type=c.funding_type,
				seating_type=c.seating_type,
				min_ticket_price=c.min_ticket_price,
				funding_start=c.funding_start,
				funding_end=c.funding_end,
				is_open=c.is_open,
				is_venue_approved=c.is_venue_approved,
				is_successful=c.is_successful,
				created_by=c.created_by,
				created_date=c.created_date,
				core_id=c.id
			)
		except Exception as e: 
			error(e)

	# BAND DIMENSION 
	all_bands = models.Band.objects.all()
	all_campaign_bands = models.CampaignBand.objects.exclude(campaign__funding_start=None)

	for b in all_bands:
		try:
			new_band = a_models.Band.objects.create(
				name=b.name,
				created_by=b.creator,
				picture=b.picture,
				core_id=b.id
			)

			# CAMPAIGN FACT
			band_campaigns = all_campaign_bands.filter(band=b).prefetch_related('pledges__purchases__item')

			for c in band_campaigns:
				a_campaign = get_campaign(c.campaign)
				a_timeslot = get_timeslot(c.campaign.timeslot)
				a_venue = get_venue(c.campaign.timeslot.venue)

				campaign_end = a_campaign.success_date

				# Set alpha campaigns to a duration of 2 weeks
				if(campaign_end == None and a_campaign.is_successful):
					campaign_end = a_campaign.funding_start + timedelta(days=14)

				# Default alpha listings to being created 2 weeks before the campaign.
				timeslot_listing = a_timeslot.created_date
				if(a_campaign.is_successful and timeslot_listing > a_campaign.funding_start):
					timeslot_listing = a_campaign.funding_start - timedelta(days=14)

				a_models.Campaign_Fact.objects.create(
					campaign=a_campaign,
					timeslot=a_timeslot,
					venue=a_venue,
					band=new_band,
					timeslot_listed=timeslot_listing,
					campaign_start=a_campaign.funding_start,
					campaign_success=campaign_end,
					is_successful=a_campaign.is_successful,
					goal_count=a_campaign.goal_count,
					gross_sales=c.campaign.total_earned()
				)

				timeslot = a_models.Timeslot_Fact.objects.get(timeslot=a_timeslot)
				timeslot.campaign = a_campaign
				timeslot.campaign_success = campaign_end
				timeslot.is_successful = a_campaign.is_successful
				timeslot.created_date = timeslot_listing

				timeslot.save()

				# PLEDGE FACT
				campaign_bands = all_campaign_bands.filter(campaign=c.campaign)
				band_count = campaign_bands.count()

				for p in c.campaign.pledges.prefetch_related('bands'):
					pledge_band_count = p.bands.count()

					# Default to "Going to see: Everyone" when band data is missing.
					if(pledge_band_count == 0):
						pledge_band_count = band_count

					"""
					Amount earned by each act is calculated by the "going to see" feature on checkout.
					If the organizaer selected the ALL_TO_ORGANIZER payout option then they will be reciving
					more cash-in-hand than these calculations suggest.
					"""
					total = decimal.Decimal(0.00)
					for purchase in p.purchases.select_related():
						total += (purchase.item.price/pledge_band_count)*purchase.quantity

					pledge_fact = a_models.Pledge_Fact.objects.create(
						campaign=a_campaign,
						timeslot=a_timeslot,
						venue=a_venue,
						band=new_band,
						user=p.user,
						total=total,
						count=p.count,
						is_processed=p.is_processed,
						is_cancelled=p.is_cancelled,
						created_date=p.created_date
					)
		except Exception as e: 
			error(e)
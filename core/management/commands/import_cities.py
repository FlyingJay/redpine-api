import os
from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError
from core.models import Country, Province, City, Venue
from django.contrib.gis.geos import Point
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.contrib.gis.geos import GEOSGeometry


class Command(createsuperuser.Command):
    help = 'Add cites'

    def handle(self, *args, **options):
        with open('/Users/connorbode/Workspaces/yelp-scraper/cache.json') as f:
            import json
            cities = json.loads(f.read())

        with open('/Users/connorbode/Workspaces/yelp-scraper/venues-master.csv') as f:
            data = f.read()

        rows = data.split('\n')
        headers = rows[0].split(',')
        rows = rows[1:]

        US = Country.objects.get(name = 'United States')

        try:
            MI = Province.objects.get(name = 'Michigan')
        except:
            MI = Province.objects.create(name = 'Michigan', country = US)

        try:
            NY = Province.objects.get(name = 'New York')
        except:
            NY = Province.objects.create(name = 'New York', country = US)

        try:
            WA = Province.objects.get(name = 'Washington')
        except:
            WA = Province.objects.create(name = 'Washington', country = US)

        try:
            OH = Province.objects.get(name = 'Ohio')
        except:
            OH = Province.objects.create(name = 'Ohio', country = US)


        states = {
            'AB': Province.objects.get(name = 'Alberta'),
            'BC': Province.objects.get(name = 'British Columbia'), 
            'QC': Province.objects.get(name = u'Québec'),
            'ON': Province.objects.get(name = 'Ontario'),
            'NS': Province.objects.get(name = 'Nova Scotia'),
            'NB': Province.objects.get(name = 'New Brunswick'),
            'NL': Province.objects.get(name = 'Newfoundland and Labrador'),
            'MB': Province.objects.get(name = 'Manitoba'),
            'PE': Province.objects.get(name = 'Prince Edward Island'),
            'SK': Province.objects.get(name = 'Saskatchewan'),
            'MI': MI,
            'NY': NY,
            'OH': OH,
            'WA': WA
        }

        provinces = []

        for row in rows[:1]:
            cols = row.split(',')
            name = cols[0]
            city = cols[3]

            # if name == u'La Boite a Bleuets': 
            #     __import__('ipdb').set_trace()

            try:
                venue = cities[city][name]

            except:
                try:
                    venue = cities[''][name]

                except:
                    venue = None
                    print('couldnt find for {}'.format(name))

            if venue is not None:
                try:
                    if venue.get('country') == 'CA':
                        country = Country.objects.get(name = 'Canada')

                    elif venue.get('country') == 'US':
                        country = Country.objects.get(name = 'United States')

                    else:
                        print(venue.get('country'))

                    province = states[venue.get('state')]

                    try:
                        city = City.objects.get(name = venue.get('city'))
                    except:
                        city = City.objects.create(name = venue.get('city'), province = province)

                    from io import BytesIO
                    from urllib.request import urlopen

                    from django.core.files import File
                    import secrets


                    # url, filename, model_instance assumed to be provided
                    response = urlopen(venue.get('image'))
                    io = BytesIO(response.read())
                    f = File(io)

                    vvvv = Venue.objects.create(
                        title = venue.get('name'),
                        address = venue.get('address 1'),
                        city = city,
                        postal_code = venue.get('post code'),
                        location = GEOSGeometry('POINT({} {})'.format(venue.get('longitude'), venue.get('latitude')), srid=4326),
                        picture = File(io),
                        currency = Venue.CAD if venue.get('country') == 'CA' else Venue.USD
                    )

                    vvvv.picture.save(secrets.token_hex(16), File(io))
                    print(vvvv.id)
                except Exception as e:
                    print(e)
                    print('failed for {}'.format(venue.get('name')))

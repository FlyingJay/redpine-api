import csv
from django.core.management import BaseCommand
from inconcert.models import ArtistImport, VenueImport, EventImport
from core.settings import BASE_DIR


class Command(BaseCommand):
    help = 'Load a csv file into the database'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)
        parser.add_argument('--model', type=str)

    def handle(self, *args, **kwargs):
        path = BASE_DIR + kwargs['path']
        model = kwargs['model']

        print(path)

        with open(path, 'rt') as f:
            reader = csv.reader(f, dialect='excel')
            for row in reader:
                if 'inconcert' in path:
                    if model == 'artist':
                        artist = ArtistImport.objects.create(
                            name = row[0],
                            page_types = row[1],
                            likes = row[2],
                            page_created = row[3],
                            facebook = row[4],
                            instagram = row[5],
                            twitter = row[6],
                            spotify = row[7],
                            soundcloud = row[8],
                            bandcamp = row[9],
                            youtube = row[10],
                            email = row[11],
                            website = row[12],
                            phone = row[13],
                            image = row[14],
                            address = row[15],
                            story = row[16],
                            about = row[17],
                            price_range = row[18],
                            artists_we_also_like = row[19],
                            general_information = row[20],
                            public_transit = row[21],
                            founding_date = row[22],
                            impressum = row[23],
                            attire = row[24],
                            culinary_team = row[25],
                            mission = row[26],
                            company_overview = row[27],
                            products = row[28],
                            awards = row[29],
                            band_interests = row[30],
                            personal_interests = row[31],
                            general_manager = row[32],
                            hometown = row[33],
                            press_contact = row[34],
                            booking_agent = row[35],
                            affiliation = row[36],
                            personal_information = row[37],
                            genre = row[38],
                            accessibility_info = row[39],
                            biography = row[39],
                            gender = row[40],
                            network = row[41],
                            misc = row[42],
                            influences = row[43],
                            current_location = row[44],
                            record_label = row[45],
                            band_members = row[46],
                            members = row[47],
                            release_date = row[48],
                            season = row[49],
                            plot_outline = row[50],
                            schedule = row[51],
                            directed_by = row[52],
                            written_by = row[53],
                            starring = row[54]
                        )
                    if model == 'venue':
                        venue = VenueImport.objects.create(
                            name = row[0],
                            page_types = row[1],
                            likes = row[2],
                            page_created = row[3],
                            facebook = row[4],
                            instagram = row[5],
                            twitter = row[6],
                            spotify = row[7],
                            soundcloud = row[8],
                            bandcamp = row[9],
                            youtube = row[10],
                            email = row[11],
                            website = row[12],
                            phone = row[13],
                            image = row[14],
                            address = row[15],
                            story = row[16],
                            about = row[17],
                            price_range = row[18],
                            artists_we_also_like = row[19],
                            general_information = row[20],
                            public_transit = row[21],
                            founding_date = row[22],
                            impressum = row[23],
                            attire = row[24],
                            culinary_team = row[25],
                            mission = row[26],
                            company_overview = row[27],
                            products = row[28],
                            awards = row[29],
                            band_interests = row[30],
                            personal_interests = row[31],
                            general_manager = row[32],
                            hometown = row[33],
                            press_contact = row[34],
                            booking_agent = row[35],
                            affiliation = row[36],
                            personal_information = row[37],
                            genre = row[38],
                            accessibility_info = row[39],
                            biography = row[39],
                            gender = row[40],
                            network = row[41],
                            misc = row[42],
                            influences = row[43],
                            current_location = row[44],
                            record_label = row[45],
                            band_members = row[46],
                            members = row[47],
                            release_date = row[48],
                            season = row[49],
                            plot_outline = row[50],
                            schedule = row[51],
                            directed_by = row[52],
                            written_by = row[53],
                            starring = row[54]
                        )
                    if model == 'event':
                        question = EventImport.objects.create(
                            name = row[0],
                            profile_link = row[1],
                            event_link = row[2]
                        )
            print("done.")
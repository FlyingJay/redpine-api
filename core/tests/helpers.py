from django.core.files.uploadedfile import SimpleUploadedFile
from core.models import *
from django.contrib.gis.geos import Point
from datetime import datetime, timedelta
from faker import Factory
from decimal import Decimal
from square import models as square_models
from background_task.models import Task
from django.forms.models import model_to_dict
import random
import shutil
import json
import os

fake = Factory.create()
mock_image = SimpleUploadedFile(name='test_image.jpg', content=open('core/tests/fixtures/pwned.jpg', 'rb').read(), content_type='image/jpeg')
mock_image_raw = open('core/tests/fixtures/mock_image_raw').read()

unique_faked_vals = []

def unique_faked(func):
    """ sometimes we need faker values to be unique (e.g. if we're faking username)... this func prevents duplicates """
    while True:
        val = func()
        try:
            unique_faked_vals.index(val)
            pass

        except:
            break

    return val


def fake_username():
    return unique_faked(lambda: fake.profile().get('username'))


def fake_email():
    return unique_faked(lambda: fake.email())


def build_user(email = None, username = None, password = None):
    if email is None:
        email = fake_email()

    if username is None:
        username = fake_username()

    if password is None:
        password = 'password'

    return User.objects.create_user(email=email, username=username, password=password)


def build_city():
    country = Country.objects.create(name=fake.country())
    province = Province.objects.create(name=fake.state(), country=country)
    city = City.objects.create(name=fake.city(), province=province)
    return city


def build_venue(name = None):
    """ Helper for building a test venue """
    city = build_city()
    manager = User.objects.create_user(username=fake_username(), password='manager')
    Profile.objects.create(user=manager, picture=mock_image)

    venue = Venue.objects.create(
        title='venue' if name is None else name,
        description='test',
        city=city,
        capacity=100,
        address='test',
        picture=mock_image,
        location=Point(0, 0, srid=4326),
        website='',
        facebook='',
        twitter='',
        soundcloud='',
        instagram='',
        youtube='',
    )
    VenueManager.objects.create(venue=venue, manager=manager)
    venue.save()

    return (manager, venue,)


def build_timeslot(venue, **kwargs):
    args = dict(
        venue=venue,
        asking_price='20',
        min_headcount=20,
        start_time=datetime.now() + timedelta(days=1),
        end_time=datetime.now() + timedelta(days=1, hours=1),
        booked=False
    )
    args.update(kwargs)
    return Timeslot.objects.create(**args)


def build_band(num = None, band_member = None):
    if num is None:
        num = random.randint(1, 6) 

    user = User.objects.create_user(
        username=fake_username(), 
        password='password'
    )
    Profile.objects.create(user=user, picture=mock_image)

    band = Band.objects.create(
        name=fake.company(),
        short_bio=fake.catch_phrase(),
        is_redpine=True,
        is_available=True,
        owner=band_member if band_member else user
    )
    return band


def build_campaign(bands, timeslot, user = None,):
    if user is None:
        user = build_user()
        Profile.objects.create(user=user, picture=mock_image)
    
    campaign = Campaign.objects.create(
        title=fake.company(),
        description=fake.catch_phrase(),
        goal_amount=Decimal(str(fake.random_int())),
        funding_type=Campaign.GOAL_AMOUNT,
        seating_type=Campaign.FIRST_COME_FIRST_SEATING,
        min_ticket_price=Decimal('10'),
        funding_start=datetime.now(),
        funding_end=datetime.now() + timedelta(days=1, hours=1),
        hashtag='{}'.format(fake.bs().replace(' ', '-')),
        picture=mock_image,
        is_venue_approved=True,
        timeslot=timeslot,
        created_by=user
    )

    for i, band in enumerate(bands):
        CampaignBand.objects.create(
            band=band,
            is_headliner=(True if i == 0 else False),
            is_accepted=True,
            campaign=campaign,
            start_time=None
        )

    return campaign


def build_purchase_item(campaign, price = None, quantity = None, is_ticket = True, name = None, description = None):
    if name is None:
        name = "Some product"

    if description is None:
        description = "Boring description."

    if price is None:
        price = 10.00

    if quantity is None:
        quantity = random.randint(1, 100)

    purchaseItem = PurchaseItem.objects.create(
        name=name,
        description=description,
        price=price,
        quantity=quantity,
        campaign=campaign,
        is_ticket=is_ticket
    )

    return purchaseItem


def build_transaction(items, quantities, user = None, campaign = None, bands = None, total = None, count = None, customer = None):
    
    computed_total = 0
    computed_count = 0
    item_references = []

    for i, item in enumerate(items):
        itemDetails = PurchaseItem.objects.get(pk=item)

        computed_total += itemDetails.price * Decimal(quantities[i])

        if itemDetails.is_ticket:
            computed_count += quantities[i]

        item_references.append(itemDetails)

    if count is None:
        count = computed_count

    if total is None:
        total = computed_total

    if customer is None:
        if user and user.email:
            customer = square_models.Customer.objects.create(square_id='', email=user.email)
        else:
            customer = square_models.Customer.objects.create(square_id='', email=fake_email())

    if user is None:
        user = build_user()
        Profile.objects.create(user=user, picture=mock_image)

    if bands is None:
        bands = []

    redpine_fee = round(Decimal(total)*Decimal('0.12'),2)

    transaction = Pledge.objects.create( 
        total=total,
        redpine_fee=redpine_fee,
        count=count,
        square_customer=customer,
        user=user,
        campaign=campaign
    )

    for i, quantity in enumerate(quantities):
        PledgePurchase.objects.create(
            transaction=transaction,
            item=item_references[i],
            quantity=quantity,
        )

    transaction.bands = bands
    transaction.save()
    return transaction


def build_ticket(transaction,details):
    return Ticket.objects.create(pledge=transaction,details=details)


def build_booking_request(user=None,venue=None,followed_up=False):
    if user is None:
        user = build_user()
        Profile.objects.create(user=user, picture=mock_image)
    if venue is None:
        manager, venue = build_venue()
    return BookingRequest.objects.create(user=user,venue=venue,followed_up=followed_up)

def build_app_cash_transaction(
    processed_by=None,
    total=None,
    redpine_fee=None,
    count=None,
    campaign=None,
    bands=None,
    payouts_processed=None,
    processed_buy=None):
    if total is None: total = Decimal('0')
    if redpine_fee is None: redpine_fee = Decimal('0')
    if count is None: count = 0
    if campaign is None: raise Exception('pass a campaign to the builder..')
    if bands is None: bands = []
    if payouts_processed is None: payouts_processed = False
    if processed_by is None: processed_by = build_user()
    transaction = AppCashTransaction.objects.create(
        total=total,
        redpine_fee=redpine_fee,
        count=count,
        campaign=campaign,
        payouts_processed=payouts_processed,
        processed_by=processed_by
    )
    transaction.bands = bands
    transaction.save()
    return transaction

def build_app_card_transaction(
    processed_by=None,
    total=None,
    redpine_fee=None,
    count=None,
    campaign=None,
    bands=None,
    payouts_processed=None,
    processed_buy=None):
    if total is None: total = Decimal('0')
    if redpine_fee is None: redpine_fee = Decimal('0')
    if count is None: count = 0
    if campaign is None: raise Exception('pass a campaign to the builder..')
    if bands is None: bands = []
    if payouts_processed is None: payouts_processed = False
    if processed_by is None: processed_by = build_user()
    transaction = AppCardTransaction.objects.create(
        total=total,
        redpine_fee=redpine_fee,
        count=count,
        campaign=campaign,
        payouts_processed=payouts_processed,
        processed_by=processed_by
    )
    transaction.bands = bands
    transaction.save()
    return transaction

def clear_media():
    """ If you're upload image fixtures during the tests, you'll want to clear the tmp_media folder afterwards """
    if os.path.exists('tmp_media'):
        shutil.rmtree('tmp_media')


def verify_task(task_name, params):
    """ verifies that a task has been created with the provided name & params """
    task_params = json.dumps(params)
    return Task.objects.get(task_name=task_name, task_params=task_params)


def assert_keys(dictionary, keys):
    """ verifies that all of the keys exist in the dictionary
    keys should be a list of dictionary keys, separated by `.`
    """

    for key in keys:
        ptr = dictionary
        split = key.split('.')
        path = split[0]

        for s in split:
            if type(ptr).__name__ != 'dict':
                raise Exception('path `{}` is not a dictionary: \n {}'.format(path, json.dumps(dictionary)))

            elif s not in ptr:
                raise Exception('key `{}` not found in dictionary at path {}'.format(s, path))

            else:
                ptr = ptr.get(s)
                path += '.' + s
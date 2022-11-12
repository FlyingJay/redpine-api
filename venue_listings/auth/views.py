from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.db.models import Q
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from core.serializers import UserPrivilegedSerializer
import square
from square.exceptions import ChargeFailureException
from datetime import *
from venue_listings.exceptions import *
from .serializers import *

def check_user(username, email):
    existing_user = None

    try:
        existing_user = User.objects.get(email__iexact=email)
    except:
        pass

    if existing_user is not None:
        raise BadRequest('Email already exists')

    existing_user = None

    try:
        existing_user = User.objects.get(username__iexact=username)
    except:
        pass

    if existing_user is not None:
        raise BadRequest('Username already exists')


class PasswordRegistrationView(generics.CreateAPIView):
    def create(self, request):
        serializer = PasswordRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        check_user(data.get('username'), data.get('email'))

        user = User.objects.create_user(
            username=data.get('username'),
            password=data.get('password'),
            email=data.get('email'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            is_staff=True
        )

        try:
            customer = square.models.Customer.objects.create_customer(
                email=data.get('email'), 
                token=request.data.get('token')
                )
        except:
            raise BadRequest()

        try: 
            metadata = {
                'user': user.id,
                'details': 'Venues: {0} {1}'.format(data.get('first_name'), data.get('last_name'))
            }

            customer.charge(
                amount=4200, 
                currency='CAD',
                metadata=metadata
            )
        except:
            raise ChargeFailureException()

        listings_user_group = Group.objects.get(name='Venue Listings Customer') 
        listings_user_group.user_set.add(user)

        return Response(UserPrivilegedSerializer(user).data, status=200)
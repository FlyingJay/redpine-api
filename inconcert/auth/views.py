from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from datetime import *
from inconcert.models import *
from inconcert.serializers import UserPrivilegedSerializer
from .serializers import *
import secrets


class PasswordAuthView(generics.CreateAPIView):
    def create(self, request):
        serializer = PasswordAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.data.get('username')
        password = serializer.data.get('password')

        try:
            user = User.objects.exclude(inconcert_profile=None).get(email__iexact=email)
        except:
            raise ValidationError()

        if not user.check_password(password):
            raise ValidationError()

        try:
            token = Token.objects.get(user=user)
        except:
            token = Token.objects.create(user=user)

        User.objects.filter(id=user.id).update(last_login=datetime.now())

        return Response({'token': token.key, 'user': user.id})


class PasswordRegistrationView(generics.CreateAPIView):
    def create(self, request):
        serializer = PasswordRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        existing_user = None
        try:
            existing_user = User.objects.exclude(inconcert_profile=None).filter(email__iexact=data.get('email')).first()
        except:
            pass

        if existing_user is not None:
            raise ValidationError({'detail':'Email already exists'})

        user = User.objects.exclude(inconcert_profile=None).filter(email__iexact=data.get('email')).first()
        if user is None:
            referrer = data.get('referrer', None)
            if referrer:
                referrer = User.objects.exclude(inconcert_profile=None).filter(id=referrer).first()

                if referrer is None:
                    raise ValidationError({'detail':'Refering user not found'})

                referrer_profile = referrer.inconcert_profile
                if referrer_profile.eligible_for_lifetime_membership and referrer_profile.referral_count() > 9:
                    referrer_profile.has_lifetime_membership = True
                    referrer_profile.save()
                    #TODO: Send an email to let them know they've recieved lifetime membership                

                #else:
                #    referrer.inconcert_profile.premium_months += 1
                #referrer.inconcert_profile.save()

            user = User.objects.create_user(
                username="inconcert_{0}".format(data.get('email')),
                password=data.get('password') if data.get('password') else secrets.token_hex(16),
                email=data.get('email')
            )

            Profile.objects.create(
                user=user,
                referrer=referrer,
                premium_months=1
            )

        user.inconcert_profile.save()

        data = UserPrivilegedSerializer(user).data
        return Response(data, status=200)


class LogoutView(generics.CreateAPIView):
    serializer_class = LogoutSerializer

    def create(self, request):
        try:
            request.auth.delete()
        except:
            pass
        
        return Response(data={}, status=200)
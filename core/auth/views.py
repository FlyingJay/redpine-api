from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from facebook import FacebookClient
from maas.models import Mail
from core.auth import exceptions
from core import helpers
from datetime import *
from core.models import *
from core.serializers import UserPrivilegedSerializer, UserGhostSerializer
from core.exceptions import *
from .serializers import *
import secrets


def reset_password(user):
    profile = user.profile
    profile.generate_password_reset_token()
    profile.save()

    helpers.create_mail_from_template(
        recipient=user.email,
        subject='Reset Password',
        template='mail/reset_password.html',
        context={
            'url': profile.get_password_reset_url()
        }
    )


class ForgotPasswordView(generics.CreateAPIView):
    def create(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email=serializer.data.get('email'))
            reset_password(user)

        except ObjectDoesNotExist as e:
            pass

        return Response({})


class FacebookAuthView(generics.CreateAPIView):
    def create(self, request):
        serializer = FacebookAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.data.get('code')
        redirect_uri = serializer.data.get('redirect_uri')
        client = FacebookClient(settings.FACEBOOK_APP_ID, settings.FACEBOOK_APP_SECRET)

        try:
            client.confirm(redirect_uri, code)
            email = client.get_email()
        except Exception as e:
            raise BadRequest('Facebook authentication failed')

        try:
            user = User.objects.get(email__iexact=email)
        except:
            raise BadRequest('User with specified email not found')

        token = Token.objects.get_or_create(user=user)[0]
        return Response({'token': token.key, 'user': user.id})


class PasswordAuthView(generics.CreateAPIView):
    def create(self, request):
        serializer = PasswordAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data.get('username')
        password = serializer.data.get('password')

        try:
            user = User.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
        except:
            raise BadRequest()

        #try/catch because venue listing customers have no profile
        try:
            is_alpha_user = user.profile.is_alpha_user
        except:
            is_alpha_user = False

        if is_alpha_user:
            reset_password(user)
            # IM A TEAPOT
            return Response(data={'is_alpha_user': True}, status=418)

        if not user.check_password(password):
            raise BadRequest()

        try:
            token = Token.objects.get(user=user)
        except:
            token = Token.objects.create(user=user)

        User.objects.filter(id=user.id).update(last_login=datetime.now())

        return Response({'token': token.key, 'user': user.id})


def check_user(username, email):
    existing_user = None

    try:
        existing_user = User.objects.filter(email__iexact=email).exclude(profile__is_ghost=True).first()
    except:
        pass

    if existing_user is not None:
        raise BadRequest('Email already exists')

    existing_user = None

    try:
        existing_user = User.objects.filter(username__iexact=username).exclude(profile__is_ghost=True).first()
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
        
        has_password = data.get('password')
        random_password = secrets.token_hex(16)

        #Check for existing ghost user first
        user = User.objects.filter(Q(username__iexact=data.get('email')) & Q(email__iexact=data.get('email')), profile__is_ghost=True).first()
        if user is None:
            user = User.objects.create_user(
                username=data.get('username'),
                password=data.get('password') if has_password else random_password,
                email=data.get('email'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name')
            )
            """
            if data.get('referrer', None):
                referrer = User.objects.get(pk=data.get('referrer', None))
                Reward.objects.create(
                    recipient=referrer,
                    subject=user,
                    amount=5.00,
                    reward_type=Reward.FIRST_SHOW,
                    is_completed=False
                )
                Reward.objects.create(
                    recipient=user,
                    subject=user,
                    amount=5.00,
                    reward_type=Reward.FIRST_SHOW,
                    is_completed=False
                )
            else:
                referrer = None
            """
            Profile.objects.create(
                user=user,
                is_artist=data.get('is_artist'),
                is_venue=data.get('is_venue'),
                birthdate=data.get('birthdate'),
                referrer=None,#referrer,
                is_ghost=False if has_password else True
            )
        elif has_password:
            #User claims ghost account
            user.set_password(data.get('password'))
            user.save()
            user.profile.is_ghost = False
            user.profile.save()

        token = data.get('token')
        if token:
            act = Band.objects.filter(join_token=token).first()

            #Assign the new artist as the act's owner, if they're the only member
            if not act.owner:
                Band.objects.filter(id=act.id).update(is_redpine=True,owner=user)

            Invitation.objects.filter(join_token=token,recipient_email=data.get('email')).update(is_successful=True)
            #Consider sending an email to the original sender now, to let them know that the act they invited has registered.

        if data.get('is_artist') and not data.get('is_venue'):
            mail.act_signup(email=data.get('email'), data={'user':user})
            user.profile.welcome_create_act = True

        user.profile.generate_email_confirmation_token()
        user.profile.save()

        if has_password:
            data = UserPrivilegedSerializer(user).data
        else:
            user.set_password(random_password)
            user.save()
            data = UserGhostSerializer(user).data
            data['password'] = random_password
        return Response(data, status=200)


class FacebookRegistrationView(generics.CreateAPIView):
    email_not_found = '''
        RedPine was unable to retrieve your email address from your Facebook account.  Please add an email to your Facebook account and try again, or register using your email address.
    '''

    def create(self, request):
        serializer = FacebookRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        code = data.get('code')
        redirect_uri = data.get('redirect_uri')
        client = FacebookClient(settings.FACEBOOK_APP_ID, settings.FACEBOOK_APP_SECRET)

        try:
            client.confirm(redirect_uri, code)
            email = client.get_email()
        except Exception as e:
            raise BadRequest('Facebook authentication failed')

        if email is None: 
            raise BadRequest(type(self).email_not_found)

        check_user(data.get('username'), email)

        user = User.objects.create_user(
            username=data.get('username'),
            password=secrets.token_hex(32),
            email=email,
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )

        profile = Profile.objects.create(
            user=user,
            is_artist=data.get('is_artist'),
            is_venue=data.get('is_venue'),
        )

        data = UserPrivilegedSerializer(user).data
        return Response(data, status=200)


class ResetPasswordView(generics.CreateAPIView):
    def create(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        try:
            user = User.objects.get(email=data.get('email'))
            profile = user.profile

            if profile.password_reset_token != data.get('token'):
                raise exceptions.TokenInvalidException()

            user.set_password(data.get('password'))
            user.save()
            profile.password_reset_token = None
            profile.is_alpha_user = False
            profile.save()

            helpers.create_mail_from_template(
                recipient=user.email,
                subject='Password Successfully Reset',
                template='mail/reset_password_success.html',
                context={}
            )

            return Response({}, status=200)

        except (exceptions.TokenInvalidException, ObjectDoesNotExist,):
            raise ValidationError({'detail': 'Password reset failed'})


class ConfirmEmailView(generics.CreateAPIView):
    def create(self, request):
        serializer = ConfirmEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        try:
            user = User.objects.get(email=data.get('email'))
            profile = user.profile

            if profile.email_confirmation_token != data.get('token'):
                raise exceptions.TokenInvalidException()

            profile.is_email_confirmed = True
            profile.email_confirmation_token = None
            profile.save()

            helpers.create_mail_from_template(
                recipient=user.email,
                subject='Email Confirmed',
                template='mail/confirm_email_success.html',
                context={}
            )

            return Response(data={})

        except (exceptions.TokenInvalidException, ObjectDoesNotExist,):
            raise ValidationError({'detail': 'Email confirmation failed'})


class LogoutView(generics.CreateAPIView):
    serializer_class = LogoutSerializer

    def create(self, request):
        try:
            request.auth.delete()
        except:
            pass
        
        return Response(data={}, status=200)
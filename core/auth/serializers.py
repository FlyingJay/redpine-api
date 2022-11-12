from rest_framework import serializers


class FacebookAuthSerializer(serializers.Serializer):
    code = serializers.CharField()
    redirect_uri = serializers.URLField()


class PasswordAuthSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class PasswordRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(required=False)#False for ghost accounts
    email = serializers.EmailField()
    birthdate = serializers.DateTimeField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    is_artist = serializers.BooleanField(default=False)
    is_venue = serializers.BooleanField(default=False)
    token = serializers.CharField(required=False)
    referrer = serializers.CharField(required=False)


class FacebookRegistrationSerializer(serializers.Serializer):
    code = serializers.CharField()
    redirect_uri = serializers.URLField()
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    is_artist = serializers.BooleanField(default=False)
    is_venue = serializers.BooleanField(default=False)


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ConfirmEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField()
    password = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    pass
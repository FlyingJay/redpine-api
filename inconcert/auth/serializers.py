from rest_framework import serializers


class PasswordRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    referrer = serializers.CharField(required=False)


class PasswordAuthSerializer(serializers.Serializer):
    username = serializers.EmailField()
    password = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    pass
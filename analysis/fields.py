from rest_framework import serializers
from pytz import timezone, utc
from datetime import datetime, timedelta


class TimeZoneField(serializers.Field):
    def to_representation(self, obj):
        return str(obj)

    def to_internal_value(self, data):
        return timezone(data)


class UTCOffsetField(serializers.Field):
    def to_representation(self, obj):
        delta = obj.utcoffset(datetime.utcnow())
        hour_offset = delta.days * 24 + delta.seconds / 60 / 60
        return hour_offset

    def to_internal_value(self, data):
        return data
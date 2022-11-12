from rest_framework import serializers
from rest_framework.fields import (FileField,)
from datetime import datetime, timedelta
from drf_extra_fields import fields as drf_extra_fields
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.utils import six
import base64
import uuid


class Base64FileField(drf_extra_fields.Base64FieldMixin, FileField):
    """
    A django-rest-framework field for handling file-uploads through raw post data.
    It uses base64 for en-/decoding the contents of the file.
    """
    INVALID_FILE_MESSAGE = "Please upload a valid file."
    INVALID_TYPE_MESSAGE = "The type of the file couldn't be determined."

    PDF = 0
    DOC = 1
    DOCX = 2
    ODT = 3
    PNG = 4
    JPEG = 5
    GIF = 6

    ALLOWED_TYPES = [
        'pdf',
        'doc',
        'docx',
        'odt',
        'png',
        'jpg',
        'gif'
    ]

    MIME_TYPES = [
        (PDF,'application/pdf'),
        (DOC,'application/msword'),
        (DOCX,'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
        (ODT,'application/vnd.oasis.opendocument.text'),
        (PNG,'image/png'),
        (JPEG,'image/jpeg'),
        (GIF,'image/gif')
    ]

    def to_internal_value(self, base64_data):
        # Check if this is a base64 string
        if base64_data in self.EMPTY_VALUES:
            return None

        if isinstance(base64_data, six.string_types):
            # Get file mime type
            mime_type = base64_data[base64_data.find('data:')+5:base64_data.find(';')]
            try:
                file_type = [t[1] for t in self.MIME_TYPES].index(mime_type)
            except ValueError:
                raise ValidationError(self.INVALID_TYPE_MESSAGE)

            # Strip base64 header.
            if ';base64,' in base64_data:
                header, base64_data = base64_data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(base64_data)
            except (TypeError, binascii.Error, ValueError):
                raise ValidationError(self.INVALID_FILE_MESSAGE)

            # Generate file name:
            file_name = str(uuid.uuid4())[:12]  # 12 characters are more than enough.
            file_extension = self.get_file_extension(file_name, decoded_file, file_type)
            complete_file_name = file_name + "." + file_extension

            data = ContentFile(decoded_file, name=complete_file_name)
            return super(drf_extra_fields.Base64FieldMixin, self).to_internal_value(data)
        raise ValidationError('This is not an base64 string')

    def get_file_extension(self, filename, decoded_file, file_type):
        return self.ALLOWED_TYPES[file_type]


class Base64MusicField(drf_extra_fields.Base64FieldMixin, FileField):
    """
    A django-rest-framework field for handling file-uploads through raw post data.
    It uses base64 for en-/decoding the contents of the file.
    """
    INVALID_FILE_MESSAGE = "Please upload a valid file."
    INVALID_TYPE_MESSAGE = "The type of the file couldn't be determined."

    MPEG3 = 0
    XMPEG3 = 1
    MP3 = 2
    XMP3 = 3

    ALLOWED_TYPES = [
        'mpeg',
        'mpeg',
        'mp3',
        'mp3'
    ]

    MIME_TYPES = [
        (MPEG3,'audio/mpeg3'),
        (XMPEG3,'audio/x-mpeg3'),
        (MP3,'audio/mp3'),
        (XMP3,'audio/x-mp3')
    ]

    def to_internal_value(self, base64_data):
        # Check if this is a base64 string
        if base64_data in self.EMPTY_VALUES:
            return None

        if isinstance(base64_data, six.string_types):
            # Get file mime type
            mime_type = base64_data[base64_data.find('data:')+5:base64_data.find(';')]
            try:
                file_type = [t[1] for t in self.MIME_TYPES].index(mime_type)
            except ValueError:
                raise ValidationError(self.INVALID_TYPE_MESSAGE)

            # Strip base64 header.
            if ';base64,' in base64_data:
                header, base64_data = base64_data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(base64_data)
            except (TypeError, binascii.Error, ValueError):
                raise ValidationError(self.INVALID_FILE_MESSAGE)

            # Generate file name:
            file_name = str(uuid.uuid4())[:12]  # 12 characters are more than enough.
            file_extension = self.get_file_extension(file_name, decoded_file, file_type)
            complete_file_name = file_name + "." + file_extension

            data = ContentFile(decoded_file, name=complete_file_name)
            return super(drf_extra_fields.Base64FieldMixin, self).to_internal_value(data)
        raise ValidationError('This is not an base64 string')

    def get_file_extension(self, filename, decoded_file, file_type):
        return self.ALLOWED_TYPES[file_type]
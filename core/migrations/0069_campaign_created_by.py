# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-10-10 16:58
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
from django.contrib.auth.models import User
import django.db.models.deletion

try:
    default_id = User.objects.first().id
except:
    default_id = 1

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0068_auto_20171010_1558'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='created_by',
            field=models.ForeignKey(default=default_id, help_text='The user who created the campaign', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
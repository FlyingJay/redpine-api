# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-11-18 20:07
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0288_purchaseitem_is_hidden'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='is_hold',
            field=models.BooleanField(default=False, help_text='Has the venue put the show on hold?'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='created_by',
            field=models.ForeignKey(help_text='The user who created the show', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='is_featured',
            field=models.BooleanField(default=False, help_text='Whether to include the show on the home page or not..'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='is_redpine_approved',
            field=models.NullBooleanField(choices=[(None, 'null'), (True, 'true'), (False, 'false')], default=True, help_text='Whether RedPine has approved the show to be sent to the venue'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='is_successful',
            field=models.BooleanField(default=True, help_text='Whether the show has been fully funded or not'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='is_venue_approved',
            field=models.NullBooleanField(choices=[(None, 'null'), (True, 'true'), (False, 'false')], default=None, help_text='Whether the venue has confirmed the show'),
        ),
    ]
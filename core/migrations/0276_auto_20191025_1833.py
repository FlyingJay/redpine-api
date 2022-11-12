# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-10-25 18:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0275_profile_is_member_organizer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountsubscription',
            name='account_type',
            field=models.CharField(choices=[('ARTIST', 'ARTIST'), ('VENUE', 'VENUE'), ('ORGANIZER', 'ORGANIZER')], max_length=9),
        ),
    ]

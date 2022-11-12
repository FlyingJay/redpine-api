# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-28 11:09
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0080_merge_20180114_0514'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('band', models.ForeignKey(help_text='The band that wants to play', on_delete=django.db.models.deletion.CASCADE, to='core.Band')),
                ('user', models.ForeignKey(help_text='The user who submitted the request', on_delete=django.db.models.deletion.CASCADE, related_name='requests', to=settings.AUTH_USER_MODEL)),
                ('venue', models.ForeignKey(help_text='The venue which is being requested', on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='core.Venue')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
    ]

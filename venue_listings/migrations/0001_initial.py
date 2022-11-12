# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-05-01 19:40
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name_plural': 'Cities',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name_plural': 'countries',
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(max_length=200)),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Province',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='provinces', to='venue_listings.Country')),
            ],
        ),
        migrations.CreateModel(
            name='Venue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('archived', models.BooleanField(default=False)),
                ('title', models.CharField(db_index=True, max_length=200)),
                ('description', models.TextField(blank=True, max_length=5000, null=True)),
                ('capacity', models.IntegerField(blank=True, null=True)),
                ('address', models.CharField(blank=True, max_length=200, null=True)),
                ('postal_code', models.CharField(blank=True, max_length=20, null=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('has_wifi', models.BooleanField(default=False)),
                ('is_accessible_by_transit', models.BooleanField(default=False)),
                ('has_atm_nearby', models.BooleanField(default=False)),
                ('has_free_parking_nearby', models.BooleanField(default=False)),
                ('has_paid_parking_nearby', models.BooleanField(default=False)),
                ('is_wheelchair_friendly', models.BooleanField(default=False)),
                ('allows_smoking', models.BooleanField(default=False)),
                ('allows_all_ages', models.BooleanField(default=False)),
                ('has_stage', models.BooleanField(default=False)),
                ('has_microphones', models.BooleanField(default=False)),
                ('has_drum_kit', models.BooleanField(default=False)),
                ('has_piano', models.BooleanField(default=False)),
                ('has_wires_and_cables', models.BooleanField(default=False)),
                ('has_front_load_in', models.BooleanField(default=False)),
                ('has_back_load_in', models.BooleanField(default=False)),
                ('has_soundtech', models.BooleanField(default=False)),
                ('has_lighting', models.BooleanField(default=False)),
                ('has_drink_tickets', models.BooleanField(default=False)),
                ('has_meal_vouchers', models.BooleanField(default=False)),
                ('has_merch_space', models.BooleanField(default=False)),
                ('has_cash_box', models.BooleanField(default=False)),
                ('has_float_cash', models.BooleanField(default=False)),
                ('website', models.URLField(blank=True, default=None, null=True)),
                ('facebook', models.URLField(blank=True, default=None, null=True)),
                ('twitter', models.URLField(blank=True, default=None, null=True)),
                ('instagram', models.URLField(blank=True, default=None, null=True)),
                ('spotify', models.URLField(blank=True, default=None, null=True)),
                ('soundcloud', models.URLField(blank=True, default=None, null=True)),
                ('bandcamp', models.URLField(blank=True, default=None, null=True)),
                ('youtube', models.URLField(blank=True, default=None, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='venues', to='venue_listings.City')),
                ('primary_genre', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='primary_venues', to='venue_listings.Genre')),
                ('secondary_genre', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='secondary_venues', to='venue_listings.Genre')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='city',
            name='province',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cities', to='venue_listings.Province'),
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-07-15 20:14
from __future__ import unicode_literals

import core.validators
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0227_auto_20190715_1819'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('archived', models.BooleanField(default=False)),
                ('subscribed_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=6, validators=[core.validators.non_negative])),
                ('account_type', models.IntegerField(choices=[(0, 'ARTIST'), (1, 'VENUE')], help_text='artist or venue?')),
                ('product_name', models.CharField(choices=[(0, 'MEMBER'), (1, 'ULTIMATE')], help_text='What level was purchased?', max_length=8)),
                ('paid', models.BooleanField(default=False)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

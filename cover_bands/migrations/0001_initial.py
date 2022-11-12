# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-01-31 04:23
from __future__ import unicode_literals

from django.db import migrations, models
import django_extensions.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CoverLead',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('archived', models.BooleanField(default=False)),
                ('email', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('price', models.CharField(db_index=True, max_length=100)),
                ('message', models.TextField(blank=True, max_length=10000, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

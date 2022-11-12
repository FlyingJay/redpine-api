# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-13 23:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0127_auto_20180913_2102'),
    ]

    operations = [
        migrations.CreateModel(
            name='CampaignDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('document', models.FileField(upload_to='')),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='core.Campaign')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
    ]
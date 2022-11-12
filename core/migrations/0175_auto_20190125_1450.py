# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-01-25 14:50
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0174_auto_20190110_0123'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('recipient_email', models.CharField(max_length=200)),
                ('join_token', models.CharField(blank=True, max_length=32, null=True)),
                ('is_successful', models.BooleanField(default=False, help_text='Whether the invited user actually signed up or not')),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default='{}', null=True)),
                ('sender', models.ForeignKey(help_text='The user that sent the invitation', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='band',
            name='join_token',
            field=models.CharField(blank=True, default='126c067e70dee8e26c92040a6b361525', max_length=32, null=True),
        ),
    ]
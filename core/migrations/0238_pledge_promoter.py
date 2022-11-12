# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-08-12 05:39
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0237_campaign_draw_bonus'),
    ]

    operations = [
        migrations.AddField(
            model_name='pledge',
            name='promoter',
            field=models.ForeignKey(blank=True, default=None, help_text='The user recieving a "draw bonus", if any.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ticket_sales', to=settings.AUTH_USER_MODEL),
        ),
    ]
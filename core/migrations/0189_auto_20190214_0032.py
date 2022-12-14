# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-02-14 00:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0188_auto_20190213_2317'),
    ]

    operations = [
        migrations.AddField(
            model_name='globalsettings',
            name='feed_picture',
            field=models.ImageField(blank=True, help_text='The image to display on the feed.', null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='globalsettings',
            name='homepage_picture',
            field=models.ImageField(blank=True, help_text="The image to display on the homepage. Set to 'None' for a random venue.", null=True, upload_to=''),
        ),
    ]

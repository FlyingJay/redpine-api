# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-16 02:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0105_auto_20180515_0000'),
    ]

    operations = [
        migrations.CreateModel(
            name='BandToBandReview',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('archived', models.BooleanField(default=False)),
                ('overall', models.IntegerField(choices=[(0, 'terrible'), (1, 'poor'), (2, 'average'), (3, 'good'), (4, 'great')])),
                ('comment', models.TextField(blank=True, help_text='Additional comments for the review.', max_length=2000, null=True)),
                ('completed', models.BooleanField(default=False)),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('completed_date', models.DateTimeField(null=True)),
                ('public_response', models.TextField(blank=True, default=None, help_text='A public response to the review.', max_length=2000, null=True)),
                ('private_response', models.TextField(blank=True, default=None, help_text='A private response to the review - just for the reviewer.', max_length=2000, null=True)),
                ('draw', models.IntegerField(choices=[(0, 'terrible'), (1, 'poor'), (2, 'average'), (3, 'good'), (4, 'great')], help_text='Did the band accurately represent their draw?')),
                ('communication', models.IntegerField(choices=[(0, 'terrible'), (1, 'poor'), (2, 'average'), (3, 'good'), (4, 'great')], help_text='Did the band communicate effectively when required?')),
                ('ease_of_working', models.IntegerField(choices=[(0, 'terrible'), (1, 'poor'), (2, 'average'), (3, 'good'), (4, 'great')], help_text='Was the band easy to work with?')),
                ('band', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews_by_bands', to='core.Band')),
                ('campaign', models.ForeignKey(blank=True, help_text='The event for which the review applies.', null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Campaign')),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='band_reviews', to='core.Band')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BandToVenueReview',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('archived', models.BooleanField(default=False)),
                ('overall', models.IntegerField(choices=[(0, 'terrible'), (1, 'poor'), (2, 'average'), (3, 'good'), (4, 'great')])),
                ('comment', models.TextField(blank=True, help_text='Additional comments for the review.', max_length=2000, null=True)),
                ('completed', models.BooleanField(default=False)),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('completed_date', models.DateTimeField(null=True)),
                ('public_response', models.TextField(blank=True, default=None, help_text='A public response to the review.', max_length=2000, null=True)),
                ('private_response', models.TextField(blank=True, default=None, help_text='A private response to the review - just for the reviewer.', max_length=2000, null=True)),
                ('equipment', models.IntegerField(choices=[(0, 'terrible'), (1, 'poor'), (2, 'average'), (3, 'good'), (4, 'great')], help_text='Did the venue accurately represent the variety and quality of their equipment?')),
                ('communication', models.IntegerField(choices=[(0, 'terrible'), (1, 'poor'), (2, 'average'), (3, 'good'), (4, 'great')], help_text='Did the venue communicate effectively when required?')),
                ('ease_of_working', models.IntegerField(choices=[(0, 'terrible'), (1, 'poor'), (2, 'average'), (3, 'good'), (4, 'great')], help_text='Was the venue easy to work with?')),
                ('campaign', models.ForeignKey(blank=True, help_text='The event for which the review applies.', null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Campaign')),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='venue_reviews', to='core.Band')),
                ('venue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews_by_bands', to='core.Venue')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VenueToBandReview',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('archived', models.BooleanField(default=False)),
                ('overall', models.IntegerField(choices=[(0, 'terrible'), (1, 'poor'), (2, 'average'), (3, 'good'), (4, 'great')])),
                ('comment', models.TextField(blank=True, help_text='Additional comments for the review.', max_length=2000, null=True)),
                ('completed', models.BooleanField(default=False)),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('completed_date', models.DateTimeField(null=True)),
                ('public_response', models.TextField(blank=True, default=None, help_text='A public response to the review.', max_length=2000, null=True)),
                ('private_response', models.TextField(blank=True, default=None, help_text='A private response to the review - just for the reviewer.', max_length=2000, null=True)),
                ('draw', models.IntegerField(choices=[(0, 'terrible'), (1, 'poor'), (2, 'average'), (3, 'good'), (4, 'great')], help_text='Did the band accurately represent their draw?')),
                ('communication', models.IntegerField(choices=[(0, 'terrible'), (1, 'poor'), (2, 'average'), (3, 'good'), (4, 'great')], help_text='Did the band communicate effectively when required?')),
                ('ease_of_working', models.IntegerField(choices=[(0, 'terrible'), (1, 'poor'), (2, 'average'), (3, 'good'), (4, 'great')], help_text='Was the band easy to work with?')),
                ('band', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews_by_venues', to='core.Band')),
                ('campaign', models.ForeignKey(blank=True, help_text='The event for which the review applies.', null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Campaign')),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='band_reviews', to='core.Venue')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
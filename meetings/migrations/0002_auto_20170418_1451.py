# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-18 14:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meetings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='meeting_type',
            field=models.CharField(blank=True, choices=[('in-person', 'In-person'), ('telephone', 'Telephone'), ('facebook', 'Facebook')], max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='socialmediachannel',
            name='channel_type',
            field=models.CharField(choices=[('GooglePlus', 'Google+'), ('YouTube', 'YouTube'), ('Facebook', 'Facebook'), ('Twitter', 'Twitter')], max_length=20),
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-31 13:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('builds', '0018_project_auto_approve_master_builds'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={'ordering': ('name',)},
        ),
    ]

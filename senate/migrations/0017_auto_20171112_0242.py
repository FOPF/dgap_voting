# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-11 23:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('senate', '0016_auto_20171111_0104'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventdocument',
            name='event',
        ),
        migrations.DeleteModel(
            name='EventDocument',
        ),
    ]
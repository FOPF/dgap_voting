# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-27 15:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='content',
            field=models.TextField(max_length=20000, verbose_name='Контент'),
        ),
    ]

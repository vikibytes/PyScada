# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-12 20:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [(b'phant', '0001_initial'), (b'phant', '0002_auto_20161012_2017')]

    initial = True

    dependencies = [
        ('pyscada', '0031_delete_variableconfigfileimport'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhantDevice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_key', models.SlugField(default=b'....................', max_length=20, unique=True)),
                ('private_key', models.CharField(default=b'....................', max_length=20)),
                ('phant_device', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='pyscada.Device')),
            ],
        ),
    ]

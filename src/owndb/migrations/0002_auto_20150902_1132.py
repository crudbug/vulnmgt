# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('owndb', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={'ordering': ('name',), 'verbose_name': 'project', 'verbose_name_plural': 'projects'},
        ),
    ]

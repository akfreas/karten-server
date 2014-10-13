# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Karten', '0002_auto_20141011_1814'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kartenstack',
            name='creation_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='kartenuser',
            name='email',
            field=models.EmailField(unique=True, max_length=255, verbose_name=b'email address', db_index=True),
        ),
    ]

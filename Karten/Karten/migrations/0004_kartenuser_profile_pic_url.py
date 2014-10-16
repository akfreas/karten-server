# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Karten', '0003_auto_20141013_0105'),
    ]

    operations = [
        migrations.AddField(
            model_name='kartenuser',
            name='profile_pic_url',
            field=models.URLField(null=True, blank=True),
            preserve_default=True,
        ),
    ]

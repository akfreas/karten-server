# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Karten', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kartenuserfriendrequest',
            name='date_accepted',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]

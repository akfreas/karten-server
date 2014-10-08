# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='KartenCouchServer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('host', models.CharField(max_length=50)),
                ('port', models.IntegerField()),
                ('protocol', models.CharField(max_length=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KartenStack',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('couchdb_name', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=255, null=True, blank=True)),
                ('creation_date', models.DateField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KartenUserFriendRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('accepted', models.BooleanField(default=False)),
                ('date_accepted', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KartenUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('username', models.CharField(unique=True, max_length=100)),
                ('email', models.EmailField(null=True, max_length=255, blank=True, unique=True, verbose_name=b'email address', db_index=True)),
                ('external_user_id', models.CharField(max_length=255, null=True, blank=True)),
                ('external_service', models.CharField(max_length=20, null=True, blank=True)),
                ('date_joined', models.DateTimeField(null=True, blank=True)),
                ('date_last_seen', models.DateTimeField(null=True, blank=True)),
                ('first_name', models.CharField(max_length=100, null=True, blank=True)),
                ('last_name', models.CharField(max_length=100, null=True, blank=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('friends', models.ManyToManyField(related_name='friends_rel_+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['username'],
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='kartenuserfriendrequest',
            name='accepting_user',
            field=models.ForeignKey(related_name=b'friend_requests', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='kartenuserfriendrequest',
            name='requesting_user',
            field=models.ForeignKey(related_name=b'friends_requested', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='kartenstack',
            name='allowed_users',
            field=models.ManyToManyField(related_name=b'stacks', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='kartenstack',
            name='couchdb_server',
            field=models.ForeignKey(related_name=b'stacks', to='Karten.KartenCouchServer'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='kartenstack',
            name='owner',
            field=models.ForeignKey(related_name=b'admin_of', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]

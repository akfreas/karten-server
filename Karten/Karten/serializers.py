from rest_framework import serializers
from Karten.models import *
from django.contrib.auth.models import User

class KartenUserSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.Field(source='owner.username')

    class Meta:
        model = KartenUser
        fields = ('external_user_id', 
                'external_service',
                'date_joined',
                'first_name',
                'last_name',
                )

class KartenStackSerializer(serializers.HyperlinkedModelSerializer):

    owner = serializers.Field(source='owner.username')

    class Meta:
        model = KartenStack
        fields = ('couchdb_name',
                'couchdb_server',
                'owner',
                'name',
                'description',
                'allowed_users',
                'creation_date')


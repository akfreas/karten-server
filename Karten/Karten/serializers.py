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

class KartenCouchServerSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = KartenCouchServer
        fields = ('server_url',)

class KartenStackSerializer(serializers.HyperlinkedModelSerializer):

    owner = serializers.Field(source='owner.username')
    couchdb_server = KartenCouchServerSerializer(read_only=True)

    class Meta:
        model = KartenStack
        fields = ('id',
                'couchdb_name',
                'couchdb_server',
                'owner',
                'name',
                'description',
                'allowed_users',
                'creation_date')
        read_only_fields = ('couchdb_name',)


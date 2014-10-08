from rest_framework import serializers
from Karten.models import *
from django.contrib.auth.models import User

class KartenUserSerializer(serializers.HyperlinkedModelSerializer):

    external_user_id = serializers.CharField(required=False)
    external_service = serializers.CharField(required=False)


    class Meta:
        model = KartenUser
        fields = ('id',
                'password',
                'username',
                'external_user_id', 
                'external_service',
                'date_joined',
                'first_name',
                'last_name',
                )
        write_only_fields = ('password',)

class KartenFriendRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = KartenUserFriendRequest
        fields = ('requesting_user',
                'accepting_user',
                'accepted')

class KartenCouchServerSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = KartenCouchServer
        fields = ('host',
                'port',
                'protocol',
                'id')

class KartenStackSerializer(serializers.ModelSerializer):

    owner = serializers.Field(source='owner.id')
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


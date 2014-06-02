from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _
import facebook
from jsonpickle.pickler import Pickler
import jsonpickle
import couchdb
from Karten.errors import *
from Karten.settings import COUCHDB_SERVERS
from Karten.json_utils import *
import re

def couchdb_instance():
    instance = couchdb.Server(url=COUCHDB_SERVERS['Karten'])
    return instance

class KartenUser(models.Model):

    external_user_id = models.CharField(max_length=255, null=True)
    external_service = models.CharField(max_length=20, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    friends = models.ManyToManyField('self', symmetrical=False)

    def populate_with_fb_info(self, access_token):
        graph_obj = facebook.GraphAPI(access_token)
        fb_object = graph_obj.get_object(self.user_id, fields="first_name,last_name")
        self.first_name = fb_object['first_name']
        self.last_name = fb_object['last_name']

    def friends_to_json(self):
        friends = self.friends.all()
        return jsonpickle.encode(friends, unpicklable=False)

    def update_with_json(self, json):
        allowed_keys = ['first_name', 'last_name']
        filtered_keys = [key for key in json.keys() if key in allowed_keys]
        for key in filtered_keys:
            self.__setattr__(key, json[key])

    def to_json(self):
        return jsonpickle.encode(to_json(self), unpicklable=False)

    @classmethod
    def get_or_create(user_id):
        try:
            user = KartenUser.objects.get(user_id=user_id)
        except KartenUser.DoesNotExist: 
            user = KartenUser(user_id=user_id)

        return user

class KartenCouchServer(models.Model):
    server_url = models.URLField(max_length=255)

    @classmethod
    def server_for_app(self):
        try:
            server = KartenCouchServer.objects.get(server_url=COUCHDB_SERVERS['Karten'])
        except KartenCouchServer.DoesNotExist:
            server = KartenCouchServer(server_url=COUCHDB_SERVERS['Karten'])
            server.save()

        return server
    def to_json(self):
        return jsonpickle.encode(to_json(self), unpicklable=False)
    
class KartenStack(models.Model):

    couchdb_name = models.CharField(max_length=255)
    couchdb_server = models.ForeignKey('KartenCouchServer', related_name='stacks')
    owner = models.ForeignKey('KartenUser', related_name='admin_of', null=True) 
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, null=True, blank=True)
    allowed_users = models.ManyToManyField('KartenUser', related_name='stacks')

    def delete(self, *args, **kwargs):
        try:
            server = couchdb.Server(self.couchdb_server.server_url)
            server.delete(self.couchdb_name)
        except couchdb.ResourceNotFound:
            e = KartenCouchDBException(message=_("The database you are trying to delete does not exist."),\
                    error_code="ErrorDatabaseDoesNotExist")
            raise e
        super(KartenStack, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):

        if self.couchdb_name is None or len(self.couchdb_name) is 0:
            couchserver = couchdb_instance()
            try:
                formatted_db_name = re.sub(r'[^\w]', '_', self.name.lower())
                couchserver.create(formatted_db_name)
                self.couchdb_name = formatted_db_name
                self.couchdb_server = KartenCouchServer.server_for_app()
            except couchdb.PreconditionFailed:
                m = "Database with name already exists. Please enter another name." % {'db_name' : self.name}
                mesg = _(m)

                e = KartenCouchDBException(message=mesg, error_code="ErrorDatabaseExists")
                raise e

        super(KartenStack, self).save(*args, **kwargs)

    def to_json(self):
        return jsonpickle.encode(to_json(self), unpicklable=False)

    @property
    def couchdb_url(self):
        return COUCHDB_SERVERS['Karten'] + self.couchdb_name


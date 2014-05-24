from django.conf import settings
from django.db import models
import facebook
import jsonpickle
from Karten.errors import *

def couchdb_instance():
    COUCHDB_URL = "http://192.168.0.233:5984"
    instance = couchdb.Server(url=COUCHDB_URL)
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

    def to_json(self):
        return jsonpickle.encode(self, unpicklable=False)

    def friends_to_json(self):
        friends = self.friends.all()
        return jsonpickle.encode(friends, unpicklable=False)

    def update_with_json(self, json):
        allowed_keys = ['first_name', 'last_name']
        filtered_keys = [key for key in json.keys() if key in allowed_keys]
        for key in filtered_keys:
            self.__setattr__(key, json[key])


    @classmethod
    def get_or_create(user_id):
        try:
            user = KartenUser.objects.get(user_id=user_id)
        except KartenUser.DoesNotExist: 
            user = KartenUser(user_id=user_id)

        return user

    
class KartenCouchDB(models.Model):

    couchdb_name = models.CharField(max_length=255)
    admin = models.ForeignKey('KartenUser', related_name='admin_of', null=True) 
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, null=True, blank=True)
    allowed_users = models.ForeignKey('KartenUser', related_name='databases', null=True)

    def save(self):
        if self.couchdb_name is None:
            couchserver = couchdb_instance()
            try:
                formatted_db_name = new_database.name.replace(" ", "_").lower()
                couchserver.create(formatted_db_name)
            except couchdb.PreconditionFailed:
                mesg = _("Database with name '%(db_name)' already exists.\
                        Please enter another name.") % {'db_name' : database_name}

                e = KartenCouchDBException(message=_mesg, error_code="ErrorDatabaseExists")
                raise e

        super(KartenCouchDB, self).save(*args, **kwargs)



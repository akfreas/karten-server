from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import facebook
from jsonpickle.pickler import Pickler
import jsonpickle
import couchdb
from Karten.errors import *
from Karten.settings import COUCHDB_SERVERS
from Karten.json_utils import *
from datetime import datetime
import re

def couchdb_instance():
    instance = couchdb.Server(url=COUCHDB_SERVERS['Karten'])
    return instance


class KartenUserManager(BaseUserManager):

    def create_user(self, username, password):
        
        user = self.model(
                username = username,
        )


        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):

        time_now = datetime.now()
        user = self.create_user(
            username=username,
            password=password,
        )
        user.date_joined = time_now
        user.date_last_seen = time_now
        user.is_admin = True
        user.is_staff = True

        user.save(using=self._db)
        return user



class KartenUser(AbstractBaseUser):

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ['username']

    USERNAME_FIELD = 'username'
    objects = KartenUserManager()

    def __unicode__(self):
        return "id %s: %s %s" % (self.id, self.first_name, self.last_name)

    username = models.CharField(max_length=100, unique=True)
        
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        null=True,
        blank=True,
        unique=True,
        db_index=True,
    )

    external_user_id = models.CharField(max_length=255, null=True)
    external_service = models.CharField(max_length=20, null=True)
    date_joined = models.DateTimeField(null=True, blank=True)
    date_last_seen = models.DateTimeField(null=True, blank=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    friends = models.ManyToManyField('self', symmetrical=False)
    is_admin = models.BooleanField(default=False)

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
    def find_by_unique(self, user_id):
        query = Q(external_user_id=user_id) | Q(id=user_id)
        user = KartenUser.objects.get(query)
        return user

    @classmethod
    def get_or_create(user_id):
        query = Q(external_user_id=user_id) | Q(id=user_id)
        try:
            user = KartenUser.objects.get(query)
        except KartenUser.DoesNotExist: 
            e = KartenUserDoesNotExist(user_id)
            return e
        return user

    def get_full_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    def get_short_name(self):
        return self.first_name

    def __unicode__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        #TODO do this properly
        return True

    def has_module_perms(self, app_label):
        #TODO do this properly
        return True

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def is_active(self):
        return True


    @is_staff.setter
    def is_staff(self, value):
        self.is_admin = value


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
    creation_date = models.DateField()

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


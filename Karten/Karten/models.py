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

from Karten.json_utils import *
from django.utils import timezone
import couch_utils
from CouchDBServerManager import couchdb_instance, unauthed_couch_url
import re

class KartenUserManager(BaseUserManager):

    def create_user(self, username, password):
        
        user = self.model(
                username = username,
        )


        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):

        time_now = timezone.now()
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
        unique=True,
        db_index=True,
    )

    external_user_id = models.CharField(max_length=255, null=True, blank=True)
    external_service = models.CharField(max_length=20, null=True, blank=True)
    date_joined = models.DateTimeField(null=True, blank=True)
    date_last_seen = models.DateTimeField(null=True, blank=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    friends = models.ManyToManyField('self', symmetrical=True)
    is_admin = models.BooleanField(default=False)

    def populate_with_fb_info(self, access_token):
        graph_obj = facebook.GraphAPI(access_token)
        fb_object = graph_obj.get_object(self.user_id, fields="first_name,last_name")
        self.first_name = fb_object['first_name']
        self.last_name = fb_object['last_name']

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

class KartenUserFriendRequest(models.Model):

    requesting_user = models.ForeignKey('KartenUser', related_name='friends_requested')
    accepting_user = models.ForeignKey('KartenUser', related_name='friend_requests')
    accepted = models.BooleanField(default=False)
    date_accepted = models.DateTimeField(blank=True, null=True)
 

class KartenCouchServer(models.Model):
    server_url = models.URLField(max_length=255)

    host = models.CharField(max_length=50)
    port = models.IntegerField()
    protocol = models.CharField(max_length=10)

    @property
    def server_url(self):
        return "%s://%s:%s/" % (self.protocol, self.host, self.port)


    @classmethod
    def server_for_app(self):
        server = KartenCouchServer.objects.first()
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
    creation_date = models.DateTimeField()

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

        if (self.couchdb_name is None or len(self.couchdb_name) is 0) and self.id is None:
            couchserver = couchdb_instance()
            self.creation_date = timezone.now()
            try:
                formatted_db_name = re.sub(r'[^\w]', '_', self.name.lower())
                formatted_db_name += ("_%s" % self.owner.username)
                couch_utils.create_db_for_user(couchserver, formatted_db_name, self.owner.username)
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
        return unauthed_couch_url() + self.couchdb_name


from django.db.models.signals import pre_save, post_save, pre_delete, m2m_changed
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

@receiver(m2m_changed, sender=KartenStack.allowed_users.through)
def update_allowed_users_on_couchdb(sender, instance, action=None, pk_set=None, *args, **kwargs):

    if action == 'post_add':
        allowed_users = KartenUser.objects.filter(id__in=pk_set)
        usernames = [u.username for u in allowed_users]
        couchserver = couchdb_instance()
        couch_utils.set_users_on_db(couchserver, instance.couchdb_name, usernames)

@receiver(post_save, sender=KartenStack)
def add_owner_to_allowed_users(sender, instance=None, created=False, *args, **kwargs):
    if created is True:
        instance.allowed_users.add(instance.owner)
        instance.save()


@receiver(pre_delete, sender=KartenStack)
def pre_delete_db(sender, instance, signal, *args, **kwargs):

    try:
        server = couchdb.Server(instance.couchdb_server)
        server.delete(instance.couchdb_name)
    except couchdb.ResourceNotFound:
        e = KartenCouchDBException(message=_("The database you are trying to delete does not exist."),\
                error_code="ErrorDatabaseDoesNotExist")
        raise e

@receiver(pre_delete, sender=KartenUser)
def delete_couch_user(sender, instance=None, **kwargs):
    couch_utils.delete_couch_user(couchdb_instance(), instance.username)

@receiver(post_save, sender=KartenUser)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        token = Token.objects.create(user=instance)
        couchserver = couchdb_instance()
        couch_utils.create_couch_user(couchserver, instance.username, token.key)

@receiver(post_save, sender=Token)
def update_couchdb_password(sender, instance=None, created=False, **kwargs):
    if created is False:
        couchserver = couchdb_instance()
        couch_utils.change_user_password(couchserver, instance.user.username, instance.key)

@receiver(pre_save, sender=KartenUserFriendRequest)
def add_friend_to_list(sender, instance=None, created=False, **kwargs):

    if instance.accepted is True:
        acceptor = instance.accepting_user
        accepted = instance.requesting_user
        accepted.friends.add(acceptor)
        accepted.save()


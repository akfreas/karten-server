import couchdb
from Karten.models import *
from Karten.errors import *

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from CouchDBServerManager import couchdb_instance

@receiver(pre_delete, sender=KartenStack)
def pre_delete_db(sender, instance, signal, *args, **kwargs):

    try:
        server = couchdb.Server(instance.couchdb_server)
        server.delete(instance.couchdb_name)
    except couchdb.ResourceNotFound:
        e = KartenCouchDBException(message=_("The database you are trying to delete does not exist."),\
                error_code="ErrorDatabaseDoesNotExist")
        raise e

@receiver(pre_delete, sender=get_user_model())
def delete_couch_user(sender, instance=None, **kwargs):
    couch_utils.delete_couch_user(couchdb_instance(), instance.username)

@receiver(post_save, sender=get_user_model())
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


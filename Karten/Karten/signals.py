from django.signals import pre_delete
from Karten.models import *
import couchdb
from errors import *

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


def pre_delete_db(sender, instance, signal, *args, **kwargs):

    try:
        server = couchdb.Server(instance.couchdb_server)
        server.delete(instance.couchdb_name)
    except couchdb.ResourceNotFound:
        e = KartenCouchDBException(message=_("The database you are trying to delete does not exist."),\
                error_code="ErrorDatabaseDoesNotExist")
        raise e
pre_delete.connect(pre_delete_db, sender=KartenDB)


@receiver(post_save, sender=get_user_model())
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


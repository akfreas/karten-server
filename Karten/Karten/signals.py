from django.signals import pre_delete
from Karten.models import *
import couchdb
from errors import *

def pre_delete_db(sender, instance, signal, *args, **kwargs):

    try:
        server = couchdb.Server(instance.couchdb_server)
        server.delete(instance.couchdb_name)
    except couchdb.ResourceNotFound:
        e = KartenCouchDBException(message=_("The database you are trying to delete does not exist."),\
                error_code="ErrorDatabaseDoesNotExist")
        raise e


pre_delete.connet(pre_delete_db, sender=KartenDB)



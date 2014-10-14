from Karten.models import *
import random
import string
from django.db.models.signals import post_save, m2m_changed

def rnd():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(random.randrange(4, 12)))

def random_email():
    return "%s@%s.com" % (rnd(), rnd())

def create_user(username, password):

    new_user = KartenUser(username=username, date_joined=timezone.now(), email=random_email())
    new_user.save()
    new_user.set_password(password)
    new_user.save()
    return new_user

def create_dummy_users(count=10, username_prefix=None):
    
    users = []
    for i in range(0, count):
        username = rnd()
        if username_prefix is not None:
            username = "%s%s" % (username_prefix, username)
        users.append(create_user(username, "password"))

    return users

def disconnect_couchdb_signals():
    post_save.disconnect(create_auth_token, sender=KartenUser)
    post_save.disconnect(update_couchdb_password, sender=Token)
    m2m_changed.disconnect(update_allowed_users_on_couchdb, sender=KartenStack.allowed_users.through)
    


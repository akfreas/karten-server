from Karten.models import *
from Karten.errors import *
from Karten.json_utils import *

from django.http import HttpResponseRedirect, HttpResponse


import json
import jsonpickle
from jsonpickle.pickler import Pickler


#couchdb utils

def couchdb_instance():
    COUCHDB_URL = "http://192.168.0.233:5984"
    instance = couchdb.Server(url=COUCHDB_URL)
    return instance

#facebook context decorator

def add_request_context(f):
    def inner_def(request, *args, **kwargs):
        query_dict = request.GET
        f_globals = f.func_globals
        if 'token' in query_dict.keys() and query_dict['token'] is not None:
            f_globals['token'] = user_dict['token']
        else:
            f_globals['token'] = None
        
        result = f(request, *args, **kwargs)
        return result
    return inner_def


def all_users(request):
    users = KartenUser.objects.all()
    users_string = jsonpickle.encode([u for u in users], unpicklable=False)
    return HttpResponse(content=users_string, content_type="application/json")

@add_request_context
def create_user(request):

    params = request.GET
    new_user = KartenUser(first_name=params['first_name'], 
            last_name=params['last_name'])

    if 'external_service' in params.keys() and 'external_user_id' in params.keys():
        ext_id = params['external_user_id']
        existing_users = KartenUser.objects.filter(external_user_id=ext_id)
        if existing_users.count() > 0:
            error = KartenUserAlreadyExists(ext_id)
            return error.http_response()

        new_user.external_user_id=ext_id
        new_user.external_service=params['external_service']
    
    if token is not None:
        new_user.populate_with_fb_info(token)

    new_user.save()

    response = jsonpickle.encode(new_user, unpicklable=False)
    return HttpResponse(content=response, mimetype="application/json")
    
def get_user(request, user_id):

    user = KartenUser.objects.get(id=user_id)
    return HttpResponse(content=user.to_json(), mimetype="application/json")

def update_user(request, user_id):

    user = KartenUser.objects.get(id=user_id)
    user_dict = request.GET
    user.update_with_json(user_dict)
    user.save()
    return HttpResponse(content=user.to_json(), mimetype="application/json")

def get_user_friends(request, user_id):

    user = KartenUser.objects.get(id=user_id)
    return HttpResponse(conent=user.friends_to_json(), content="application/json")
        
@add_request_context
def create_user_friend(request, user_id):
    user = KartenUser.objects.get(id=user_id)
    friend_json = request.body
    friend = KartenUser.get_or_create(friend_json['id'])
    friend.update_with_json(friend_json)

    if facebook_token is not None:
        friend.populate_with_fb_info(facebook_token)

    return HttpResponse(content=friend.to_json(), mimetype="application/json")
    

@add_request_context
def create_database(request):
    
    params = request.GET
    user = KartenUser.objects.get(id=params['owner'])
    new_database = KartenDB(name=params['name'], 
                                 description=params['description'], 
                                 owner=user)
    new_database.owner = user
    new_database.save()
    return HttpResponse(content=new_database.to_json(), content_type="application/json")
   
@add_request_context
def delete_database(request, database_id):
    params = request.GET
    try:
        database = KartenDB.objects.get(id=database_id)
    except KeyError:
        exception = ErrorMessage(e.description, e.name)
        return exception.http_response()
    except KartenDB.DoesNotExist:
        KartenDBException(params['id'])
        return KartenDBException.http_response()

    database.delete()
    return HttpResponse(content=database.to_json(), content_type="appliction/json")

@add_request_context
def get_user_databases(request, user_id):

    try:
        user = KartenUser.objects.get(id=user_id)
    except KartenUser.DoesNotExist:
        exception = KartenUserDoesNotExist(user_id, _("The database you requested does not exist."))
        return exception.http_response

    databases = user.databases.all()
    return HttpResponse(content=jsonpickle.encode(databases, unpicklable=False), mimetype="application/json")
    
@add_request_context
def add_user_to_database(request, database_id, user_id):

    try:
        database = KartenDB.objects.get(id=database_id)
    except KartenDB.DoesNotExist:
        e = KartenDBDoesNotExist(database_id)
        return e.http_response()

    try:
        user = KartenUser.objects.get(id=user_id)
    except KartenUser.DoesNotExist:
        e = KartenUserDoesNotExist(user_id)
        return e.http_response()

    database.allowed_users.add(user)
    database.save()
    return HttpResponse(content=database.to_json(), content_type="application/json")

@add_request_context
def remove_user_from_database(request, database_id, user_id):

    try:
        database = KartenDB.objects.get(id=database_id)
    except KartenDB.DoesNotExist:
        e = KartenDBDoesNotExist(database_id)
        return e.http_response()

    try:
        user = KartenUser.objects.get(id=user_id)
    except KartenUser.DoesNotExist:
        e = KartenUserDoesNotExist(user_id)
        return e.http_response()

    database.allowed_users.remove(user)
    database.save()
    return HttpResponse(content=database.to_json(), content_type="application/json")

@add_request_context
def get_all_users_for_database(request, database_id):

    try:
        database = KartenDB.objects.get(id=database_id)
    except KartenDB.DoesNotExist:
        e = KartenDBDoesNotExist(database_id)
        return e.http_response()
    users = database.users.all()
    json_dict = to_json(users)

    return HttpResponse(pickler.encode(json_dict, unpicklable=False), content_type="application_json")





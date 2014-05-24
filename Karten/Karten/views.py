from Karten.models import *
from Karten.errors import *

from django.http import HttpResponseRedirect, HttpResponse


import json
import jsonpickle


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
    post_json = json.loads(request.body)
    new_database = KartenCouchDB(name=post_json['name'], 
                                 description=post_json['description'], 
                                 admin=user)
    try:
        new_database.admin = user
        new_database.save()
    except Exception as e:
        return e.http_response()

@add_request_context
def get_user_databases(request, user_id):

    try:
        user = KartenUser.objects.get(id=user_id)
    except KartenUser.DoesNotExist:
        exception = KartenUserDoesNotExist(user_id)
        return exception.http_response

    databases = user.databases.all()
    return HttpResponse(content=jsonpickle.encode(databases, unpicklable=False), mimetype="application/json")
    
   


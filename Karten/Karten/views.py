from Karten.models import *
from Karten.errors import *
from Karten.json_utils import *
from django.utils.translation import ugettext as _

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
    user = KartenUser(first_name=params['first_name'], 
            last_name=params['last_name'])

    if 'external_service' in params.keys() and 'external_user_id' in params.keys():
        ext_id = params['external_user_id']
        existing_users = KartenUser.objects.filter(external_user_id=ext_id)
        if existing_users.count() > 1:
            error = KartenUserAlreadyExists(ext_id)
            return error.http_response()
        elif existing_users.count() == 1:
            user = existing_users[0]
        elif existing_users.count() == 0:
            user.external_user_id=ext_id
            user.external_service=params['external_service']
    
    if token is not None:
        user.populate_with_fb_info(token)

    user.save()

    response = jsonpickle.encode(user, unpicklable=False)
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
def create_stack(request):
    
    params = request.GET
    user = KartenUser.objects.get(id=params['owner[id]'])

    new_stack = KartenStack(name=params['name'], 
                                 owner=user)
    if 'description' in params.keys():
        new_stack.description = params['description']

    new_stack.owner = user
    new_stack.save()
    new_stack.allowed_users.add(user)
    new_stack.save()
    return HttpResponse(content=new_stack.to_json(), content_type="application/json")
   
@add_request_context
def delete_stack(request, stack_id):
    params = request.GET
    try:
        stack = KartenStack.objects.get(id=stack_id)
    except KeyError:
        exception = ErrorMessage(e.description, e.name)
        return exception.http_response()
    except KartenStack.DoesNotExist:
        KartenStackException(params['id'])
        return KartenStackException.http_response()

    stack.delete()
    return HttpResponse(content=stack.to_json(), content_type="appliction/json")

@add_request_context
def get_user_stacks(request, user_id):

    try:
        user = KartenUser.objects.get(id=user_id)
    except KartenUser.DoesNotExist:
        exception = KartenUserDoesNotExist(user_id, _("The stack you requested does not exist."))
        return exception.http_response

    stacks = to_json(user.stacks.all())
    return HttpResponse(content=jsonpickle.encode(stacks, unpicklable=False), mimetype="application/json")
    
@add_request_context
def add_user_to_stack(request, stack_id, user_id):

    try:
        stack = KartenStack.objects.get(id=stack_id)
    except KartenStack.DoesNotExist:
        e = KartenStackDoesNotExist(stack_id)
        return e.http_response()

    try:
        user = KartenUser.objects.get(id=user_id)
    except KartenUser.DoesNotExist:
        e = KartenUserDoesNotExist(user_id)
        return e.http_response()

    stack.allowed_users.add(user)
    stack.save()

    response_dict = to_json(stack)
    response_dict['allowed_users'] = to_json(stack.allowed_users.all())
    return HttpResponse(content=jsonpickle.encode(response_dict, unpicklable=False), content_type="application/json")

@add_request_context
def remove_user_from_stack(request, stack_id, user_id):

    try:
        stack = KartenStack.objects.get(id=stack_id)
    except KartenStack.DoesNotExist:
        e = KartenStackDoesNotExist(stack_id)
        return e.http_response()

    try:
        user = KartenUser.objects.get(id=user_id)
    except KartenUser.DoesNotExist:
        e = KartenUserDoesNotExist(user_id)
        return e.http_response()

    stack.allowed_users.remove(user)
    stack.save()
    response_dict = to_json(stack)
    response_dict['allowed_users'] = to_json(stack.allowed_users.all())
    return HttpResponse(content=jsonpickle.encode(response_dict, unpicklable=False), content_type="application/json")

@add_request_context
def get_all_users_for_stack(request, stack_id):

    try:
        stack = KartenStack.objects.get(id=stack_id)
    except KartenStack.DoesNotExist:
        e = KartenStackDoesNotExist(stack_id)
        return e.http_response()
    users = stack.users.all()
    json_dict = to_json(users)

    return HttpResponse(pickler.encode(json_dict, unpicklable=False), content_type="application_json")



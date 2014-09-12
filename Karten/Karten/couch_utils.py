import couchdb
import random
import json

def create_couch_user(server, new_username, user_password):

    user_couchid = 'org.couchdb.user:%s' % new_username
    new_user_dict = {'_id' : user_couchid,
                     'name': new_username,
                     'roles' : [],
                     'type' : 'user',
                     'password' : user_password}
    users_resource = server.resource("_users")
    try:
        result = users_resource.put(path=user_couchid, body=json.dumps(new_user_dict))
        return result
    except couchdb.ResourceConflict:
        return None

def add_user_to_db(server, db_name, username):
    pass

def create_db_for_user(server, db_name, username):
    
    new_db = server.create(db_name)
    security_resource = new_db.resource("_security")

    permissions_dict = {'admins' :
                            {'names' : [],
                             'roles' : [],
                             },
                        'members' : {
                            'names' : [username],
                            'roles' : []
                            }
                        }

    result = security_resource.put(body=json.dumps(permissions_dict))
    return result

def change_user_password(server, username, new_password):

    delete_couch_user(server, username)
    create_couch_user(server, username, new_password)

def delete_couch_user(server, username):

    couch_user_id = "org.couchdb.user:%s" % username
    user_db = server['_users']
    user_doc = user_db.get(couch_user_id)
    if user_doc is not None:
        user_db.delete(user_doc)


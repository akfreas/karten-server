from django.test import TestCase, Client
from Karten.models import KartenUser
from Karten.settings import *
import json
import string
import random

def rnd():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(random.randrange(4, 12)))

class UserCreationTestCase(TestCase):

    def setUp(self):
        self.client = Client()

    def test_user_creation(self):
        data_dict = {'first_name' : 'Big', 'last_name' : 'Pig'}
        response = self.client.get("/user/create", data_dict)
        resp_json = json.loads(response.content)
        filtered_keys = [k for k in resp_json.keys() if k in data_dict.keys()]
        self.assertEqual(len(filtered_keys), len(data_dict.keys()))
        for key in filtered_keys:
            self.assertEqual(data_dict[key], resp_json[key])

        

    def test_add_users_and_user_list(self):
        user_dicts = {}
        for i in range(0, 100):
            user_dict = {'first_name' : "fnm" + rnd(), 
                'last_name' : "lnm" + rnd(),
                'external_service' : "exts" + rnd(),
                'external_user_id' : "extid" + rnd()
                }
            response = self.client.get("/user/create", user_dict)
            self.assertEqual(200, response.status_code)
            response_json = json.loads(response.content)
            user_dicts[response_json['id']] = user_dict
        
        user_list_response = json.loads(self.client.get("/users").content)
        for user in user_list_response:
            expected_user = user_dicts[user['id']]

            for key in expected_user.keys():
                self.assertEqual(expected_user[key], user[key], \
                        "value for key %s does not match in returned dict. %s != %s. ID: %i" % (key, expected_user, user_dict, user['id']))

        for user_id in user_dicts.keys():
            expected_user = user_dicts[user_id]
            response_json = json.loads(self.client.get("/user/%s" % user_id).content)
 
            for key in expected_user.keys():
                self.assertEqual(expected_user[key], response_json[key], \
                        "value for key %s does not match in returned dict from user get. %s != %s. ID: %i" % (key, expected_user, user_dict, user['id']))

    def test_user_update(self):
        user_dict = {'first_name' : "fnm" + rnd(), 
                'last_name' : "lnm" + rnd(),
                'external_service' : "exts" + rnd(),
                'external_user_id' : "extid" + rnd()
                }
        response = self.client.get("/user/create", user_dict)
        self.assertEqual(200, response.status_code)
        response_json = json.loads(response.content)
        user_dict['id'] = response_json['id']
        

        for key in ['first_name', 'last_name']:
            if key is 'id':
                continue
            new_value = rnd()
            update_dict = {key : new_value}
            url = "/user/%i/update" % user_dict['id']
            response = self.client.get(url, update_dict)
            response_json = json.loads(response.content)
            self.assertEqual(new_value, response_json[key])


class DatabaseTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.create_user()

    def create_user(self):
        user_dict = {'first_name' : "fnm" + rnd(), 
                'last_name' : "lnm" + rnd(),
                'external_service' : "exts" + rnd(),
                'external_user_id' : "extid" + rnd()
                }
        response = self.client.get("/user/create", user_dict)
        self.assertEqual(200, response.status_code)
        self.user_info = json.loads(response.content)

    def test_create_delete_database(self):
        
        database_data = {'name' : "test_" + rnd(), 
            'description' : "test db", 
            'owner' : self.user_info['id']}
        response = self.client.get("/database/create", database_data)
        new_db = json.loads(response.content)
        self.assertEqual(new_db['name'], database_data['name'])
        self.assertEqual(new_db['owner_id'], database_data['owner'])
        self.assertEqual(new_db['description'], database_data['description'])

        expected_db_url = COUCHDB_SERVERS['Karten'] + "/" + database_data['name']
        self.assertEqual(expected_db_url, new_db['couchdb_server']['server_url'] + "/" + new_db['name']) 

        json_response = json.loads(self.client.get("/database/%s/delete" % new_db['id']).content)
        self.assertEqual(json_response['couchdb_name'], new_db['couchdb_name'])


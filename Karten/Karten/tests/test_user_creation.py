from django.test import TestCase, Client
from Karten.models import KartenUser
from Karten.settings import *
from Karten.errors import *
import json
import string
import random

def rnd():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(random.randrange(4, 12)))

def write_json_data(test_name, json):
    json_file = open("Karten/tests/json-outputs/%s.json" % test_name, "w")
    json_file.write(json)
    json_file.close()

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

        
    def test_user_creation_error(self):
        data_dict = {'first_name' : 'Big', 'last_name' : 'Pig', 'external_user_id' : '1', 'external_service' : 'fb'}
        response = self.client.get("/user/create", data_dict)
        error_response = self.client.get("/user/create", data_dict)
        resp_json = json.loads(error_response.content)
        expected_error = KartenUserAlreadyExists(data_dict['external_user_id'])
        self.assertEqual(resp_json['error_code'], expected_error.error_code)
        self.assertEqual(resp_json['info']['message'], expected_error.message)

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
        users_response = self.client.get("/users") 
        user_list = json.loads(users_response.content)
        for user in user_list:
            expected_user = user_dicts[user['id']]

            for key in expected_user.keys():
                self.assertEqual(expected_user[key], user[key], \
                        "value for key %s does not match in returned dict. %s != %s. ID: %i" % (key, expected_user, user_dict, user['id']))

        write_json_data("UserListFetch", users_response.content)

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
        self.user_info = self.create_user()

    def create_user(self):
        user_dict = {'first_name' : "fnm" + rnd(), 
                'last_name' : "lnm" + rnd(),
                'external_service' : "exts" + rnd(),
                'external_user_id' : "extid" + rnd()
                }
        response = self.client.get("/user/create", user_dict)
        self.assertEqual(200, response.status_code)
        return json.loads(response.content)

    def database_data(self):
        database_data = {'name' : "test_" + rnd(), 
            'description' : "test db", 
            'owner' : self.user_info['id']}
        return database_data


    def test_get_user_stacks(self):
        user_dict = self.create_user();

        response_json = json.loads(self.client.get("/user/%s/stacks/all" % user_dict['id']).content)

        self.assertEqual(len(response_json), 0)

        database_data = self.database_data()

        database_response = self.client.get("/stack/create", database_data)
        new_db = json.loads(database_response.content)

    def test_create_delete_database(self):
        
        database_data = self.database_data()
        response = self.client.get("/stack/create", database_data)
        new_db = json.loads(response.content)
        self.assertEqual(new_db['name'], database_data['name'])
        self.assertEqual(new_db['owner_id'], database_data['owner'])
        self.assertEqual(new_db['description'], database_data['description'])

        expected_db_url = COUCHDB_SERVERS['Karten'] + "" + database_data['name']
        self.assertEqual(expected_db_url, new_db['couchdb_server']['server_url'] + "" + new_db['name']) 

        write_json_data("CreateDatabaseData", response.content)


        json_response = json.loads(self.client.get("/stack/%s/delete" % new_db['id']).content)
        self.assertEqual(json_response['couchdb_name'], new_db['couchdb_name'])

    def test_add_remove_user_to_database(self):
        database_data = self.database_data()
        response = self.client.get("/stack/create", database_data)
        new_db = json.loads(response.content)
        new_user = self.create_user()

        add_user_response = json.loads(self.client.get("/stack/%s/user/%s/add" % (new_db['id'], new_user['id'])).content)

        test_val = False
        for user in add_user_response['allowed_users']:
            if user['id'] is new_user['id']:
                test_val = True

        self.assertTrue(test_val)
        all_stacks = json.loads(self.client.get("/user/%s/stacks/all" % new_user['id']).content)
        self.assertTrue(len(all_stacks), 1)
        self.assertTrue(all_stacks[0]['name'], database_data['name'])
        self.assertTrue(all_stacks[0]['description'], database_data['description'])
        self.assertTrue(all_stacks[0]['owner']['id'], new_user['id'])

        delete_user_response = json.loads(self.client.get("/stack/%s/user/%s/delete" % (new_db['id'], new_user['id'])).content)

        test_val = True
        for user in delete_user_response['allowed_users']:
            if user['id'] is new_user['id']:
                test_val = False

        self.assertTrue(test_val)

        self.client.get("/stack/%s/delete" % new_db['id'])




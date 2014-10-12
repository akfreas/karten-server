from django.test import TestCase, Client
from Karten.models import KartenUser
from Karten.settings import *
from Karten.errors import *
from Karten.serializers import *
import json
import string
import random
from testutils import *

from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

def rnd():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(random.randrange(4, 12)))

def write_json_data(test_name, json):
    json_file = open("Karten/tests/json-outputs/%s.json" % test_name, "w")
    json_file.write(json)
    json_file.close()

class UserCreationTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        disconnect_couchdb_signals()

    def valid_user_dict(self):
        data_dict = {'first_name' : 'Big', 
                     'last_name' : 'Pig',
                     'username' : 'bigpig',
                     'password' : 'password',
                     'email' : 'big@pig.com'}
        return data_dict

    def test_user_creation(self):
        data_dict = self.valid_user_dict()
        response = self.client.post("/users/", data_dict)
        resp_json = json.loads(response.content)
        filtered_keys = [k for k in resp_json.keys() if k in data_dict.keys()]
        for key in filtered_keys:
            self.assertEqual(data_dict[key], resp_json[key])

        new_client = Client()
        new_client.login(username=data_dict['username'], password=data_dict['password'])
        self.assertIsNotNone(new_client.session.get('_auth_user_hash'))
        
    def test_user_creation_error(self):
        data_dict = {'first_name' : 'Big', 
                     'last_name' : 'Pig', 
                     'external_user_id' : '1', 
                     'external_service' : 'fb'}
        error_response = self.client.post("/users/", data_dict)
        missing_fields = ['username', 'email', 'password']
        resp_json = json.loads(error_response.content)
        self.assertEqual(len(missing_fields), len(resp_json))
        for error_field in resp_json.keys():
            self.assertTrue(error_field in missing_fields)

    def test_invalid_email(self):
        data_dict = self.valid_user_dict()
        data_dict['email'] = rnd()

        response = self.client.post('/users/', data_dict)
        errors = json.loads(response.content) 
        
        self.assertIsNotNone(errors['email']) 
        self.assertEqual(len(errors['email']), 1)
        self.assertEqual(len(errors.keys()), 1)

    def test_duplicate_email_and_username(self):
        data_dict = self.valid_user_dict()

        response1 = self.client.post('/users/', data_dict)
        response2 = self.client.post('/users/', data_dict)
        errors = json.loads(response2.content) 
        self.assertIsNotNone(errors['email']) 
        self.assertEqual(len(errors['email']), 1)

        self.assertIsNotNone(errors['username']) 
        self.assertEqual(len(errors['username']), 1)
        self.assertEqual(len(errors.keys()), 2)

    def test_user_list(self):
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, 404)

    def test_user_update(self):
        user = create_user(username=rnd(), password="password")

        user.first_name = rnd()
        user.save()
        serialized_user = KartenUserSerializer(user)
        new_client = Client()
        new_client.login(username=user.username, password="password")
        update_dict = {'first_name' : 'test111'}
        data = JSONRenderer().render(update_dict) 

        user_update = new_client.put("/users/me/", data) 
        self.assertEqual(user_update.status_code, 202)
        response = new_client.get("/users/me/")
        updated_user = response.data 
        self.assertEqual(update_dict['first_name'], updated_user['first_name'])
        

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

    def test_create_stack_with_duplicate_name(self):

        database_data = self.database_data()
        response_1 = self.client.get("/stack/create", database_data)
        new_db_1 = json.loads(response.content)
        response_2 = self.client.get("/stack/create", database_data)
        new_db_2 = json.loads(response.content)

        self.assertEqual(new_db_1['name'], new_db_2['name'])
        self.assertEqual(new_db_1['owner_id'], new_db_2['owner_id'])
        self.assertEqual(new_db_1['description'], new_db_2['description'])
        self.assertNotEqual(new_db_1['couchdb_server'], new_db_2['couchdb_server'])

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




from django.test import TestCase, Client
from Karten.models import *
from Karten.settings import *
from Karten.errors import *
import json
import string
import random
from datetime import datetime
from django.utils import timezone
from Karten.models import create_auth_token, update_couchdb_password
from Karten.tests.testutils import *
from rest_framework.authtoken.models import Token

test_username = "test11"
test_password = "password"

class FriendRequestTestCase(TestCase):

    def setUp(self):
        post_save.disconnect(create_auth_token, sender=KartenUser)
        post_save.disconnect(update_couchdb_password, sender=Token)
        self.client = Client()
        self.current_user = create_user(test_username, test_password)
        self.client.login(username=test_username, password=test_password)

        self.friends = create_dummy_users()

    def request_friends(self):

        first_friend = self.friends[0]
        request_dict = {'user_ids' : [f.id for f in self.friends]}
        response = self.client.post("/friends/requests/outgoing/", request_dict)
        self.assertEqual(response.status_code, 201)

    def remove_friend_requests(self):

        KartenUserFriendRequest.objects.all().delete()

    def test_add_friend(self):
        self.request_friends()
        for friend in self.friends:
            new_client = Client()
            new_client.login(username=friend.username, password="password")
            incoming_request = new_client.get("/friends/requests/incoming/")
            self.assertEqual(incoming_request.status_code, 200)
            requests = json.loads(incoming_request.content)
            self.assertEqual(len(requests), 1)
            matching_request = requests[0]
            self.assertIsNotNone(matching_request)
            self.assertEqual(matching_request['accepting_user'], friend.id)
            self.assertEqual(matching_request['accepted'], False)
            self.assertEqual(matching_request['requesting_user'], self.current_user.id)
        self.remove_friend_requests()

    def test_add_nonexistent_friend(self):
 
        request_dict = {'user_ids' : ''}
        response = self.client.post("/friends/requests/outgoing/", request_dict)
        self.assertEqual(response.status_code, 400)

    def test_add_friend_invalid_id(self):
 
        first_friend = self.friends[0]
        request_dict = {'user_ids' : [2323490, '999999']}
        response = self.client.post("/friends/requests/outgoing/", request_dict)
        no_friends = json.loads(response.content)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(no_friends), 0)

    def test_accept_friend_request_invalid_id(self):

        bad_request = self.client.post("/friends/requests/incoming/98089/accept/")
        self.assertEqual(bad_request.status_code, 404)

    def test_accept_friend_request(self):

        self.request_friends()

        for friend in self.friends[:5]:
            new_client = Client()
            new_client.login(username=friend.username, password="password")
            incoming_request = new_client.get("/friends/requests/incoming/")
            requests = json.loads(incoming_request.content)
            for request_id in [f['id'] for f in requests]:
                response = new_client.post("/friends/requests/incoming/%s/accept/" % request_id)
                self.assertEqual(response.status_code, 200)

            accepted_friends = json.loads(new_client.get("/friends/requests/incoming/").content)
            self.assertEqual(len(accepted_friends), 1)
            accepted_request = accepted_friends[0]
            self.assertEqual(accepted_request['accepted'], True)
            self.assertEqual(accepted_request['accepting_user'], friend.id)

        for i in range(len(self.friends)):
            user = self.friends[i]
            new_client = Client()
            new_client.login(username=user.username, password="password")

            user_friends = json.loads(new_client.get("/user/%s/friends/" % user.id).content)

            if i < 5:
                self.assertEqual(len(user_friends), 1)
                self.assertEqual(user_friends[0]['username'], test_username)
            else:
                self.assertEqual(len(user_friends), 0)



    def test_deny_friend_request(self):

        self.request_friends()

        for friend in self.friends[:5]:
            new_client = Client()
            new_client.login(username=friend.username, password="password")
            incoming_request = new_client.get("/friends/requests/incoming/")
            requests = json.loads(incoming_request.content)
            for request_id in [f['id'] for f in requests]:
                response = new_client.post("/friends/requests/incoming/%s/deny/" % request_id)
                self.assertEqual(response.status_code, 200)

            accepted_friends = json.loads(new_client.get("/friends/requests/incoming/").content)
            self.assertEqual(len(accepted_friends), 1)
            accepted_request = accepted_friends[0]
            self.assertEqual(accepted_request['accepted'], False)
            self.assertEqual(accepted_request['accepting_user'], friend.id)

        for i in range(len(self.friends)):
            user = self.friends[i]
            new_client = Client()
            new_client.login(username=user.username, password="password")

            user_friends = json.loads(new_client.get("/user/%s/friends/" % user.id).content)
            self.assertEqual(len(user_friends), 0)


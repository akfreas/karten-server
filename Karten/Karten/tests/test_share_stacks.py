from django.test import TestCase, Client
from Karten.models import *
from Karten.settings import *
from Karten.errors import *
import json
import string
import random
from datetime import datetime
from django.utils import timezone
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token

from Karten.tests.testutils import *


class UserShareStackTestCase(TestCase):

    def setUp(self):
        disconnect_couchdb_signals()
        self.owner = create_user("test_user", "password")
        server = KartenCouchServer(host="localhost", port=99, protocol="https")
        server.save()
        stack = KartenStack(couchdb_name="test1",
                                 couchdb_server=server,
                                 owner=self.owner,
                                 name="test1",
                                 creation_date=timezone.now())
        stack.save()
        self.stack = stack
        self.client = Client()
        self.client.login(username=self.owner.username, password="password")

    def test_share_stack(self):
    
        share_users = create_dummy_users(count=10)
        user_ids = [u.id for u in share_users]
        share_user_dict = {'user_ids' : user_ids}
        share_response = self.client.post("/stacks/%s/share/" % self.stack.id, share_user_dict)
        self.assertEqual(share_response.status_code, 201)

        stack = json.loads(self.client.get("/stacks/%s/" % self.stack.id).content)
        allowed_users = stack['allowed_users']
        is_true = [x for x in user_ids if x in allowed_users]
        is_true += [self.stack.owner.id]

        self.assertEqual(len(allowed_users), len(is_true))
        
    def test_unshare_stack(self):

        share_users = create_dummy_users(count=10)
        user_ids = [u.id for u in share_users]
        share_user_dict = {'user_ids' : user_ids}
        share_response = self.client.post("/stacks/%s/share/" % self.stack.id, share_user_dict)
        self.assertEqual(share_response.status_code, 201)
        subtracted_users = user_ids[::5]
        unshare_user_dict = {"user_ids" : subtracted_users}
        unshare_response = self.client.delete("/stacks/%s/share/" % self.stack.id, json.dumps(unshare_user_dict), content_type="application/json")

        self.assertEqual(unshare_response.status_code, 200)

        unsubtracted_users = [u for u in user_ids if u not in subtracted_users]
        unsubtracted_users += [self.owner.id]
        unsubtracted_users.sort()
        users_from_response = json.loads(unshare_response.data)
        users_from_response.sort()

        self.assertEqual(len(unsubtracted_users), len(users_from_response))

        for i in range(len(unsubtracted_users)):
            user1 = unsubtracted_users[i]
            user2 = users_from_response[i]
            self.assertEqual(user1, user2)
        


        


        
         






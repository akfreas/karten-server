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

class UserSearchTestCase(TestCase):

    def setUp(self):
        disconnect_couchdb_signals()
        self.users = create_dummy_users(username_prefix="aaa")
        create_dummy_users(username_prefix="bbb")
        self.client = Client()

    def test_user_search(self):

        users = json.loads(self.client.get('/users/search/', {'q' : 'aaa'}).content)
        self.assertEqual(len(users), len(self.users))

    def test_search_blank_query(self):
        response = self.client.get('/users/search/')
        self.assertEqual(response.status_code, 400)


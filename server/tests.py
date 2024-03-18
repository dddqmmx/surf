import uuid

from django.test import TestCase
from server.models import User


class UserTestCase(TestCase):
    def setUp(self):
        pass

    def test_animals_can_speak(self):
        public_key = '123'
        if User.objects.filter(public_key=uuid):
            print("to login")
        else:
            User.objects.create(uuid=uuid.uuid4(), public_key=public_key)
            print('to init user info')
            print(User.objects.all())
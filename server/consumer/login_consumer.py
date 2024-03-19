import base64
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from cryptography.hazmat.primitives import serialization

from util.PgModel import PgModel
from util.creat_ras_key import generate_key_pair
from util.encryption.encryption_ras import decrypt_data, encrypt_data
from util.session.session_util import Session


class LoginConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.public_key = None
        self.pg = PgModel()

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        receiveJson = json.loads(text_data)
        command = receiveJson['command']
        if 'login' == command:
            session_id = receiveJson['session_id']
            print(session_id)
            print(Session.get_session_by_id(session_id))
            session = Session.get_session_by_id(session_id);
            if session:
                public_key = session.get('client_public_key')
                sql = "select count(1) from public.user where public_key = %s"
                res = self.pg.query(sql, (public_key,))
                print(res)
                if len(res) > 0:
                    requestJson = {
                        'command': 'to_url',
                        'url': 'chat'
                    }
                    await self.send(json.dumps(requestJson))
                else:
                    filters = {
                        "public_key": public_key
                    }
                    self.pg.save('public.user', filters, primary='uuid')
                    requestJson = {
                        'command': 'to_url',
                        'url': 'chat'
                    }
                    await self.send(json.dumps(requestJson))
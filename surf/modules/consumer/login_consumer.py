import base64
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from cryptography.hazmat.primitives import serialization

from surf.modules.util import Pg
# from surf.modules.util import generate_key_pair
# from surf.modules.util import decrypt_data, encrypt_data
from surf.modules.util import Session


class LoginConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.public_key = None
        self.pg = Pg()

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        receiveJson = json.loads(text_data)
        command = receiveJson['command']
        if 'login' == command:
            session_id = receiveJson['session_id']
            session = Session.get_session_by_id(session_id)
            if session:
                public_key = session.get('client_public_key')
                sql = "select * from public.user where public_key = %s"
                res = self.pg.query(sql, (public_key,))
                if len(res) > 0:
                    print(1)

                else:
                    print(2)
                    filters = {
                        "public_key": public_key
                    }
                    self.pg.save('public.user', filters, primary='uuid')
                print(res[0]['uuid'])
                session.set('uuid', res[0]['uuid'])
                requestJson = {
                    'command': 'to_url',
                    'url': 'main'
                }
                await self.send(json.dumps(requestJson))
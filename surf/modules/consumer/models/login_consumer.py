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

    async def receive(self, text_data=None, bytes_data=None):
        receiveJson = json.loads(text_data)
        command = receiveJson['command']
        if 'login' == command:
            session_id = receiveJson['session_id']
            session = Session.get_session_by_id(session_id)
            if session:
                public_key = session.get('client_public_key')
                sql = "SELECT c_user_id as id FROM public.t_users WHERE c_public_key = %s"
                res = self.pg.query(sql, [public_key])
                if len(res) > 0:
                    print(1)
                    user_id = res[0]['id']
                else:
                    print(2)
                    filters = {
                        "c_public_key": public_key
                    }
                    user_id = self.pg.save('public.t_users', filters, return_id=True, return_id_clumn="c_user_id")
                print(user_id)
                if user_id is not False:
                    session.set('user_uuid', user_id)
                    requestJson = {
                        'command': 'to_url',
                        'url': 'main'
                    }
                    await self.send(json.dumps(requestJson))
                else:
                    print("登录你麻痹")

import base64
import json
import traceback

from channels.generic.websocket import AsyncWebsocketConsumer

from surf.modules.consumer.services import UserService


class UserConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.public_key = None
        self.service = UserService()
        # self.func_dict = {
        #     'login': self.login
        # }

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        receive_json = json.loads(text_data)
        command = receive_json['command']
        session_id = receive_json['session_id']
        if 'login' == command:
            await self.login(session_id)

    async def login(self, session_id):
        request_json = self.service.login(session_id)
        if request_json is not False:
            await self.send(json.dumps(request_json))
        else:
            print("登录失败")

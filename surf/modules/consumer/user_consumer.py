import base64
import json
import traceback

from channels.generic.websocket import AsyncWebsocketConsumer

from surf.modules.consumer.services import UserService


class UserConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.public_key = None
        self.user_service = UserService()
        self.func_dict = {
            'login': self.login,
            'get_user_data': self.get_user_data
        }

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        receive_json = json.loads(text_data)
        command = receive_json['command']
        session_id = receive_json['session_id']
        if command in self.func_dict.keys():
            await self.func_dict.get(command)(str(session_id))

    async def login(self, session_id: str):
        respond_json = self.user_service.login(session_id)
        if respond_json is not False:
            await self.send(json.dumps(respond_json))
        else:
            print("登录失败")

    async def get_user_data(self, session_id: str):
        respond_json = self.user_service.get_user_data(session_id)
        if respond_json is not False:
            await self.send(json.dumps(respond_json))
        else:
            print("获取失败")

import json

from surf.modules.consumer.services import UserService
from surf.modules.util import BaseConsumer


class UserConsumer(BaseConsumer):
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
        text_data = json.loads(text_data)
        command = text_data['command']
        if command in self.func_dict.keys():
            await self.func_dict.get(command)(text_data)

    async def login(self, text_data):
        respond_json = self.user_service.login(text_data['session_id'])
        if respond_json is not False:
            await self.send(json.dumps(respond_json))
        else:
            print("登录失败")

    async def get_user_data(self, session_id: str):
        respond_json = self.user_service.get_user_data(session_id)
    async def get_user_data(self, text_data):
        respond_json = self.user_service.get_user_data(text_data['session_id'])
    async def search_user(self, text_data):
        respond_json = self.user_service.search_user(text_data['user_id_list'])
        if respond_json is not False:
            await self.send(json.dumps(respond_json))
        else:
            print("获取失败")

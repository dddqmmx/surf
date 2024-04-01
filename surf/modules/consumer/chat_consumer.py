import json

from channels.generic.websocket import AsyncWebsocketConsumer

from surf.modules.util import Pg
from surf.modules.util import Ec


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.public_key = None
        self.pg = Pg()
        self.ec = Ec()


    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        receiveJson = json.loads(text_data)
        command = receiveJson['command']
        if 'get_message' == command:
            index_name = 'message'
            search_body = {
                'query': {
                    'match_all': {}
                }
            }
            search_response = self.ec.search(index_name, search_body)
            print(search_response)
        if 'send_message' == command:
            pass
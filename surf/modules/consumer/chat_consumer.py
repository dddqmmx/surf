import json

from channels.generic.websocket import AsyncWebsocketConsumer

from surf.modules.util import Pg


class ChatConsumer(AsyncWebsocketConsumer):
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
        if 'send_message' == command:
            pass
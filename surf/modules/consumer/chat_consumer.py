from channels.generic.websocket import AsyncWebsocketConsumer

from surf.modules.util import PgModel
from surf.modules.util import generate_key_pair


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.public_key = None
        self.pg = PgModel()

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        pass
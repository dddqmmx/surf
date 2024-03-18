import json

from channels.generic.websocket import AsyncWebsocketConsumer
from cryptography.hazmat.primitives import serialization

from util.encryption.encryption_ras import generate_key_pair


class InitConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.private_key = None
        self.public_key = None

    async def connect(self):
        await self.accept()
        self.private_key, self.public_key = generate_key_pair()  # 将private_key保存为self.private_key
        serialized_public_key = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        initJson = {
            'command': 'init',
            'public_key': serialized_public_key.decode('utf-8')
        }
        await self.send(text_data=json.dumps(initJson))

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        pass

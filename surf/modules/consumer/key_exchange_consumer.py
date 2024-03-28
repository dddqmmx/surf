import json

from channels.generic.websocket import AsyncWebsocketConsumer
from cryptography.hazmat.primitives import serialization

from surf.modules.encryption.encryption_ras import generate_key_pair
from surf.modules.util import Session


class KeyExchangeConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.private_key = None
        self.public_key = None

    async def connect(self):
        await self.accept()


    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        receiveJson = json.loads(text_data)
        command = receiveJson['command']
        if command == 'key_exchange':
            self.private_key, self.public_key = generate_key_pair()  # 将private_key保存为self.private_key
            serialized_public_key = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            session = Session.create_session()
            session.set('client_public_key', receiveJson['public_key'])
            initJson = {
                'command': 'key_exchange',
                'public_key': serialized_public_key.decode('utf-8'),
                'session_id': session.session_id
            }
            await self.send(text_data=json.dumps(initJson))

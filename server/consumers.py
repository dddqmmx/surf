# yourapp/consumers.py
import base64
import json
import uuid

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from cryptography.hazmat.primitives import serialization

from server.models import User
from util.encryption.encryption_ras import generate_key_pair, decrypt_data, encrypt_with_serialized_public_key, \
    encrypt_data
from server.PgModel import PgModel


class LoginConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.public_key = None
        self.pg = PgModel()

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
        decrypted_chunks = []
        encrypted_chunks = text_data.split(' ')
        for chunk in encrypted_chunks:
            decoded_bytes = base64.b64decode(chunk)
            decrypted_message = decrypt_data(decoded_bytes, self.private_key)
            decrypted_chunks.append(decrypted_message)
        decrypted_data = ''.join(decrypted_chunks)
        receiveJson = json.loads(decrypted_data)
        command = receiveJson['command']
        if 'login' == command:
            public_key = receiveJson['public_key']
            print(public_key)
            sql = "select count(1) from public.user where public_key = %s"
            res = self.pg.query(sql, (public_key,))
            print(res)
            if len(res) > 0:
                await self.send(encrypt_data('123中文', base64.b64decode(public_key).decode('utf-8')))
            else:
                filters = {
                    "public_key": public_key
                }
                self.pg.save('public.user', filters, primary='uuid')



class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.private_key = None
        self.public_key = None

    async def connect(self):
        await self.accept()


    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        pass

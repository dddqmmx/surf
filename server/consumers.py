# yourapp/consumers.py
import base64
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from cryptography.hazmat.primitives import serialization

from util.encryption.encryption_ras import generate_key_pair, decrypt_data, encrypt_data
from util.PgModel import PgModel


# class ChatConsumer(AsyncWebsocketConsumer):
#     def __init__(self, *args, **kwargs):
#         super().__init__(args, kwargs)
#         self.private_key = None
#         self.public_key = None
#
#     async def connect(self):
#         await self.accept()
#
#
#     async def disconnect(self, close_code):
#         pass
#
#     async def receive(self, text_data):
#         pass

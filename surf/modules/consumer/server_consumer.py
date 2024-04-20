# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius(fuzequan)
Created Time    : 2024/4/18 18:23
File Name       : server_consumer.py
Last Edit Time  : 
"""
import json

from .services import ServerService
from surf.modules.util import BaseConsumer


class ServerConsumer(BaseConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.server_service = ServerService()
        self.func_dict = {
            "create_server": self.create_server
        }

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        text_data = json.loads(text_data)
        if text_data and text_data["command"]:
            await self.func_dict.get(text_data["command"])(text_data)
        pass

    async def create_server(self, text_data):
        if text_data:
            respond_json = self.server_service.create_server(text_data)
            await self.send(respond_json)

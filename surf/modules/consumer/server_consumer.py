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
            "create_server": self.create_server,
            "create_channel_group": self.create_channel_group,
            "create_channel": self.create_channel,
            "get_server_details": self.get_server_details
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
        respond_json = self.server_service.create_server(text_data)
        await self.send(respond_json)

    async def create_channel_group(self, text_data):
        respond_json = self.server_service.create_channel_group(text_data)
        await self.send(respond_json)

    async def create_channel(self, text_data):
        respond_json = self.server_service.create_channel(text_data)
        await self.send(respond_json)

    async def get_server_details(self, text_data):
        respond_json = self.server_service.get_server_details(text_data)
        await self.send(respond_json)

    async def add_server_member(self, text_data):
        respond_json = self.server_service.add_server_member(text_data)
        await self.send(respond_json)

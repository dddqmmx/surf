# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius(fuzequan)
Created Time    : 2024/4/18 18:23
File Name       : server_consumer.py
Last Edit Time  : 
"""

from services import ServerService
from surf.modules.consumer import BaseConsumer


class ServerConsumer(BaseConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.server_service = ServerService()

    async def connect(self):
        pass

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        pass

    async def create_server(self, text_data):
        if text_data:
            filters = text_data["server_filter"]
            res = self.server_service.create_server(filters)
            if res:
                print("成功")
            else:
                print("失败")
        else:
            print("创建失败")
        pass

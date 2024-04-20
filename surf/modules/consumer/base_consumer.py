# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius(fuzequan)
Created Time    : 2024/4/18 18:26
File Name       : base_consumer.py
Last Edit Time  : 
"""
import abc
from abc import abstractmethod, ABCMeta

from channels.generic.websocket import AsyncWebsocketConsumer


class BaseConsumer(AsyncWebsocketConsumer, metaclass=ABCMeta):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @abstractmethod
    async def connect(self):
        await self.accept()

    @abstractmethod
    async def disconnect(self, close_code):
        pass

    @abstractmethod
    async def receive(self, text_data=None, bytes_data=None):
        pass

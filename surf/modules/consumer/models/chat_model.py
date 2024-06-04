# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius(fuzequan)
Created Time    : 2024/6/4 17:10
File Name       : chat_model.py
Last Edit Time  : 
"""
from surf.modules.util import BaseModel


class ChatModel(BaseModel):
    def __init__(self):
        super().__init__()

    def send_chat(self, filters):
        return self._pg.save("c_channel_chats", filters, return_id=True, return_id_clumn="c_chat_id")

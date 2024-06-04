# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius(fuzequan)
Created Time    : 2024/6/4 17:10
File Name       : chat_model.py
Last Edit Time  : 
"""
import traceback

from surf.appsGlobal import logger
from surf.modules.util import BaseModel


class ChatModel(BaseModel):
    def __init__(self):
        super().__init__()

    def send_chat(self, filters):
        return self._pg.save("c_channel_chats", filters, return_id=True, return_id_clumn="c_chat_id")

    def is_revoked(self, chat_id):
        flag = False
        try:
            sql = """
            SELECT c_status as status FROM t_channel_chats WHERE c_chat_id = %s
            """
            flag = True if self._pg.query(sql, [chat_id])[0]['status'] else flag
        except Exception as e:
            logger.error(f"""{e}\n{traceback.format_exc()}""")
        finally:
            return flag

    def revoke_message(self, filters):
        return self._pg.save("c_channel_chats",
                             filters,
                             primary="c_chat_id",
                             return_id=True,
                             return_id_clumn="c_chat_id")

# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius(fuzequan)
Created Time    : 2024/4/28 16:13
File Name       : userpool.py
Last Edit Time  : 
"""
import asyncio
import datetime
import json
from typing import Union, Tuple, Dict
from .session_util import Session
from .surf_user import SurfUser
from surf.appsGlobal import logger, get_logger, setResult, errorResult

con_log = get_logger('connections')


class UserPool(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(UserPool, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.__connected_user: Dict[str, SurfUser] = {}
            self.__broadcast_map: Dict[str, Dict[str, SurfUser]] = {}
            self.lock = asyncio.Lock()
            self._initialized = True
            con_log.info(f'UserPool initialized:{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

    def get_users(self):
        return self.__connected_user.copy()

    def get_broadcast_by_channel_id(self, channel_id):
        return self.__broadcast_map.copy()[channel_id]

    def connect_user_to_pool(self, session, user) -> bool:
        session_id = session.session_id
        if self.__connected_user.get(session_id, None):
            con_log.info(f"session_id:{session_id} has already logged in, user\'s info might be infiltrated")
            return False
        else:
            for k, user in self.get_users().items():
                if user.check_user_id_by_session_id(session_id):
                    con_log.info(
                        f"session_id:{session_id}'s bound user_id has logged in already"
                        f", user\'s info might be infiltrated")
                    return False
            self.__connected_user[session_id] = user
            return True

    def access_new_user(self, session, consumer, return_id=False) -> Union[bool, Tuple[bool, str]]:
        user_id = session.get('user_id')
        surf_user = SurfUser(user_id, consumer)
        flag = self.connect_user_to_pool(session, surf_user)
        if return_id:
            return flag, session.session_id
        return flag

    def broadcast_to_all_user_in_channel(self, text_data):
        channel_id = text_data['channel_id']
        for k, user in self.get_broadcast_by_channel_id(channel_id).items():
            user.broadcast(text_data)

    def detach_user_from_pool_by_session_id(self, session_id):
        del self.__connected_user[session_id]
        con_log.info(f'session_id:{session_id} has disconnect from surf')


def session_check(func):
    async def wrapper(*args, **kwargs):
        flag = False
        session_id = None
        text_data = json.loads(kwargs['text_data'])
        if text_data['command'] != 'login' and text_data != 'key_exchange':
            session_id = text_data.get('session_id', None)
            if session_id:
                for k, user in UserPool().get_users():
                    if user.check_user_id_by_session_id(session_id) and session_id == args[0].session_id:
                        flag = True
                        break
        else:
            flag = True
        if flag:
            return await func(*args, **kwargs)
        else:
            logger.error(text_data)
            logger.error(f"发现无效session进行操作：{session_id}， 已拦截")
            await args[0].send(errorResult(text_data['command'], '无效session', text_data['path']))
    return wrapper

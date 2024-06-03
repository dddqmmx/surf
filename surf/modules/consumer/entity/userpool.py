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
import threading
import traceback
from typing import *
from surf.appsGlobal import logger, get_logger, setResult, errorResult
from surf.modules.util.session_util import Session
from .surf_user import SurfUser
from .surf_channel import SurfChannel
from surf.modules.consumer.services import UserService, ServerService

con_log = get_logger('connections')


class UserPool(object):
    _instance = None
    _lock = threading.Lock()  # 类级别的锁，用于线程安全

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(UserPool, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.__connected_user: Dict[str, SurfUser] = {}
            self.__broadcast_map: Dict[str, Dict[str, SurfChannel]] = {}
            self.lock = asyncio.Lock()
            self._initialized = True
            self.__user_service = UserService()
            self.__server_service = ServerService()
            con_log.info(f'UserPool initialized:{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

    def get_users(self):
        return self.__connected_user.copy()

    def get_user_by_session_id(self, session_id):
        return self.__connected_user.get(session_id, None)

    def get_broadcast_by_server_id(self, server_id):
        return self.__broadcast_map.copy().get(server_id, {})

    async def connect_user_to_pool(self, session, user):
        async with self.lock:
            session_id = session.session_id
            if self.__connected_user.get(session_id, None):
                con_log.info(f"session_id:{session_id} has already logged in, user\'s info might be infiltrated")
                return False
            for k, exist_user in self.get_users().items():
                if exist_user.check_user_id_by_session_id(session_id):
                    con_log.info(
                        f"session_id:{session_id}'s bound user_id has logged in already"
                        f", user\'s info might be infiltrated")
                    return False
            self.__connected_user[session_id] = user
            return True

    async def init_new_user(self, session, consumer, return_id=False):
        user_id = session.get('user_id')
        user_name = session.get('user_name')
        surf_user = SurfUser(user_id, consumer, user_name)
        flag = await self.connect_user_to_pool(session, surf_user)
        if flag:
            await self.init_users_broadcast_map(session, surf_user)
        if return_id:
            return flag, session.session_id
        return flag

    async def add_user_to_channel(self, session_id, channel_id):
        user = self.get_users().get(session_id, None)
        try:
            if user:
                server_id = self.__server_service.get_server_by_channel_id(channel_id)
                await self.__broadcast_map[server_id][channel_id].add_user(user)
                return True
        except Exception as e:
            logger.error(f"添加用户:{user.user_name} 到频道：{channel_id}失败:{e}\n{traceback.format_exc()}")
        return False

    async def remove_user_from_channel(self, session_id, channel_id):
        user = self.get_users().get(session_id, None)
        try:
            if user:
                server_id = self.__server_service.get_server_by_channel_id(channel_id)
                await self.__broadcast_map[server_id][channel_id].remove_user(user)
                return True
        except Exception as e:
            logger.error(f"从频道：{channel_id} 移除用户:{user.user_name} 失败:{e}\n{traceback.format_exc()}")
        return False

    async def broadcast_to_all_user_in_channel(self, text_data):
        if text_data.get('is_audio', False):
            channel_id = text_data['channel_id']
            server_id = self.__server_service.get_server_by_channel_id(channel_id)
            user_list = self.get_broadcast_by_server_id(server_id).get(channel_id, [])
            tasks = []
            for user in user_list:
                if user.check_user_id_by_session_id(text_data['session_id']):
                    continue
                tasks.append(user.broadcast(json.dumps(text_data)))
        else:
            channel_id = text_data['messages']['channel_id']
            server_id = self.__server_service.get_server_by_channel_id(channel_id)
            user_list = self.get_broadcast_by_server_id(server_id).get(channel_id, [])
            tasks = [user.broadcast(json.dumps(text_data)) for user in user_list]
        await asyncio.gather(*tasks)
        logger.info(f'broadcast to all user in channel:{channel_id} done, total:{len(tasks)}')

    async def init_users_broadcast_map(self, session: Session, surf_user):
        user_id = session.get('user_id')
        ids = self.__server_service.get_channels_by_user_id(user_id)
        if ids is not False:
            async with self.lock:
                for channel_id in ids:
                    server_id = self.__server_service.get_server_by_channel_id(channel_id['id'])
                    if not self.__broadcast_map.get(server_id, None):
                        self.__broadcast_map[server_id] = {}
                    channel = self.__server_service.get_channel_details_by_channel_id(channel_id['id'])
                    if not self.__broadcast_map[server_id].get(channel_id['id'], None):
                        self.__broadcast_map[server_id][channel_id['id']] = SurfChannel(
                            channel_id['id'],
                            True if channel[0]['type'] == "voice" else False,
                            int(channel[0]['max_members'])
                        )
                    if channel[0]['type'] == "text":
                        await self.__broadcast_map[server_id][channel_id['id']].add_user(surf_user)
                    logger.info(
                        f"add userid:{user_id} to channel:{channel_id} done, "
                        f"current user in channel: {self.__broadcast_map[server_id][channel_id['id']].size()}")

    async def detach_user_from_pool_by_session_id(self, session_id):
        async with self.lock:
            user_id = Session.get_session_by_id(session_id).get('user_id')
            ids = self.__server_service.get_channels_by_user_id(user_id)
            if ids is not False:
                for channel_id in ids:
                    server_id = self.__server_service.get_server_by_channel_id(channel_id['id'])
                    await self.__broadcast_map[server_id][channel_id['id']].remove_user(user_id)
                    logger.info(
                        f"remove userid:{user_id} to channel:{channel_id} done, current user in channel: {self.__broadcast_map[server_id][channel_id['id']].size()}")
        del self.__connected_user[session_id]
        con_log.info(f'session_id:{session_id} has disconnect from surf, current online: {len(self.__connected_user)}')

    def check_online(self, session_id: str) -> bool:
        return self.get_users().get(session_id, False)

    async def connect_user_to_single_channel_by_id(self, session_id, channel_id: str) -> Tuple[bool, str]:
        user: SurfUser = self.get_users()[session_id]
        server_id = self.__server_service.get_server_by_channel_id(channel_id)
        flag, rtn_str = await self.__broadcast_map[server_id][channel_id].add_user(user)
        return flag, rtn_str

    async def remove_user_from_single_channel_by_id(self, session_id, channel_id: str) -> bool:
        user: SurfUser = self.get_users()[session_id]
        server_id = self.__server_service.get_server_by_channel_id(channel_id)
        flag = await self.__broadcast_map[server_id][channel_id].remove_user(user)
        return flag

    def get_channel_users(self, channel_id: str) -> List[Dict[str, str]]:
        user_list = []
        server_id = self.__server_service.get_server_by_channel_id(channel_id)
        for user in self.__broadcast_map[server_id][channel_id].get_users_in_channel():
            user_list.append(user.get_user_data())
        return user_list


def session_check(func):
    async def wrapper(*args, **kwargs):
        flag = False
        up = UserPool()
        text_data = json.loads(kwargs['text_data'])
        session_id = text_data.get('session_id', None)
        error_str = ""
        rtn_str = ""

        if text_data['command'] != 'login' and text_data['command'] != 'key_exchange':
            if session_id:
                user = up.get_user_by_session_id(session_id)
                session = Session.get_session_by_id(session_id)
                if user and user.check_user_id(session.get('user_id')) and session_id == args[0].session_id:
                    flag = up.check_online(session_id)
                    if not flag:
                        error_str = "用户已离线，无法操作"
                        rtn_str = "已离线"
                else:
                    error_str = f"发现无效session进行操作：{session_id}， 已拦截"
                    rtn_str = "无效session"
        else:
            flag = True

        if flag:
            return await func(*args, **kwargs)
        else:
            logger.error(text_data)
            logger.error(error_str)
            await args[0].send(errorResult(text_data['command'], rtn_str, text_data['path']))

    return wrapper


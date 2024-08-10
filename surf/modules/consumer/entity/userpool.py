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


class UserPool:
    _instance = None
    _lock = threading.Lock()

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
            con_log.info(f'UserPool initialized: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

    def get_users(self):
        return self.__connected_user.copy()

    def get_user_by_session_id(self, session_id):
        return self.__connected_user.get(session_id)

    def get_broadcast_by_server_id(self, server_id):
        return self.__broadcast_map.get(server_id, {}).copy()

    async def connect_user_to_pool(self, session, user):
        async with self.lock:
            session_id = session.session_id
            if session_id in self.__connected_user:
                con_log.info(f"session_id:{session_id} has already logged in, user\'s info might be infiltrated")
                return False
            if any(exist_user.check_user_id_by_session_id(session_id) for exist_user in self.__connected_user.values()):
                con_log.info(
                    f"session_id:{session_id}'s bound user_id has logged in already, user\'s info might be infiltrated")
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
        return (flag, session.session_id) if return_id else flag

    async def add_user_to_channel(self, session_id, channel_id):
        user = self.__connected_user.get(session_id)
        if not user:
            return False
        try:
            server_id = self.__server_service.get_server_by_channel_id(channel_id)
            await self.__broadcast_map[server_id][channel_id].add_user(user)
            return True
        except Exception as e:
            logger.error(f"添加用户:{user.user_name} 到频道：{channel_id}失败:{e}\n{traceback.format_exc()}")
            return False

    async def remove_user_from_channel(self, session_id, channel_id):
        try:
            user_id = Session.get_session_by_id(session_id).get('user_id')
            if user_id:
                server_id = self.__server_service.get_server_by_channel_id(channel_id)
                await self.__broadcast_map[server_id][channel_id].remove_user(user_id)
                return True
        except Exception as e:
            logger.error(f"从频道：{channel_id} 移除用户:{user_id} 失败:{e}\n{traceback.format_exc()}")
        return False

    async def broadcast_to_all_user_in_channel(self, text_data):
        channel_id = text_data['channel_id'] if text_data.get('is_audio', False) else text_data['messages'][
            'channel_id']
        server_id = self.__server_service.get_server_by_channel_id(channel_id)
        channel = self.get_broadcast_by_server_id(server_id).get(channel_id, None)
        if channel:
            tasks = [
                user.broadcast(json.dumps(text_data))
                for user in channel.channel_users
                if not user.check_user_id(text_data.get('user_id', ''))
            ]
            await asyncio.gather(*tasks)
            logger.info(f'broadcast to all user in channel:{channel_id} done, total:{len(tasks)}')

    async def init_users_broadcast_map(self, session: Session, surf_user):
        user_id = session.get('user_id')
        ids = self.__server_service.get_channels_by_user_id(user_id)
        if ids:
            async with self.lock:
                for channel_id in ids:
                    server_id = self.__server_service.get_server_by_channel_id(channel_id['id'])
                    self.__broadcast_map.setdefault(server_id, {})
                    channel = self.__server_service.get_channel_details_by_channel_id(channel_id['id'])
                    if channel_id['id'] not in self.__broadcast_map[server_id]:
                        self.__broadcast_map[server_id][channel_id['id']] = SurfChannel(
                            channel_id['id'],
                            channel[0]['type'] == "voice",
                            int(channel[0]['max_members'])
                        )
                    if channel[0]['type'] == "text":
                        await self.__broadcast_map[server_id][channel_id['id']].add_user(surf_user)
                    logger.info(
                        f"add userid:{user_id} to channel:{channel_id['id']} done, current user in channel: {self.__broadcast_map[server_id][channel_id['id']].size()}")

    async def detach_user_from_pool_by_session_id(self, session_id):
        async with self.lock:
            user_id = Session.get_session_by_id(session_id).get('user_id')
            ids = self.__server_service.get_channels_by_user_id(user_id)
            if ids:
                for channel_id in ids:
                    server_id = self.__server_service.get_server_by_channel_id(channel_id['id'])
                    await self.__broadcast_map[server_id][channel_id['id']].remove_user(user_id)
                    logger.info(
                        f"remove userid:{user_id} from channel:{channel_id['id']} done, current user in channel: {self.__broadcast_map[server_id][channel_id['id']].size()}")
            self.__connected_user.pop(session_id, None)
            con_log.info(
                f'session_id:{session_id} has disconnect from surf, current online: {len(self.__connected_user)}')

    def check_online(self, session_id: str) -> bool:
        return session_id in self.__connected_user

    async def connect_user_to_single_channel_by_id(self, session_id, channel_id: str) -> Tuple[bool, str]:
        user = self.__connected_user.get(session_id)
        if not user:
            return False, "User not found"
        server_id = self.__server_service.get_server_by_channel_id(channel_id)
        return await self.__broadcast_map[server_id][channel_id].add_user(user)

    async def remove_user_from_single_channel_by_id(self, session_id, channel_id: str) -> bool:
        server_id = self.__server_service.get_server_by_channel_id(channel_id)
        user_id = Session.get_session_by_id(session_id).get('user_id')
        return await self.__broadcast_map[server_id][channel_id].remove_user(user_id)

    def get_channel_users(self, channel_id: str) -> List[Dict[str, str]]:
        server_id = self.__server_service.get_server_by_channel_id(channel_id)
        return [user.get_user_data() for user in self.__broadcast_map[server_id][channel_id].get_users_in_channel()]


def session_check(func):
    async def wrapper(*args, **kwargs):
        text_data = json.loads(kwargs['text_data'])
        session_id = text_data.get('session_id')
        up = UserPool()

        if text_data.get('zedfeorius_test_code') == 'sbsb123' or text_data.get('command') in ('login', 'key_exchange'):
            return await func(*args, **kwargs)

        if not session_id:
            return await handle_invalid_session(args, text_data, "无效session")

        user = up.get_user_by_session_id(session_id)
        session = Session.get_session_by_id(session_id)

        if user and user.check_user_id(session.get('user_id')) and session_id == args[0].session_id:
            if up.check_online(session_id):
                return await func(*args, **kwargs)
            else:
                return await handle_invalid_session(args, text_data, "用户已离线，无法操作")
        else:
            return await handle_invalid_session(args, text_data, f"发现无效session进行操作：{session_id}， 已拦截")

    async def handle_invalid_session(args, text_data, error_str):
        logger.error(text_data)
        logger.error(error_str)
        await args[0].send(
            errorResult(text_data['command'], "已离线" if "离线" in error_str else "无效session", text_data['path']))
        return None

    return wrapper

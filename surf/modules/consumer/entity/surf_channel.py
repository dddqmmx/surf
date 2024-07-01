# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius(fuzequan)
Created Time    : 2024/5/31 15:14
File Name       : surf_channel.py
Last Edit Time  :
"""
import asyncio
import json
from typing import List, Tuple

from surf.appsGlobal import logger
from .surf_user import SurfUser


class SurfChannel(object):
    def __init__(self, channel_id: str, is_voice_channel: bool, max_members: int = 0):
        self.channel_id: str = channel_id
        self.is_voice_channel: int = is_voice_channel
        self.max_members: int = max_members
        self.channel_users: List[SurfUser] = []
        self.lock = asyncio.Lock()

    async def add_user(self, user: SurfUser) -> Tuple[bool, str]:
        rtn_str = ""
        try:
            async with self.lock:
                if user not in self.channel_users:
                    if self.max_members == 0 or len(self.channel_users) < self.max_members:
                        self.channel_users.append(user)
                        return True, rtn_str
                    rtn_str = "频道列表已经满人"
                else:
                    rtn_str = "用户已经在该频道中"
                    logger.error(f"User:{user.user_name} already in channel:{self.channel_id}")
        except Exception as e:
            logger.error(f"add user:{user.user_name} to to channel:{self.channel_id} error:{e}")
        return False, rtn_str

    async def remove_user(self, user_id: str) -> bool:
        try:
            async with self.lock:
                for user in self.channel_users:
                    if user.check_user_id(user_id):
                        self.channel_users.remove(user)
                        return True
        except Exception as e:
            logger.error(f"remove user:{user.user_name} from channel:{self.channel_id} error:{e}")
        return False

    def size(self) -> int:
        return len(self.channel_users)

    async def broadcast(self, text_data):
        tasks = []
        try:
            if self.is_voice_channel:
                for user in self.channel_users:
                    if user.check_user_id_by_session_id(text_data['session_id']):
                        continue
                    tasks.append(user.broadcast(json.dumps(text_data)))
            else:
                tasks = [user.broadcast(json.dumps(text_data)) for user in self.channel_users]
            await asyncio.gather(*tasks)
            logger.info(f'broadcast to all user in channel:{self.channel_id} done, total:{len(tasks)}')
        except Exception as e:
            logger.error(f"broadcast to all user in channel:{self.channel_id} error:{e}")

    async def change_size(self, size: int):
        try:
            async with self.lock:
                self.max_members = size
                return True
        except Exception as e:
            logger.error(f"change_size:{size} error:{e}")
            return False

    def get_users_in_channel(self) -> List[SurfUser]:
        return [user.get_user_data() for user in self.channel_users]

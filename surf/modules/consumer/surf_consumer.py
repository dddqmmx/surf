# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius(fuzequan)
Created Time    : 2024/5/8 15:14
File Name       : surf_consumer.py
Last Edit Time  : 
"""
import json
from typing import Callable, Dict

from surf.appsGlobal import logger, errorResult, setResult
from surf.modules.util import BaseConsumer
from surf.modules.consumer.entity import UserPool, session_check
from surf.modules.consumer.services import ChatService, ServerService, UserService

from cryptography.hazmat.primitives import serialization
from surf.modules.encryption.encryption_ras import generate_key_pair


class SurfConsumer(BaseConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.userPool = UserPool()
        self.session_id = None
        self.service_dict = {
            "chat": ChatService(),
            "server": ServerService(),
            "user": UserService()
        }
        self.func_dict: Dict[str, Dict[str, Callable[[str], any]]] = {
            "key": {
                "key_exchange": self.key_exchange
            },
            "chat": {
                "get_message": self.get_message,
                "send_message": self.send_message,
                "send_audio": self.send_audio,
                "revoke_message": self.revoke_message
            },
            "user": {
                'login': self.login,
                'get_user_data': self.get_user_data,
                'search_user': self.search_user,
                'get_friends': self.get_friends,
                'add_friends': self.add_friend,
                'get_invitations': self.get_invitations
            },
            "server": {
                "create_server": self.create_server,
                "create_channel_group": self.create_channel_group,
                "delete_channel_group": self.delete_channel_group,
                "create_channel": self.create_channel,
                "delete_channel": self.delete_channel,
                "get_server_details": self.get_server_details,
                "add_server_member": self.add_server_member,
                "connect_to_channel": self.connect_to_channel,
                "disconnect_from_channel": self.disconnect_from_channel,
                "get_channel_users_data": self.get_channel_users_data
            },
            'test': {
                'test1': self.test
            }
        }

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        if self.session_id:
            await self.userPool.detach_user_from_pool_by_session_id(self.session_id)

    @session_check
    async def receive(self, text_data=None, bytes_data=None):
        text_data = json.loads(text_data)
        command = text_data['command']
        # path = self.scope['url_route']['kwargs']['path']
        path = text_data['path']
        if path in self.func_dict.keys() and command in self.func_dict[path].keys():
            await self.func_dict[path].get(command)(text_data)

    async def key_exchange(self, text_data):
        """
        key 交换
        :param text_data:
        :return:
        """
        private_key, public_key = generate_key_pair()  # 将private_key保存为self.private_key
        serialized_public_key = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        await self.send(setResult(text_data['command'], serialized_public_key.decode('utf-8'), text_data['path']))

    """-------------------------------user----------------------------"""

    async def login(self, text_data):
        """
        登陆
        :param text_data:
        :return:
        """
        respond_json, session = self.service_dict['user'].login(text_data['public_key'])
        if session:
            if not await self.userPool.init_new_user(session, self):
                logger.error('user login failed, see more at connections.log')
                await self.send(errorResult('login', '登录失败', 'user'))
        self.session_id = session.session_id
        await self.send(respond_json)

    async def get_user_data(self, text_data):
        """
        获取用户信息
        :param text_data:
        :return:
        """
        respond_json = self.service_dict['user'].get_user_data(text_data)
        await self.send(respond_json)

    async def search_user(self, text_data):
        """
        查询用户
        :param text_data:
        :return:
        """
        respond_json = self.service_dict['user'].search_user(text_data)
        await self.send(respond_json)

    async def get_friends(self, text_data):
        """
        获取好友
        :param text_data:
        :return:
        """
        respond_json = self.service_dict['user'].get_friends(text_data)
        await self.send(respond_json)

    async def add_friend(self, text_data):
        """
        添加好友
        :param text_data:
        :return:
        """
        respond_json = self.service_dict['user'].add_friend(text_data, self.session_id)
        await self.send(respond_json)

    async def get_invitations(self, text_data):
        """
        获取好友申请列表
        :param text_data:
        :return:
        """
        respond_json = self.service_dict['user'].get_invitations(text_data)
        await self.send(respond_json)

    """-------------------------------server----------------------------"""

    async def create_server(self, text_data):
        """
        创建服务器
        :param text_data:
        :return:
        """
        respond_json = self.service_dict['server'].create_server(text_data)
        await self.send(respond_json)

    async def create_channel_group(self, text_data):
        """
        创建频道组
        :param text_data:
        :return:
        """
        respond_json = self.service_dict['server'].create_channel_group(text_data)
        await self.send(respond_json)

    async def delete_channel_group(self, text_data):
        """
        删除频道组
        :param text_data:
        :return:
        """
        respond_json = self.service_dict['server'].delete_channel_group(text_data)
        await self.send(respond_json)

    async def create_channel(self, text_data):
        """
        创建频道
        :param text_data:
        :return:
        TODO: 相关权限验证
        """
        respond_json = self.service_dict['server'].create_channel(text_data)
        await self.send(respond_json)

    async def delete_channel(self, text_data):
        """
        删除频道
        :param text_data:
        :return:
        TODO: 相关权限验证
        """
        respond_json = self.service_dict['server'].delete_channel(text_data)
        await self.send(respond_json)

    async def get_server_details(self, text_data):
        """
        获取服务器详细信息
        :param text_data:
        :return:
        """
        respond_json = self.service_dict['server'].get_server_details(text_data)
        await self.send(respond_json)

    async def add_server_member(self, text_data):
        """
        添加服务器成员
        :param text_data:
        :return:
        """
        respond_json = self.service_dict['server'].add_server_member(text_data)
        await self.send(respond_json)

    async def connect_to_channel(self, text_data):
        """
        链接用户到频道
        :param text_data:
        :return:
        """
        flag, rtn_str = await self.userPool.connect_user_to_single_channel_by_id(text_data['session_id'],
                                                                                 text_data['channel_id'])
        result = setResult(f"{text_data['command']}_result", flag, 'server') if flag else setResult(
            text_data['command'],
            rtn_str,
            'server')
        await self.send(result)

    async def disconnect_from_channel(self, text_data):
        """
        从频道中断开用户联机
        :param text_data:
        :return:
        """
        flag = await self.userPool.connect_user_to_single_channel_by_id(text_data['session_id'],
                                                                        text_data['channel_id'])
        result = setResult(f"{text_data['command']}_result", flag, 'server')
        await self.send(result)

    async def get_channel_users_data(self, text_data):
        """
        获取频道内的用户（语音频道用）
        :param text_data:
        :return:
        """
        result = setResult(f"{text_data['command']}_result",
                           self.userPool.get_channel_users(text_data['channel_id']),
                           "server")
        await self.send(result)

    async def get_server_members(self, text_data):
        """
        获取服务器内的所有用户
        """
        respond_json = self.service_dict['server'].get_server_members(text_data)
        await self.send(respond_json)

    """-------------------------------chat----------------------------"""

    async def get_message(self, text_data):
        """
        获取消息
        :param text_data:
        :return:
        """
        respond_json = self.service_dict['chat'].get_message(text_data)
        await self.send(respond_json)

    async def send_message(self, text_data):
        """
        发送消息
        :param text_data:
        :return:
        """
        respond_json = self.service_dict['chat'].send_message(text_data)
        if json.loads(respond_json)['messages'] is not False:
            await self.userPool.broadcast_to_all_user_in_channel(json.loads(respond_json))
        else:
            await self.send(respond_json)

    async def send_audio(self, text_data):
        """
        发送音频
        :param text_data:
        :return:
        """
        text_data["is_audio"] = True
        text_data['content'] = json.loads(text_data['content'])
        print(len(text_data['content']))
        await self.userPool.broadcast_to_all_user_in_channel(text_data)

    async def revoke_message(self, text_data):
        """
        撤回消息
        :param text_data:
        :return:
        """
        respond_json = self.service_dict['chat'].revoke_message(text_data)
        await self.send(respond_json)

    async def test(self, text_data):
        await self.send('114514')

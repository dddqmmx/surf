# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius(fuzequan)
Created Time    : 2024/4/18 15:21
File Name       : server_service.py
Last Edit Time  : 
"""
import json
import traceback
from typing import Union

from surf.modules.consumer.models import ServerModel, ChannelModel, RoleModel
from surf.modules.util import Session
from surf.appsGlobal import logger, setResult, errorResult


class ServerService(object):
    def __init__(self):
        self.__serverModel = ServerModel()
        self.__channelModel = ChannelModel()
        self.__roleModel = RoleModel()

    def create_server(self, text_data):
        """
            filters:
                description: "",
                name: "",
                owner_id: "",
                is_private: true
        """
        error_flag = False
        server_id = None
        try:
            if text_data:
                filters = text_data.get("server", None)
                if filters:
                    if isinstance(filters, dict):
                        filters["owner_id"] = Session.get_session_by_id(text_data["session_id"]).get("user_id")
                        server_filter = {f"c_{k}": v for k, v in filters.items()}
                        server_id = self.__serverModel.save_server(server_filter)
                        if server_id:
                            permissions = self.__roleModel.get_all_permissions()
                            filters = [
                                {
                                    "c_server_id": server_id,
                                    "c_name": "服务器拥有者",
                                    "c_permissions": json.dumps([item['id'] for item in permissions])
                                },
                                {
                                    "c_server_id": server_id,
                                    "c_name": "普通成员",
                                    "c_permissions": json.dumps([permissions[0]['id']])
                                }
                            ]
                            role_ids = self.__roleModel.create_role(filters)
                            if role_ids is not False and len(role_ids) == 2:
                                filters = {"c_server_id": server_id, "c_user_id": server_filter["c_owner_id"],
                                           "c_roles": json.dumps([role_ids[0]])}
                                res = self.__serverModel.save_server_user(filters=filters)
                                if res:
                                    filters = [{"c_server_id": server_id, "c_group_name": "文字频道分组"},
                                               {"c_server_id": server_id, "c_group_name": "语音频道分组"}]
                                    res = self.__channelModel.save_channel_group(filters)
                                    if res is not False and len(res) == 2:
                                        filters = [
                                            {
                                                "c_group_id": res[0],
                                                "c_name": "默认文字频道",
                                                "c_type": "text",
                                                "c_description": "这是一个文字频道",
                                                "c_create_by": server_filter["c_owner_id"]
                                            },
                                            {
                                                "c_group_id": res[1],
                                                "c_name": "默认语音频道",
                                                "c_type": "voice",
                                                "c_description": "这是一个语音频道",
                                                "c_create_by": server_filter["c_owner_id"]
                                            }
                                        ]
                                        channel_ids = self.__channelModel.save_channel(filters)
                                        if channel_ids is not False and len(channel_ids) == 2:
                                            filters = [
                                                {
                                                    "c_channel_id": channel_ids[0],
                                                    "c_user_id": server_filter["c_owner_id"],
                                                    # TODO:更改为实际权限
                                                    "c_permissions": json.dumps(1)  # 假设权限ID 1 是基础访问权限
                                                },
                                                {
                                                    "c_channel_id": channel_ids[1],
                                                    "c_user_id": server_filter["c_owner_id"],
                                                    # TODO:更改为实际权限
                                                    "c_permissions": json.dumps(1)  # 假设权限ID 1 是基础访问权限
                                                }
                                            ]
                                            if self.__channelModel.save_channel_members(filters):
                                                return setResult(f"{text_data['command']}_result", True, 'server')
                                        else:
                                            error_flag = True
                                            logger.error('频道创建失败')
                                    logger.info("服务器创建成功")
                                else:
                                    logger.error("添加服务器创始者失败")
                                    error_flag = True
                            else:
                                logger.error("服务器初始角色添加失败")
                                error_flag = True
                        else:
                            logger.error("服务器创建失败")
                            error_flag = True
                    else:
                        logger.error("类型错误")
                        error_flag = True
                else:
                    logger.error("未获取到server参数")
                    error_flag = True
            else:
                logger.error("text_data参数错误")
                error_flag = True
        except Exception as e:
            error_flag = True
            logger.error(f"create server error：{e}\n{traceback.format_exc()}")
        if error_flag and server_id:
            self.__serverModel.delete_server_by_id({"c_server_id": server_id})
            print('delete error server done')
        return errorResult(f"{text_data['command']}_result", '服务器创建失败', 'server')

    def create_channel_group(self, text_data):
        try:
            if text_data:
                filters = text_data.get("channel_group", None)
                if filters:
                    group_id = self.__channelModel.save_channel_group({f"c_{k}": v for k, v in filters.items()})
                    if group_id is not False:
                        logger.info(f"创建频道组成功：{group_id}")
                        return setResult(f"{text_data['command']}_result", True, 'server')
                    else:
                        logger.error("创建频道组失败")
                else:
                    logger.error("filters error")
            else:
                logger.error("text_data is None type")
        except Exception as e:
            logger.error(f"create channel group error\n{e}\n{traceback.format_exc()}")
        return errorResult(f"{text_data['command']}_result", '创建频道组失败', 'server')

    def create_channel(self, text_data):
        try:
            if text_data:
                filters = text_data.get("channel", None)
                if filters:
                    group_id = self.__channelModel.save_channel({f"c_{k}": v for k, v in filters.items()})
                    if group_id is not False:
                        return setResult(f"{text_data['command']}_result", True, 'server')
                    else:
                        logger.error("create failed")
                else:
                    logger.error("params channel_group error")
            else:
                logger.error("text_data is empty")
        except Exception as e:
            logger.error(f"create channel group error\n{e}\n{traceback.format_exc()}")
        return errorResult(f"{text_data['command']}_result", '创建频道失败', 'server')

    def add_server_member(self, text_data):
        try:
            if text_data:
                filters = text_data.get("server_member", None)
                if filters:
                    filters['role_id'] = self.__roleModel.get_server_role_by_name(filters)
                    res = self.__serverModel.save_server_user(
                        {f"c_{k}": v for k, v in filters.items()})
                    if len(res) > 0:
                        return setResult(f"{text_data['command']}_result", True, 'server')
                else:
                    logger.error("filters is None")
        except Exception as e:
            logger.error(f"""{e}\n{traceback.format_exc()}""")
        return errorResult(f"{text_data['command']}_result", '添加失败', 'server')

    def get_server_details(self, text_data):
        try:
            server_dict = self.__serverModel.get_server_details(text_data['server_id'])[0]
            server_dict['channel_groups'] = []
            channel_group_list = self.__channelModel.get_channel_group_by_server_id(text_data['server_id'])
            if len(channel_group_list) > 0:
                for channel_group in channel_group_list:
                    channel_group_dict = {k: v for k, v in channel_group.items()}
                    channel_group_dict['channels'] = self.__channelModel.get_channel_by_group_id(channel_group_dict['id'])
                    server_dict['channel_groups'].append(channel_group_dict)
                return setResult(f"{text_data['command']}_result", server_dict, 'server')
            return setResult(f"{text_data['command']}_result", False, 'server')
        except Exception as e:
            print(f"""{e}\n{traceback.format_exc()}""")
        return errorResult(f"{text_data['command']}_result", '查询错误', 'server')

    def get_servers_by_user(self, text_data):
        try:
            session_id = text_data.get('session_id', None)
            if session_id:
                session = Session.get_session_by_id(session_id)
                user_id = session.get('user_id')
                server_list = self.__serverModel.get_servers_by_user_id(user_id)
                data = []
                for server in server_list:
                    server_dict = self.__serverModel.get_server_details(server['id'])[0]
                    data.append(server_dict)
                return setResult(f"{text_data['command']}_result", data, 'server')
            else:
                logger.error('session_id not get')
        except Exception as e:
            print(f"""{e}\n{traceback.format_exc()}""")
        return errorResult(f"{text_data['command']}_result", 'session_id not get', 'server')

    def get_channels_by_user_id(self, user_id) -> Union[list, bool]:
        try:
            res = self.__channelModel.get_channel_ids_by_user_id(user_id)
            if res:
                return res
        except Exception as e:
            print(f"""{e}\n{traceback.format_exc()}""")
        return False

    def get_server_by_channel_id(self, channel_id) -> Union[str, bool]:
        try:
            res = self.__channelModel.get_server_by_channel_id(channel_id)
            if res:
                return res[0]['id']
        except Exception as e:
            print(f"""{e}\n{traceback.format_exc()}""")
        return False

# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius(fuzequan)
Created Time    : 2024/4/18 15:21
File Name       : server_service.py
Last Edit Time  : 
"""
import json
import traceback

from surf.modules.consumer.models import ServerModel, ChannelModel, RoleModel
from surf.modules.util import Session


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
        respond_json = {
            "command": "create_result",
            "message": False
        }
        error_flag = False
        server_id = None
        try:
            if text_data:
                filters = text_data.get("server", None)
                if filters:
                    if isinstance(filters, dict):
                        filters["owner_id"] = Session.get_session_by_id(filters["session_id"]).get("user_id")
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
                                    "c_permissions": json.dumps([permissions[0]])
                                }
                            ]
                            role_ids = self.__roleModel.create_role(filters)
                            if len(role_ids) == 2:
                                filters = {"c_server_id": server_id, "c_user_id": server_filter["c_owner_id"],
                                           "c_roles": json.dumps([role_ids[0]])}
                                res = self.__serverModel.save_server_user(filters=filters)
                                if res:
                                    filters = [{"c_server_id": server_id, "c_group_name": "文字频道分组"},
                                               {"c_server_id": server_id, "c_group_name": "语音频道分组"}]
                                    res = self.__channelModel.save_channel_group(filters)
                                    if len(res) == 2:
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
                                        res = self.__channelModel.save_channel(filters)
                                        if res is not False and len(res) == 2:
                                            respond_json["message"] = True
                                        else:
                                            error_flag = True
                                            print("create channel failed")
                                    print("成功")
                                else:
                                    print("add creator to server failed")
                                    error_flag = True
                            else:
                                print("add server role failed")
                                error_flag = True
                        else:
                            print("server create failed")
                            error_flag = True
                    else:
                        print("type error")
                        error_flag = True
                else:
                    print("未获取到server参数")
                    error_flag = True
            else:
                print("text_data参数错误")
                error_flag = True
        except Exception as e:
            error_flag = True
            print(f"create server error：{e}\n{traceback.format_exc()}")
        finally:
            if error_flag and server_id:
                self.__serverModel.delete_server_by_id({"c_server_id": server_id})
                print('delete error server done')
            return json.dumps(respond_json)

    def create_channel_group(self, text_data):
        respond_json = {
            "command": "create_result",
            "message": False
        }
        try:
            if text_data:
                filters = text_data.get("channel_group", None)
                if filters:
                    group_id = self.__channelModel.save_channel_group({f"c_{k}": v for k, v in filters.items()})
                    if group_id is not False:
                        respond_json["message"] = True
                    else:
                        print("create failed")
                else:
                    print("params channel_group error")
            else:
                print("text_data is empty")
        except Exception as e:
            print(f"create channel group error\n{e}\n{traceback.format_exc()}")
        finally:
            return json.dumps(respond_json)

    def create_channel(self, text_data):
        respond_json = {
            "command": "create_result",
            "message": False
        }
        try:
            if text_data:
                filters = text_data.get("channel", None)
                if filters:
                    group_id = self.__channelModel.save_channel({f"c_{k}": v for k, v in filters.items()})
                    if group_id is not False:
                        respond_json["message"] = True
                    else:
                        print("create failed")
                else:
                    print("params channel_group error")
            else:
                print("text_data is empty")
        except Exception as e:
            print(f"create channel group error\n{e}\n{traceback.format_exc()}")
        finally:
            return json.dumps(respond_json)

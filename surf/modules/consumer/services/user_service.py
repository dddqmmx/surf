# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius
Created Time    : 2024/4/13 19:39
File Name       : user_service
Project Name    : surf-extreme
Last Edit Time  : 
"""
import json
import traceback

from surf.modules.util import Session
from surf.modules.consumer.models import UserModel
from .server_service import ServerService
from surf.appsGlobal import logger, setResult, errorResult


class UserService(object):
    def __init__(self):
        self.__userModel = UserModel()
        pass

    def login(self, public_key):
        try:
            session = Session.create_session()
            session.set('client_public_key', public_key)
            res = self.__userModel.get_userid_by_public_key(public_key)
            if len(res) > 0:
                user_id = res[0]['id']
            else:
                filters = {
                    "c_public_key": public_key
                }
                user_id = self.__userModel.save_user(filters)
            if user_id is not False:
                logger.info(f"user {user_id} has login")
                session.set('user_id', user_id)
                return setResult('to_url', {'address': 'main', 'session_id': session.session_id})
        except Exception as e:
            logger.error(f"""{e}\n{traceback.format_exc()}""")
        return errorResult('to_url', False)

    def get_user_data(self, text_data):
        try:
            session = Session.get_session_by_id(text_data['session_id'])
            if session:
                user_id = session.get("user_id")
                res = self.__userModel.get_userdata_by_userid([user_id])
                if len(res) > 0:
                    user_dict = {
                        "user_nickname": res[0]["nickname"],
                        "user_info": res[0]["info"],
                        'servers': []
                    }
                    servers = ServerService().get_servers_by_user(text_data)
                    servers = json.loads(servers)
                    if servers['status']:
                        user_dict['servers'] = servers['messages']
                        return setResult(f"{text_data['command']}_result", {'user': user_dict})
                    else:
                        logger.error('获取用户所在服务器错误')
        except Exception as e:
            logger.error(f"""{e}\n{traceback.format_exc()}""")
        return errorResult(f"{text_data['command']}_result", '获取用户数据错误')

    def search_user(self, text_data):
        user_id_list = text_data['user_id_list']
        data = False
        try:
            if isinstance(user_id_list, list):
                res = self.__userModel.get_userdata_by_userid(user_id_list)
                if len(res) > 0:
                    data = []
                    for item in res:
                        data.append({"user_nickname": item["nickname"], "user_info": item["info"]})
                return setResult(f"{text_data['command']}_result", data)
        except Exception as e:
            logger.error(f"""{e}\n{traceback.format_exc()}""")
        return errorResult(f"{text_data['command']}_result", '搜索失败')

    def get_friends(self, text_data):
        try:
            session = Session.get_session_by_id(text_data['session_id'])
            if session:
                user_id = session.get("user_id")
                friend_list = self.__userModel.get_friends_by_user_id(user_id)
                if len(friend_list) > 0:
                    user_list = self.__userModel.get_userdata_by_userid([item['id'] for item in friend_list])
                    if len(user_list) > 0:
                        return setResult(f"{text_data['command']}_result", user_list)
                    else:
                        logger.error(f"获取好友信息错误，好友列表:{str(friend_list)}")
                else:
                    return setResult(f"{text_data['command']}_result", False)
            logger.error('session不存在或已过期')
        except Exception as e:
            logger.error(f"""{e}\n{traceback.format_exc()}""")
        return errorResult(f"{text_data['command']}_result", '获取失败')

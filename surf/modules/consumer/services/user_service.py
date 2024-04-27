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


class UserService(object):
    def __init__(self):
        self.__userModel = UserModel()
        pass

    def login(self, session_id):
        try:
            session = Session.get_session_by_id(session_id)
            if session:
                public_key = session.get('client_public_key')
                res = self.__userModel.get_userid_by_public_key(public_key)
                if len(res) > 0:
                    print(1)
                    user_id = res[0]['id']
                else:
                    print(2)
                    filters = {
                        "c_public_key": public_key
                    }
                    user_id = self.__userModel.save_user(filters)
                print(user_id)
                if user_id is not False:
                    session.set('user_id', user_id)
                    respond_json = {
                        'command': 'to_url',
                        'url': 'main'
                    }
                    return json.dumps(respond_json)
                else:
                    return False
        except Exception as e:
            print(f"""{e}\n{traceback.format_exc()}""")
            return False

    def get_user_data(self, text_data):
        respond_json = {
            'command': f"{text_data['command']}_result",
            'message': {}
        }
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
                    respond_json['message']['user'] = user_dict
                    servers = ServerService().get_servers_by_user(text_data)
                    servers = json.loads(servers)
                    if servers['status']:
                        respond_json['message']['user']['servers'] = servers['message']
                else:
                    return False
        except Exception as e:
            print(f"""{e}\n{traceback.format_exc()}""")
            return False
        finally:
            return json.dumps(respond_json)

    def search_user(self, user_id_list):
        respond_json = {
            'command': "search_user_result",
            'message': [],
            'status': False
        }
        try:
            if isinstance(user_id_list, list):
                res = self.__userModel.get_userdata_by_userid(user_id_list)
                if len(res) > 0:
                    for item in res:
                        respond_json['message'].append({"user_nickname": item["nickname"], "user_info": item["info"]})
                        respond_json['status'] = True
        except Exception as e:
            print(f"""{e}\n{traceback.format_exc()}""")
        finally:
            return json.dumps(respond_json)

    def get_friends(self, text_data):
        respond_json = {
            'command': f"{text_data['command']}_result",
            'message': [],
            'status': False
        }
        try:
            session = Session.get_session_by_id(text_data['session_id'])
            if session:
                user_id = session.get("user_id")
                friend_list = self.__userModel.get_friends_by_user_id(user_id)
                if len(friend_list) > 0:
                    user_list = self.__userModel.get_userdata_by_userid([item['id'] for item in friend_list])
                    if len(user_list) > 0:
                        respond_json['message'] = user_list
                        respond_json['status'] = True
                    else:
                        return False
                else:
                    return False
        except Exception as e:
            print(f"""{e}\n{traceback.format_exc()}""")
            return False
        finally:
            return json.dumps(respond_json)
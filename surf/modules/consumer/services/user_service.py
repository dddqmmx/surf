# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius
Created Time    : 2024/4/13 19:39
File Name       : user_service
Project Name    : surf-websocket
Last Edit Time  : 
"""
from surf.modules.util import Session
from surf.modules.consumer.models import UserModel


class UserService(object):
    def __init__(self):
        self.__pg = UserModel()
        pass

    def login(self, session_id, ):
        session = Session.get_session_by_id(session_id)
        if session:
            public_key = session.get('client_public_key')
            res = self.__pg.get_userid_by_public_key(public_key)
            if len(res) > 0:
                print(1)
                user_id = res[0]['id']
            else:
                print(2)
                filters = {
                    "c_public_key": public_key
                }
                user_id = self.__pg.save('public.t_users', filters, return_id=True, return_id_clumn="c_user_id")
            print(user_id)
            if user_id is not False:
                session.set('user_uuid', user_id)
                request_json = {
                    'command': 'to_url',
                    'url': 'main'
                }
                return request_json
            else:
                return False

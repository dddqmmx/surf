# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius(fuzequan)
Created Time    : 2024/4/29 16:16
File Name       : surf_user.py
Last Edit Time  : 
"""

from channels.generic.websocket import AsyncWebsocketConsumer
from session_util import Session
from surf.appsGlobal import get_logger

logger = get_logger('user')


class SurfUser(object):
    def __init__(self, user_id: str, session_id: str, consumer):
        self.__cur_server = None
        self.__user_id = user_id
        self.__session_id = session_id
        self.__servers = []
        self.__ws = AsyncWebsocketConsumer()
        self.__ws.scope = consumer.scope
        self.__ws.send = consumer.send

    def check_session_id(self, session_id) -> bool:
        return session_id == self.__session_id

    def check_user_id_by_session_id(self, session_id) -> bool:
        return Session.get_session_by_id(session_id).get('user_id') == self.__user_id

    def set_cur_server(self, cur_server):
        self.__cur_server = cur_server

    def check_cur_server(self, cur_server) -> bool:
        return self.__cur_server == cur_server

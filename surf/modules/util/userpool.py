# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius(fuzequan)
Created Time    : 2024/4/28 16:13
File Name       : userpool.py
Last Edit Time  : 
"""
import asyncio
from surf.appsGlobal import get_logger

con_log = get_logger('connections')


class UserPool(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(UserPool, cls).__new__(cls)

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.__connected_user = {}
            self.lock = asyncio.Lock()
            self._initialized = True

    def get_users(self):
        return self.__connected_user.copy()

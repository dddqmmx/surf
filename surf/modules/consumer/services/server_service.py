# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius(fuzequan)
Created Time    : 2024/4/18 15:21
File Name       : server_service.py
Last Edit Time  : 
"""

from surf.modules.consumer.models import ServerModel


class ServerService(object):
    def __init__(self):
        self.__serverModel = ServerModel()

    def create_server(self, filters: dict):
        column_list: list = self.__serverModel.get_columns()
        if all(filters.keys()) in column_list:
            res = self.__serverModel.create_server(filters)
            if res is not False:
                print(res)
                return True
        else:
            return False

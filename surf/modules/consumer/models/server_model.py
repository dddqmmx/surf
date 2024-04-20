# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius(fuzequan)
Created Time    : 2024/4/18 15:23
File Name       : server_model.py
Last Edit Time  : 
"""

from surf.modules.util import BaseModel


class ServerModel(BaseModel):
    def __init__(self):
        super().__init__()

    def get_columns(self):
        return self._pg.getClumnsByTable("t_servers")

    def create_server(self, filters: dict):
        return self._pg.save(table="t_servers", filters=filters, return_id=True, return_id_clumn="c_server_id")

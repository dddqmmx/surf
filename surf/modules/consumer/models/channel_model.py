# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius
Created Time    : 2024/4/20 19:37
File Name       : channel_model
Project Name    : surf-websocket
Last Edit Time  : 
"""
import traceback
from typing import Union, List, Dict

from surf.modules.util import BaseModel


class ChannelModel(BaseModel):
    def __init__(self):
        super().__init__()

    def save_channel(self, filters) -> str or bool:
        return self._pg.save("t_channels", filters, primary="c_channel_id", return_id=True,
                             return_id_clumn="c_channel_id")

    def save_channel_group(self, filters) -> str or bool:
        return self._pg.save("t_channel_groups", filters, primary="c_group_id", return_id=True,
                             return_id_clumn="c_group_id")

    def get_channel_group_by_server_id(self, server_id):
        res = []
        try:
            sql = """SELECT c_group_id as id, c_group_name as name FROM t_channel_groups WHERE c_server_id = %s"""
            res.extend(self._pg.query(sql, [server_id]))
        except Exception as e:
            print(f"""{e}\n{traceback.format_exc()}""")
        finally:
            return res

    def get_channel_by_group_id(self, group_id):
        res = []
        try:
            sql = """
            SELECT 
                c_channel_id as id, 
                c_name as name, 
                c_type as type,
                c_description as description
            FROM t_channels WHERE c_group_id = %s"""
            res.extend(self._pg.query(sql, [group_id]))
        except Exception as e:
            print(f"""{e}\n{traceback.format_exc()}""")
        finally:
            return res

    def save_channel_members(self, filters) -> bool:
        return self._pg.save("t_channel_members", filters)

    def get_channel_ids_by_user_id(self, user_id) -> List[Dict[str, str]]:
        res = []
        try:
            sql = """
                    SELECT 
                        c_channel_id as id
                    FROM t_channel_members WHERE c_user_id = %s"""
            res.extend(self._pg.query(sql, [user_id]))
        except Exception as e:
            print(f"""{e}\n{traceback.format_exc()}""")
        finally:
            return res

    def get_server_by_channel_id(self, channel_id) -> List[Dict[str, str]]:
        res = []
        try:
            sql = """
            SELECT 
                s.c_server_id as id 
            FROM
                t_servers as s 
            INNER JOIN 
                t_channel_groups as cg 
                ON 
                (s.c_server_id = cg.c_server_id )   
            INNER JOIN
                t_channels as c
                ON 
                (cg.c_group_id = c.c_group_id)
            WHERE c.c_channel_id = %s
            """
            res.extend(self._pg.query(sql, [channel_id]))
        except Exception as e:
            print(f"""{e}\n{traceback.format_exc()}""")
        finally:
            return res

    def get_channel_details_by_channel_id(self, channel_id) -> List[Dict[str, str]]:
        res = []
        try:
            sql = """
            SELECT
                c_channel_id as id,
                c_type as type,
                c_max_members as max_members
            FROM 
                t_channels 
            WHERE c_channel_id = %s
            """
            res.extend(self._pg.query(sql, [channel_id]))
        except Exception as e:
            print(f"""{e}\n{traceback.format_exc()}""")
        finally:
            return res

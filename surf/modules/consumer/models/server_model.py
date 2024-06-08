# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius(fuzequan)
Created Time    : 2024/4/18 15:23
File Name       : server_model.py
Last Edit Time  : 
"""
import traceback

from surf.appsGlobal import logger
from surf.modules.util import BaseModel


class ServerModel(BaseModel):
    def __init__(self):
        super().__init__()

    def get_columns(self):
        return self._pg.getClumnsByTable("t_servers")

    def save_server(self, filters: dict or list):
        return self._pg.save(table="t_servers", filters=filters, return_id=True, return_id_clumn="c_server_id")

    def save_server_user(self, filters):
        return self._pg.save(table="t_server_members", filters=filters)

    def delete_server_by_id(self, filters):
        return self._pg.delete(table="t_servers", filters=filters)

    def get_servers_by_user_id(self, user_id):
        res = []
        try:
            sql = """SELECT c_server_id as id FROM t_server_members WHERE c_user_id = %s"""
            res.extend(self._pg.query(sql, [user_id]))
        except Exception as e:
            logger.error(f"""{e}\n{traceback.format_exc()}""")
        finally:
            return res

    def get_server_details(self, server_id):
        res = []
        try:
            sql = """
            SELECT 
                c_server_id as id,
                c_description as description,
                c_name as name,
                c_icon_url as icon_url
            FROM t_servers 
            WHERE c_server_id = %s AND c_is_active = true"""
            res.extend(self._pg.query(sql, [server_id]))
        except Exception as e:
            logger.error(f"""{e}\n{traceback.format_exc()}""")
        finally:
            return res

    def check_is_user_in_server_by_id(self, server_id: str, user_id: str) -> bool:
        flag = False
        try:
            sql = """
            SELECT
                COUNT(1) as count
            FROM
                t_server_members
            WHERE c_server_id = %s and c_user_id = %s
            """
            res = self._pg.query(sql, [server_id, user_id])
            flag = True if res == 1 else flag
        except Exception as e:
            logger.error(f"""{e}\n{traceback.format_exc()}""")
        finally:
            return flag

    def get_members_by_server_id(self, server_id):
        res = []
        try:
            sql = """
            SELECT c_user_id as user_id FROM t_server_members WHERE c_server_id = %s
            """
            res.extend(self._pg.query(sql, [server_id]))
        except Exception as e:
            logger.error(f"""{e}\n{traceback.format_exc()}""")
        finally:
            return res

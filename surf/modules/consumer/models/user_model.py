# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius
Created Time    : 2024/4/13 19:42
File Name       : user_model
Project Name    : surf-extreme
Last Edit Time  : 
"""
import traceback
from typing import Union, List

from surf.appsGlobal import logger
from surf.modules.util import BaseModel


class UserModel(BaseModel):
    def __init__(self):
        super().__init__()

    def get_userid_by_public_key(self, public_key):
        res = []
        try:
            sql = "SELECT c_user_id as id FROM public.t_users WHERE c_public_key = %s"
            res = self._pg.query(sql, [public_key])
        except Exception as e:
            logger.error(f"""get userid by user's public_key fails, key:{public_key}\n{e}\n{traceback.format_exc()}""")
        finally:
            return res

    def get_userdata_by_userid(self, user_id_list):
        res = []
        try:
            sql = "SELECT c_nickname as nickname, c_user_info as info FROM public.t_users WHERE c_user_id = %s"
            for user_id in user_id_list:
                if isinstance(user_id, str) and len(user_id) == 36:
                    res.extend(self._pg.query(sql, [user_id]))
                else:
                    return []
        except Exception as e:
            logger.error(f"""get user data by userid fails, users: {user_id_list}\n{e}\n{traceback.format_exc()}""")
        finally:
            return res

    def save_user(self, filters: dict, primary="c_user_id") -> Union[str, bool]:
        return self._pg.save("t_users", filters, primary, return_id=True, return_id_clumn="c_user_id")

    def get_friends_by_user_id(self, user_id):
        res = []
        try:
            sql = """SELECT c_friend_id as id FROM t_user_friends WHERE c_user_id = %s"""
            res.extend(self._pg.query(sql, [user_id]))
        except Exception as e:
            logger.error(f"""get user friends by userid fails, user: {user_id}\n{e}\n{traceback.format_exc()}""")
        finally:
            return res

    def search_user_by_id(self, user_id):
        res = []
        try:
            sql = """SELECT count(1) FROM t_users WHERE c_user_id = %s"""
            res.extend(self._pg.query(sql, [user_id]))
        except Exception as e:
            logger.error(f"""search user by id failed, search params:{user_id}\n{e}\n{traceback.format_exc()}""")
        finally:
            return res

    def add_user_as_friend(self, filters: dict) -> bool:
        return self._pg.save("t_user_friends", filters)

    def get_invitations_by_user_id(self, user_id: str):
        res = []
        try:
            sql = """SELECT c_user_id as id, c_status as status FROM t_user_friends WHERE c_friend_id = %s"""
            res.extend(self._pg.query(sql, [user_id]))
        except Exception as e:
            logger.error(f"""search user by id failed, search params:{user_id}\n{e}\n{traceback.format_exc()}""")
        finally:
            return res

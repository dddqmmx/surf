# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius
Created Time    : 2024/4/13 19:42
File Name       : user_model
Project Name    : surf-extreme
Last Edit Time  : 
"""
import traceback

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
            print(f"""get userid by user's public_key fails, key:{public_key}\n{e}\n{traceback.format_exc()}""")
        finally:
            return res

    def get_userdata_by_userid(self, user_id):
        res = []
        try:
            sql = "SELECT c_nickname as nickname, c_user_info as info FROM public.t_users WHERE c_user_id = %s"
            res = self._pg.query(sql, [user_id])
        except Exception as e:
            print(f"""get user data by userid fails, userid: {user_id}\n{e}\n{traceback.format_exc()}""")
        finally:
            return res





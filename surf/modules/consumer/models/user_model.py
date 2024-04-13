# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius
Created Time    : 2024/4/13 19:42
File Name       : user_model
Project Name    : surf-websocket
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
            res = super().query(sql, [public_key])
        except Exception as e:
            print(f"""{e}\n{traceback.format_exc()}""")
        finally:
            return res




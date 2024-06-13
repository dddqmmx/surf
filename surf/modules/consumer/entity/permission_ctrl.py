# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius(fuzequan)
Created Time    : 2024/6/1 15:14
File Name       : permission_ctrl.py
Last Edit Time  :
"""
import orjson as json
from surf.modules.consumer.models import RoleModel


class PermissionCtrl(object):
    def __init__(self, user_id=None, group_id=None, channel_id=None):
        self.global_permissions = {}
        self.group_permissions = {}
        self.channel_permissions = {}
        self.mp = RoleModel()
        self.get_global_permissions(user_id)

    def get_global_permissions(self, user_id):
        roles = self.mp.get_roles_by_user(user_id)
        for role in roles:
            rp = self.mp.get_permissions_by_role(role)[0]
            self.global_permissions.update({item for item in json.loads(rp['permission'])})

    def get_group_permissions(self, group_id):
        pass

    def get_channel_permissions(self, channel_id):
        pass


if __name__ == '__main__':
    l1 = {1, 2, 3}
    l2 = {1, 4, 5}
    print(l2)

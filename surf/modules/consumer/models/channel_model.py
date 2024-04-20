# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius
Created Time    : 2024/4/20 19:37
File Name       : channel_model
Project Name    : surf-websocket
Last Edit Time  : 
"""
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

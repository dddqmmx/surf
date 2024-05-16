# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius
Created Time    : 2024/4/27 1:31
File Name       : chat_service
Project Name    : surf-websocket
Last Edit Time  : 
"""
import copy
import datetime
import traceback
import uuid

from surf.appsGlobal import CHAT_TEMP, get_logger, setResult, errorResult
from surf.modules.util import Ec, Session

logger = get_logger('chat')


class ChatService(object):
    def __init__(self):
        self.ec = Ec()
        pass

    def get_message(self, text_data):
        try:
            channel_id = text_data.get('channel_id', None)
            if channel_id:
                search_body = {
                    "query": {
                        "match": {
                            "channel_id": channel_id
                        }
                    },
                    "sort": [
                        {
                            "chat_time": {
                                "order": "asc"
                            }
                        }
                    ],
                    "size": 20,
                    "track_scores": True
                }
                chat_list = self.ec.search('chat_message', search_body)['hits']['hits']
                messages = [chat['_source'] for chat in chat_list]
                type = text_data['type']
                logger.info(f"channel:{channel_id}'s chat data get:{chat_list}")
                return setResult(command=f"{text_data['command']}_result",
                                 data=messages,
                                 extra_col=[{"type": type}],
                                 path='chat')
        except Exception as e:
            logger.error(f"""获取消息失败\n{e}\n{traceback.format_exc()}""")
        return errorResult(f"{text_data['command']}_result", '获取消息失败', 'chat')

    def send_message(self, text_data):
        try:
            if text_data.get('session_id', None) and text_data.get('message', None):
                session = Session.get_session_by_id(text_data["session_id"])
                filters = copy.deepcopy(CHAT_TEMP)
                filters['_id'] = str(uuid.uuid4())
                filters['_source'] = text_data['message']
                filters['_source']['chat_id'] = filters['_id']
                filters['_source']['type'] = 'text'
                filters['_source']['user_id'] = session.get('user_id')
                filters['_source']['chat_time'] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                count = self.ec.bulk(self.ec.generator([filters], 'create'))
                if count[0] == 1:
                    return setResult('new_message', filters['_source'], 'chat')
                logger.error('添加数据到es失败')
        except Exception as e:
            logger(f"""发送消息失败\n{e}\n{traceback.format_exc()}""")
        return errorResult('new_message', '数据添加至es失败', 'chat')

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
from surf.modules.consumer.models import ChatModel
from surf.modules.util import Ec, Session

logger = get_logger('chat')


class ChatService(object):
    def __init__(self):
        self.ec = Ec()
        self.__chat_model = ChatModel()

    def get_message(self, text_data):
        """
        Getting Channel's Chat Data(Data Getting From ES). Supporting not just init for max of 20(maby more in
        future) messages, also supporting to getting further data for history.
        Sample of content in :param -> text_data ↓
        text_data = {
            'channel_id': 'this is an uuid for a channel', -> String type UUID only
            'last_msg': ['timestamp', chat_id]
        }
        """
        try:
            channel_id = text_data.get('channel_id', None)
            last_msg = text_data.get('last_msg', [])
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
                                "order": "desc"
                            }
                        }
                    ],
                    "size": 20,
                    "track_scores": True
                }
                if len(last_msg) > 0:
                    search_body['sort'][0]['chat_id'] = {'order': 'desc'}
                    search_body['search_after'] = last_msg
                chat_list = self.ec.search('chat_message', search_body)['hits']['hits']
                messages = [chat['_source'] for chat in chat_list]
                # for message in messages:
                #     if self.__chat_model.is_revoked(message['chat_id']):
                #         message['type'] = 'revoked'
                #         del message['content']
                messages = messages[::-1]
                logger.info(f"channel:{channel_id}'s chat data get:{chat_list}")
                return setResult(command=f"{text_data['command']}_result",
                                 data=messages,
                                 path='chat')
        except Exception as e:
            logger.error(f"""获取消息失败\n{e}\n{traceback.format_exc()}""")
        return errorResult(f"{text_data['command']}_result", '获取消息失败', 'chat')

    def send_message(self, text_data):
        try:
            if text_data.get('session_id', None) and text_data.get('message', None):
                chat_id = self.__chat_model.send_chat({
                    "c_channel_id": text_data['message']['channel_id'],
                    "c_status": 0
                })
                if chat_id:
                    session = Session.get_session_by_id(text_data["session_id"])
                    filters = copy.deepcopy(CHAT_TEMP)
                    filters['_id'] = chat_id
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

    def revoke_message(self, text_data):
        chat_id = text_data['chat_id']
        if not self.__chat_model.is_revoked(chat_id):
            res_id = self.__chat_model.revoke_message(
                {
                    "c_chat_id": chat_id,
                    "c_status": 1
                }
            )
            if chat_id == res_id:
                return setResult(f"{text_data['command']}_result", True, 'chat')
            return errorResult(f"{text_data['command']}_result", "撤回失败", 'chat')
        return errorResult(f"{text_data['command']}_result", "消息已经被撤回", 'chat')

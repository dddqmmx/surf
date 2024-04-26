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
import json
import traceback
import uuid

from surf.appsGlobal import CHAT_TEMP
from surf.modules.util import Ec, Session


class ChatService(object):
    def __init__(self):
        self.ec = Ec()
        pass

    def get_message(self, text_data):
        respond_json = {
            'command': f"{text_data['command']}_result",
            'type': 0,
            'messages': []
        }
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
                if chat_list:
                    respond_json['messages'] = [chat['_source'] for chat in chat_list]
                    respond_json['type'] = text_data['type']
        except Exception as e:
            print(f"""{e}\n{traceback.format_exc()}""")
        finally:
            return json.dumps(respond_json)

    def send_message(self, text_data):
        respond_json = {
            'command': 'send_message_result',
            'message': False
        }
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
                    respond_json = {
                                'command': 'new_message',
                                'message': filters['_source']
                            }
        except Exception as e:
            print(f"""{e}\n{traceback.format_exc()}""")
        finally:
            return json.dumps(respond_json)

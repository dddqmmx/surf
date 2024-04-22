import copy
import datetime
import json
import uuid

from channels.generic.websocket import AsyncWebsocketConsumer

from surf.appsGlobal import CHAT_TEMP
from surf.modules.util import BaseModel, Session
from surf.modules.util import Ec
connectUsers = []


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.public_key = None
        self.pg = BaseModel()
        self.ec = Ec()
        self.func_dict = {
            "get_message": self.get_message,
            "send_message": self.send_message
        }

    async def connect(self):
        connectUsers.append(self)
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        receive_json = json.loads(text_data)
        command = receive_json['command']
        if 'get_message' == command:
            pass
        elif 'send_message' == command:
            pass

    async def get_message(self, text_data):
        respond_json = {
            'command': "get_message_reply'",
            'type': 1,
            'messages': []
        }
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
            for chat in chat_list:
                respond_json['messages'].append(chat['_source'])
        await self.send(text_data=json.dumps(respond_json))

    async def send_message(self, text_data):
        if all(['session_id', 'message']) in text_data.keys():
            session = Session.get_session_by_id(text_data["session_id"])
            filters = copy.deepcopy(CHAT_TEMP)
            filters['_id'] = uuid.uuid4()
            filters['_source'] = text_data['message']
            filters['_source']['chat_id'] = filters['_id']
            filters['_source']['user_id'] = session.get('user_id')
            filters['_source']['chat_time'] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            count = self.ec.bulk(self.ec.generator([filters]))
            if count == 1:
                for user in connectUsers:
                    await user.send(
                        json.dumps({
                            'command': 'new_message',
                            'message': text_data['message']['content']
                        })
                    )

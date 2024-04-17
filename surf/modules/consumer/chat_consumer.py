import json

from channels.generic.websocket import AsyncWebsocketConsumer

from surf.modules.util import BaseModel, Session
from surf.modules.util import Ec

connectUsers = []


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.public_key = None
        self.pg = BaseModel()
        self.ec = Ec()

    async def connect(self):
        connectUsers.append(self)
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        receive_json = json.loads(text_data)
        command = receive_json['command']
        if 'get_message' == command:
            index_name = 'message'
            search_body = {
                "query": {
                    "match": {
                        "chat_uuid": "bfd83b81-e041-4570-a822-65321f63b70b"
                    }
                },
                "sort": [
                    {
                        "timestamp": {
                            "order": "asc"
                        }
                    }
                ],
                "size": 20,
                "track_scores": True
            }
            search_response = self.ec.search(index_name, search_body)['hits']['hits']
            messages = []
            for message in search_response:
                messages.append(message['_source'])
            reply_json = {
                'command': "get_message_reply'",
                'type': 1,
                'messages': messages
            }
            await self.send(text_data=json.dumps(reply_json))
        elif 'send_message' == command:
            message = receive_json['message']
            session = Session.get_session_by_id(receive_json["session_id"])
            message['user_id'] = session.get('user_id')
            del (receive_json['session_id'])
            for connectUser in connectUsers:
                await connectUser.send(
                    json.dumps({
                        'command': 'new_message',
                        'message': message
                    })
                )

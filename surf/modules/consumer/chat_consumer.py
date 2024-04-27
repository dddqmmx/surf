import json

from channels.generic.websocket import AsyncWebsocketConsumer

from surf.modules.consumer.services import ChatService
from surf.modules.util import Ec

connectUsers = []


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.public_key = None
        self.chat_service = ChatService()
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
        text_data = json.loads(text_data)
        if text_data.get('command', None):
            await self.func_dict.get(text_data['command'])(text_data)

    async def get_message(self, text_data):
        respond_json = self.chat_service.get_message(text_data)
        await self.send(respond_json)

    async def send_message(self, text_data):
        respond_json = self.chat_service.send_message(text_data)
        if respond_json['message'] is not False:
            for user in connectUsers:
                await user.send(respond_json)
        else:
            await self.send(respond_json)


if __name__ == "__main__":
    search_body = {
        "query": {
            "match": {
                "channel_id": 'aa6cd21b-7080-4e65-9059-8a6a8c303cbb'
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
    chat_list = Ec().search('chat_message', search_body)['hits']['hits']
    print(chat_list)

# yourapp/routing.py

from django.urls import re_path
from .user_consumer import UserConsumer
from .chat_consumer import ChatConsumer
from .key_exchange_consumer import KeyExchangeConsumer

url = [
    re_path(r'ws/chat/$', ChatConsumer.as_asgi()),
    re_path(r'ws/user/$', UserConsumer.as_asgi()),
    re_path(r'ws/key_exchange/$', KeyExchangeConsumer.as_asgi()),
]

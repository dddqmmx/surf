# yourapp/routing.py

from django.urls import re_path
from . import consumers
from .consumer import *
from .consumer.chat_consumer import ChatConsumer
from .consumer.key_exchange_consumer import KeyExchangeConsumer
from .consumer.login_consumer import LoginConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/$', ChatConsumer.as_asgi()),
    re_path(r'ws/login/$', LoginConsumer.as_asgi()),
    re_path(r'ws/key_exchange/$', KeyExchangeConsumer.as_asgi()),

]

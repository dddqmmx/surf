# yourapp/routing.py

from django.urls import re_path
from surf.modules.consumer.chat_consumer import ChatConsumer
from surf.modules.consumer import KeyExchangeConsumer
from surf.modules.consumer.login_consumer import LoginConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/$', ChatConsumer.as_asgi()),
    re_path(r'ws/login/$', LoginConsumer.as_asgi()),
    re_path(r'ws/key_exchange/$', KeyExchangeConsumer.as_asgi()),

]

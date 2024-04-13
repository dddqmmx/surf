# yourapp/routing.py

from django.urls import re_path
from surf.modules.consumer import (ChatConsumer, KeyExchangeConsumer)
from .login_consumer import LoginConsumer

url = [
    re_path(r'ws/chat/$', ChatConsumer.as_asgi()),
    re_path(r'ws/login/$', LoginConsumer.as_asgi()),
    re_path(r'ws/key_exchange/$', KeyExchangeConsumer.as_asgi()),
]

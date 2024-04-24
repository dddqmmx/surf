# yourapp/routing.py

from django.urls import re_path
from surf.modules.consumer import *

url = [
    re_path(r'ws/chat/$', ChatConsumer.as_asgi()),
    re_path(r'ws/user/$', UserConsumer.as_asgi()),
    re_path(r'ws/server/$', ServerConsumer.as_asgi()),
    re_path(r'ws/key_exchange/$', KeyExchangeConsumer.as_asgi()),
]

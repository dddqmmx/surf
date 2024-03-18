# yourapp/routing.py

from django.urls import re_path
from . import consumers
from .consumer import *
from .consumer import init_consumer

websocket_urlpatterns = [
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/login/$', consumers.LoginConsumer.as_asgi()),
    re_path(r'ws/init/$', init_consumer.InitConsumer.as_asgi()),

]

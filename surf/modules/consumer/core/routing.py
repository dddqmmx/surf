# yourapp/routing.py

from django.urls import re_path
from surf.modules.consumer import *

url = [
    re_path(r'ws/surf/$', SurfConsumer.as_asgi())
]

from django.urls import re_path
from .consumers import *


websocket_urlpatterns = [
    re_path(r'ws/chat/$', MyConsumer.as_asgi()),# (?P<chat>[\w-]+)/$
    re_path(r'ws/notif/$',Consumer_notication.as_asgi()),
    
]

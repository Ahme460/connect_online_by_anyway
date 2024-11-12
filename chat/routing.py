from django.urls import re_path
from .consumers import MyConsumer


websocket_urlpatterns = [
    re_path(r'ws/chat/3', MyConsumer.as_asgi()),# (?P<chat>[\w-]+)/$
]
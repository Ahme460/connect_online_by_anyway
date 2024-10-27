from django.urls import re_path
from .consumers import MyConsumer


websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<chat>[\w-]+)/$', MyConsumer.as_asgi()),
]
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter 
from chat.middleware import CustomAuthMiddleware
import chat.routing


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": CustomAuthMiddleware(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})

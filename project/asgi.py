
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
# application = get_asgi_application()

# import django


from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter 

import chat.routing
# import django
# from channels.routing import get_default_application





application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})

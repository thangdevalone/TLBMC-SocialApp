import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from .middleware import JWTAuthMiddleware
from channels.auth import AuthMiddlewareStack
from NewFeeds.routing import websocket_urlpatterns 
from MessengerChat.routing import message_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SocialApp.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket':  AuthMiddlewareStack(
        JWTAuthMiddleware(
            URLRouter(
                websocket_urlpatterns + message_urlpatterns
            )
        )
       
    ),
})

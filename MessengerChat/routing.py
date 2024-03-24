from django.urls import re_path

from .consumers import ChatConsumer

message_urlpatterns = [
    re_path(r'ws/chat/$', ChatConsumer.as_asgi()),
]

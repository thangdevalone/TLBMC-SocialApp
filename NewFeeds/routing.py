# routing.py

from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/comments', consumers.CommentConsumer.as_asgi()),
]

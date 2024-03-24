from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoomChatMessagesViewSet, RoomChatAttachmentsViewSet

router = DefaultRouter()
router.register(r'room-chat-messages', RoomChatMessagesViewSet, basename='room-chat-messages')
router.register(r'room-chat-attachments', RoomChatAttachmentsViewSet, basename='room-chat-attachments')

urlpatterns = [
    path('', include(router.urls)),
]
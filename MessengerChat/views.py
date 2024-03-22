from rest_framework import viewsets, permissions
from .models import RoomChatMessages, PrivateChatRoom, RoomChatAttachments
from .serializers import RoomChatMessagesSerializer, RoomChatAttachmentsSerializer

class RoomChatMessagesViewSet(viewsets.ModelViewSet):
    queryset = RoomChatMessages.objects.all()
    serializer_class = RoomChatMessagesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(room_id=self.kwargs['room_id'],
                                    recipient=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RoomChatAttachmentsViewSet(viewsets.ModelViewSet):
    queryset = RoomChatAttachments.objects.all()
    serializer_class = RoomChatAttachmentsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(message=RoomChatMessages.objects.get(pk=self.kwargs['message_id']))


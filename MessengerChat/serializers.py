from rest_framework import serializers
from .models import RoomChatMessages, PrivateChatRoom, RoomChatAttachments

class RoomChatMessagesSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username') 
    class Meta:
        model = RoomChatMessages
        fields = ('id', 'room', 'user', 'timestamp', 'content', 'recipient', 'is_read')

class RoomChatAttachmentsSerializer(serializers.ModelSerializer):
    attachment_url = serializers.SerializerMethodField()

    class Meta:
        model =RoomChatAttachments
        def get_attachment_url(self, obj):
            request = self.context['request']
            return request.build_absolute_uri(obj.attachment.url)


    

import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import PrivateChatRoom, RoomChatMessages, RoomChatAttachments, Presence
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_name = f'chat_room_{room_id}'

        try:
            self.chat_room = await async_to_sync(self.get_chat_room)(room_id)
        except PrivateChatRoom.DoesNotExist:
            await self.close()
            return
        await self.channel_layer.group_add(self.chat_room.group_name, self.channel_name)
        await self.update_presence(online=True)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.chat_room.group_name, self.channel_name)
        await self.update_presence(online=False)

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)

        if data['type'] == 'chat_message':
            message = await self.create_message(data['message'], data['recipient_id'])
            await self.send_message(message)


        if data['type'] == 'chat_attachment':
            attachment = await self.create_attachment(data['file'], data['message_id'])
            await self.send_attachment(attachment)

        if data['type'] == 'message_read':
            await self.update_message_read(data['message_id'])

    @async_to_sync
    async def get_chat_room(self, room_id):
        return PrivateChatRoom.objects.get(pk=room_id)

    @async_to_sync
    async def create_message(self, content, recipient_id):
        return RoomChatMessages.objects.create(
            user=self.scope['user'],
            room=self.chat_room,
            content=content,
            recipient_id=recipient_id
        )

    @async_to_sync
    async def create_attachment(self, file, message_id):
        return RoomChatAttachments.objects.create(
            message=RoomChatMessages.objects.get(pk=message_id),
            attachment=file
        )

    async def send_message(self, message):
        await self.channel_layer.group_send(
            self.chat_room.group_name,
            {'type': 'chat_message', 'message': message.content, 'sender': message.user.username, 'message_id': message.id}
        )


    async def send_attachment(self, attachment):
        await self.channel_layer.group_send(
            self.chat_room.group_name,
            {'type': 'chat_attachment', 'attachment_url': attachment.attachment_url, 'message_id': attachment.message.id}
        )

    @async_to_sync
    async def update_message_read(self, message_id):
        RoomChatMessages.objects.filter(pk=message_id).update(is_read=True)

    @async_to_sync
    async def update_presence(self, online):
        user = self.scope['user']
        presence, _ = Presence.objects.get_or_create(user=user)
        presence.last_seen = timezone.now() if online else timezone.now() - timezone.timedelta(minutes=5)
        presence.save()




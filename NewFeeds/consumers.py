import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Comment, Post
from Account.models import CustomUser
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from .serializers import CommentSerializer


class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.post_group_name = 'post'
        await self.channel_layer.group_add(
            self.post_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.post_group_name,
            self.channel_name
        )

    @database_sync_to_async
    def create_comment(self, post_id, author_id, content, rep_id=None, tag_id=None):
        author = CustomUser.objects.get(id=author_id)
        post = Post.objects.get(id=post_id)

        rep = None
        if rep_id:
            try:
                rep = Comment.objects.get(id=rep_id)
            except ObjectDoesNotExist:
                pass

        tag = None
        if tag_id:
            try:
                tag = CustomUser.objects.get(id=tag_id)
            except ObjectDoesNotExist:
                pass

        return Comment.objects.create(
            post=post,
            author=author,
            content=content,
            rep=rep,
            tag=tag
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        incoming_comment = text_data_json['comment']
        post_id = text_data_json['post_id']
        user_id = self.scope['user_id']
        rep_id = text_data_json.get('rep_id', None)
        tag = text_data_json.get('tag', None)
        # Save comment to database asynchronously
        comment = await self.create_comment(post_id, user_id, incoming_comment, rep_id, tag)
        comment_data = CommentSerializer(comment).data
        # Send message to room group
        await self.channel_layer.group_send(
            self.post_group_name,
            {
                'type': 'comment_message',
                'data': comment_data
            }
        )

    # Receive message from room group
    async def comment_message(self, event):
        

        # Send message to WebSocket
        await self.send(text_data=json.dumps(event["data"]))

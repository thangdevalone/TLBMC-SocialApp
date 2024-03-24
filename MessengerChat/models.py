from django.db import models
from Account.models import CustomUser
from django.utils import timezone

class PrivateChatRoom(models.Model):
    user1=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="user1")
    user2=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="user2")
    is_activate=models.BooleanField(default=True)
    
    def __str__(self):
        return f"Phòng chat của {self.user1} và {self.user2}."
    
    @property
    def group_name(self):
        return f"PrivateChatRoom -{self.id}"
    
class RoomChatMessagesManager(models.Manager):
    def by_room(self,room):
        qs=RoomChatMessages.objects.filter(room=room).order_by("-timestamp")

class RoomChatMessages(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    room=models.ForeignKey(PrivateChatRoom,on_delete=models.CASCADE)
    timestamp=models.DateTimeField(auto_now_add=True)
    content=models.TextField(unique=False,blank=False)
    recipient=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="recipient")
    is_read=models.BooleanField(default=False)
    
    objects=RoomChatMessagesManager()
    
    def __str__(self):
        return self.content

class RoomChatAttachments(models.Model):
    message = models.ForeignKey(RoomChatMessages, on_delete=models.CASCADE)
    attachment = models.FileField(upload_to="chat/attachments/")
    timestamp = models.DateTimeField(auto_now_add=True)

class Presence(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    last_seen = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user} - {self.last_seen}"

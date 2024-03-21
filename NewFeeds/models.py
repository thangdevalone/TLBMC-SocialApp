from django.db import models
from Account.models import CustomUser
from django.utils import timezone
# Create your models here.
class Post(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    global_post= models.BooleanField()
    created_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.created_at:
            # If created_at field is not set, set it to current local time
            self.created_at = timezone.localtime(timezone.now())
        return super().save(*args, **kwargs)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='comments_user')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    rep = models.ForeignKey('self', related_name='replies', on_delete=models.CASCADE, null=True, blank=True)
    tag = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.created_at:
            # If created_at field is not set, set it to current local time
            self.created_at = timezone.localtime(timezone.now())
        return super().save(*args, **kwargs)
class LikeComment(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes_cmt')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

class Wall(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='shares')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
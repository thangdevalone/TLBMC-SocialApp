
from django.db import models
from django.utils import timezone
from Account.models import CustomUser
class Course(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True,blank=True)
    link = models.TextField()
    image = models.ImageField(upload_to='course_images/')
    created_at = models.DateTimeField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    def save(self, *args, **kwargs):
            if not self.created_at:
                # If created_at field is not set, set it to current local time
                self.created_at = timezone.localtime(timezone.now())
            return super().save(*args, **kwargs)
    def __str__(self):
        return self.title
class CourseSave(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
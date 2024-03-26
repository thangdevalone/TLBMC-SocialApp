from django.db import models

# Create your models here.
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email, username, and password.
        """
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email, username, and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='default.png')
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    facebook = models.URLField(max_length=255, null=True, blank=True)
    instagram = models.URLField(max_length=255, null=True, blank=True)
    linkedin = models.URLField(max_length=255, null=True, blank=True)

    # Học vấn
    education = models.TextField()

    # Kinh nghiệm làm việc
    work_experience = models.TextField()

    # Kỹ năng
    skills = models.TextField()

    # Hoạt động
    activities = models.TextField(null=True, blank=True)

    # Chứng chỉ
    certificates = models.TextField(null=True, blank=True)

    # Danh hiệu và giải thưởng
    awards = models.TextField(null=True, blank=True)


    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    @property
    def is_staff(self):
        return not self.is_superuser
    
class Image(models.Model):
    image = models.ImageField(upload_to='related_images/',null=True,blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    pos=models.IntegerField()
    def __str__(self):
        return self.image.name
    
class Friendship(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Chờ đồng ý'),
        ('accepted', 'Bạn bè'),
        ('cancelled', 'Hủy kết bạn'),
    )

    from_user = models.ForeignKey(CustomUser, related_name='friendship_creator_set', on_delete=models.CASCADE)
    to_user = models.ForeignKey(CustomUser, related_name='friend_set', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

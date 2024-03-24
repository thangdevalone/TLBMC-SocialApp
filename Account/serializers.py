from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from .models import CustomUser,Image
import base64
from django.conf import settings
import os
class CustomUserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'full_name', 'education', 'profile_picture']

    def get_profile_picture(self, obj):
        if obj.profile_picture:
            # Extracting the path relative to the '/media/' directory
            return obj.profile_picture.url
        return None
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'pos', 'image', 'user']
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['full_name', 'phone_number', 'date_of_birth', 'education', 'work_experience', 'address', 'email', 'password']  # Add other fields as needed
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            phone_number=validated_data['phone_number'],
            date_of_birth=validated_data['date_of_birth'],
            education=validated_data['education'],
            work_experience=validated_data['work_experience'],
            address=validated_data['address'],
            password=validated_data['password']
        )
        return user
class UserDetailSerializer(serializers.ModelSerializer):
    related_images = serializers.SerializerMethodField()
    def get_related_images(self, obj):
        # Trích xuất các hình ảnh liên quan từ đối tượng CustomUser
        related_images = Image.objects.filter(user=obj)
        # Serialize danh sách các hình ảnh liên quan
        serializer = ImageSerializer(related_images, many=True)
        return serializer.data
    class Meta:
        model = CustomUser
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}
class CustomUserUpdateSerializer(serializers.ModelSerializer):
    profile_picture = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'profile_picture', 'full_name', 'date_of_birth', 'phone_number', 'address', 'facebook', 'instagram', 'linkedin', 'education', 'work_experience', 'skills', 'activities', 'certificates', 'awards']

    def update(self, instance, validated_data):
        profile_picture_data = validated_data.pop('profile_picture', None)
        instance = super().update(instance, validated_data)

        if profile_picture_data:
            # Giải mã base64 và lưu ảnh vào thư mục media
            format, imgstr = profile_picture_data.split(';base64,')
            ext = format.split('/')[-1]
            filename = f'{instance.pk}_profile_picture.{ext}'
            filepath = os.path.join(settings.MEDIA_ROOT, filename)

            # Ghi dữ liệu vào tệp trong thư mục media
            with open(filepath, 'wb') as f:
                f.write(base64.b64decode(imgstr))

            # Lưu đường dẫn của ảnh vào trường profile_picture
            instance.profile_picture = os.path.join(settings.MEDIA_URL, filename)
            instance.save()

        return instance
    
  
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')

        if password != password2:
            raise serializers.ValidationError("Passwords do not match")

        return data
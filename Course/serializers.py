# serializers.py

from rest_framework import serializers
from .models import Course,CourseSave
from Account.models import CustomUser
from Account.serializers import CustomUserSerializer
class CusSavedCourseSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = CourseSave
        fields = ['user']

    def get_user(self, obj):
        # Lấy thông tin người dùng liên kết với bản ghi CourseSave
        user = obj.user  # Assuming 'user' is the ForeignKey field in CourseSave
        # Serializer thông tin người dùng
        serializer = CustomUserSerializer(user)
        return serializer.data if user else None

class CourseSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    created_by=CustomUserSerializer()
    saver =serializers.SerializerMethodField()
    class Meta:
        model = Course
        fields = '__all__'
    def get_saver(self, obj):
        saver_queryset = CourseSave.objects.filter(course=obj)
        saver_serializer = CusSavedCourseSerializer(saver_queryset, many=True)  # Serialize queryset with many=True
        return saver_serializer.data
class SavedCourseSerializer(serializers.ModelSerializer):
    course = CourseSerializer(many=False)
    class Meta:
        model = CourseSave
        fields = ['id', 'course']

        

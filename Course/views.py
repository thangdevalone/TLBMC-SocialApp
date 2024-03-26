
from rest_framework import viewsets, generics, status, mixins
from rest_framework.permissions import IsAuthenticated
from Account.permissions import IsAdminOrReadOnly
from .models import Course, CourseSave
from rest_framework.views import APIView
from .serializers import CourseSerializer, SavedCourseSerializer
import base64
from django.core.files.base import ContentFile
from rest_framework.response import Response
class CourseViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminOrReadOnly]

    def list(self, request):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

    def create(self, request):
        image_data = request.data.get('image')
        if image_data:
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            image_data = ContentFile(
                base64.b64decode(imgstr), name=f"image.{ext}")
            user = request.user
            data = {
                'image': image_data,
                'created_by': user.id,
                'description': request.data.get('description'),
                'link': request.data.get('link'),
                'title': request.data.get('title')
            }
            image_serializer = CourseSerializer(data=data)
            if image_serializer.is_valid():
                image_serializer.save()
                return Response(image_serializer.data, status=status.HTTP_201_CREATED)
            return Response(image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response("", status=status.HTTP_400_BAD_REQUEST)

class CourseSaveAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Lấy dữ liệu từ request
        user_id = request.user.id
        course_id = request.data.get('course_id')

        # Kiểm tra xem bản ghi đã tồn tại hay không
        try:
            course_save = CourseSave.objects.get(user_id=user_id, course_id=course_id)
            course_save.delete()  # Xóa bản ghi nếu tồn tại
            return Response({"message": "Record deleted successfully."}, status=status.HTTP_200_OK)
        except CourseSave.DoesNotExist:
            # Nếu không có bản ghi tồn tại, tạo một bản ghi mới
            CourseSave.objects.create(user_id=user_id, course_id=course_id)
            return Response({"message": "Record created successfully."}, status=status.HTTP_201_CREATED)
    
    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        saved_courses = CourseSave.objects.filter(user_id=user_id).values_list('course_id', flat=True)
        courses = Course.objects.filter(pk__in=saved_courses)
        serializer = CourseSerializer(courses, many=True)  # Assuming you have a serializer for Course model
        return Response(serializer.data, status=status.HTTP_200_OK)
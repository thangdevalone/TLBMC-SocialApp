import json
import re
from django.shortcuts import render
# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer,UserDetailSerializer,CustomUserUpdateSerializer,ImageSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
import random
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser,Image
from .permissions import IsAdminUser
import base64
from django.core.files.base import ContentFile
otp_storage={}
class UserRegistrationAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        userData=""
        if email in otp_storage and "userData" in otp_storage[email]:
            userData = otp_storage[email]["userData"]
            # Tiếp tục xử lý
        else:
            return Response({'error': 'Dữ liệu người dùng không tồn tại hoặc không hợp lệ.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(data=userData)
        
        if(request.data.get('otp')==otp_storage[email]["otp"]):
            if serializer.is_valid():
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                data=UserDetailSerializer(user)
                return Response({'data': data.data, 'token': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }}, status=status.HTTP_201_CREATED)
            return Response({"error":"Có lỗi xảy ra"}, status=status.HTTP_400_BAD_REQUEST)
class SendOtp(APIView):
    def post(self, request):
        email = request.data.get('email')
        if email and re.match(r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', email):
            # Kiểm tra xem email đã tồn tại trong cơ sở dữ liệu hay chưa
            if CustomUser.objects.filter(email=email).exists():
                return Response({'error': 'Email đã được đăng kí'}, status=status.HTTP_400_BAD_REQUEST)
            
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])  # Tạo mã OTP ngẫu nhiên
            send_mail(
                'Xác thực email',
                f'Mã OTP của bạn là: {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            otp_storage[email]={
                "otp":otp,
                "userData":request.data
            }
     
            return Response({'message': 'Email đã được gửi OTP.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Email không hợp lệ.'}, status=status.HTTP_400_BAD_REQUEST)
class UserLoginAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(email=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            data=UserDetailSerializer(user)
            return Response({'data': data.data, 'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
class CustomUserUpdateAPIView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request):
        serializer = CustomUserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UploadRelatedImageView(APIView):
    def post(self, request, *args, **kwargs):
        # Trích xuất dữ liệu base64 từ yêu cầu
        image_data = request.data.get('image')
        pos = request.data.get('pos')
        
        # Kiểm tra xem dữ liệu hình ảnh base64 có tồn tại không
        if image_data:
            # Giải mã dữ liệu base64 thành hình ảnh
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            image_data = ContentFile(base64.b64decode(imgstr), name=f"image.{ext}")
            
            # Tạo một serializer để xử lý dữ liệu hình ảnh
            user = request.user  # Lấy người dùng hiện tại từ request.user
            image_serializer = ImageSerializer(data={'image': image_data, 'user': user.id, 'pos': pos})
            if image_serializer.is_valid():
                # Lưu hình ảnh vào cơ sở dữ liệu
                image_serializer.save()

                user_serializer = UserDetailSerializer(request.user)
                return Response(user_serializer.data['related_images'], status=status.HTTP_201_CREATED)
            return Response(image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'No image data provided'}, status=status.HTTP_400_BAD_REQUEST)
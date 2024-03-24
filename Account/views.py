
import re
from django.db.models import Q

# Create your views her
import base64
from random import sample, random
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.serializers import serialize
from django.core.signing import dumps, loads
from django.http import JsonResponse
from django.core.files.base import ContentFile
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, Friendship, Image
from .permissions import IsUser
from .serializers import (
    CustomUserSerializer, CustomUserUpdateSerializer,
    ForgotPasswordSerializer, FriendshipSerializer,
    ImageSerializer, ResetPasswordSerializer, UserDetailSerializer,
    UserSerializer,
)


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
                return Response({'data': data.data, 'tokens': {
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
    permission_classes = [IsUser]

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

class FriendshipRequestListAPIView(APIView):
    def get(self, request):
        user = request.user
        friendship_requests = Friendship.objects.filter(to_user=user, status='pending')
        serializer = FriendshipSerializer(friendship_requests, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Trích xuất id của người dùng muốn kết bạn từ dữ liệu gửi lên
        friend_id = request.data.get('friend_id')

        # Kiểm tra xem id của người bạn có hợp lệ không
        try:
            friend = CustomUser.objects.get(pk=friend_id)
        except CustomUser.DoesNotExist:
            return Response({'message': 'Người dùng không tồn tại'}, status=status.HTTP_404_NOT_FOUND)

        # Tạo một mối quan hệ bạn bè mới với trạng thái là 'pending'
        friendship_request = Friendship(from_user=request.user, to_user=friend, status='pending')
        friendship_request.save()

        # Trả về thông điệp xác nhận hoặc thông báo lỗi nếu có
        return Response({'message': 'Lời mời kết bạn đã được gửi đi'}, status=status.HTTP_201_CREATED)

    def put(self, request):
        try:
            friendship_request = Friendship.objects.get( request.data.get('from_id'))
        except Friendship.DoesNotExist:
            return Response({'message': 'Yêu cầu kết bạn không tồn tại'}, status=status.HTTP_404_NOT_FOUND)

        # Kiểm tra xem người dùng hiện tại có phải là người nhận lời mời kết bạn không
        if request.user != friendship_request.to_user:
            return Response({'message': 'Bạn không có quyền cập nhật yêu cầu kết bạn này'}, status=status.HTTP_403_FORBIDDEN)

        # Lấy trạng thái mới từ dữ liệu gửi lên
        new_status = request.data.get('status')

        # Kiểm tra xem trạng thái mới có hợp lệ không
        if new_status not in dict(Friendship.STATUS_CHOICES).keys():
            return Response({'message': 'Trạng thái không hợp lệ'}, status=status.HTTP_400_BAD_REQUEST)

        # Cập nhật trạng thái và lưu vào cơ sở dữ liệu
        friendship_request.status = new_status
        friendship_request.save()

        # Trả về thông điệp xác nhận
        return Response({'message': 'Trạng thái đã được cập nhật'}, status=status.HTTP_200_OK)
    
class FriendSuggestionAPIView(APIView):
    def get(self, request):
        # Lấy danh sách tất cả người dùng trừ người dùng hiện tại
        users = CustomUser.objects.exclude(pk=request.user.id)
        
        # Loại bỏ những người đã gửi lời mời hoặc là bạn bè của người dùng hiện tại
        excluded_users = Friendship.objects.filter(
            Q(from_user=request.user) | Q(to_user=request.user),
            status__in=['pending', 'accepted']
        ).values_list('from_user', 'to_user')
        excluded_user_ids = [user_id for friendship in excluded_users for user_id in friendship if user_id != request.user.pk]
        users = users.exclude(pk__in=excluded_user_ids)
        
        # Chọn ngẫu nhiên n người dùng từ danh sách (n là số lượng người dùng hiện có hoặc 10, tùy thuộc vào số lượng)
        n = min(10, len(users))
        suggested_users = sample(list(users), n)

        # Serialize thông tin người dùng và trả về
        serializer = CustomUserSerializer(suggested_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


@api_view(['POST'])
def forgot_password_view(request):
    serializer = ForgotPasswordSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"message": "User not found for the provided email"},
                            status=status.HTTP_404_NOT_FOUND)

        # Generate reset token
        try:
        # refresh = RefreshToken.for_user(user)
        # # reset_token = str(refresh.access_token)
            data={"email":user.email}
            token=dumps(data, key=settings.SECURITY_PASSWORD_SALT)

        except TokenError as e:
            return Response({"error": "Failed to generate reset token",
                            "status": status.HTTP_500_INTERNAL_SERVER_ERROR},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        email_subject = "Password Reset Request"
        email_message = f"Here's an email about forgetting the password for account: {user.email} \n "
        email_message += f"Click the following link to reset your password: {settings.BACKEND_URL}/api/forgot/reset-password/{token}"

        send_mail(
            email_subject,
            email_message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return Response({"message": "Password reset email sent successfully",
                        "status": status.HTTP_200_OK},
                        status=status.HTTP_200_OK)
   
@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password_view(request, token):
    serializer = ResetPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        email = loads(token, key=settings.SECURITY_PASSWORD_SALT)["email"]
        user = CustomUser.objects.get(email=email)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        return Response({"error": "Invalid reset token",
                         "status": status.HTTP_400_BAD_REQUEST},
                        status=status.HTTP_400_BAD_REQUEST)
    new_password = serializer.validated_data['password']
    if not new_password:
        raise ValidationError("New password is required")
    user.set_password(new_password)
    user.save()

    return Response({"message": "Password reset successfully",
                     "status": status.HTTP_200_OK},
                    status=status.HTTP_200_OK)

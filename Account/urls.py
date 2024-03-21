
from django.urls import path
from .views import UserRegistrationAPIView, UserLoginAPIView,SendOtp,CustomUserUpdateAPIView,UploadRelatedImageView

urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='user-registration'),
    path('login/', UserLoginAPIView.as_view(), name='user-login'),
    path('send-otp/', SendOtp.as_view(), name='otp'),
    path('update-profile/', CustomUserUpdateAPIView.as_view(), name='update_profile'),
    path('create_related_image/', UploadRelatedImageView.as_view(), name='create_related_image'),
]
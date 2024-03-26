
from django.urls import path
from .views import UserRegistrationAPIView, UserLoginAPIView,SendOtp,CustomUserUpdateAPIView,UploadRelatedImageView,reset_password_view,forgot_password_view,change_password
urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='user-registration'),
    path('login/', UserLoginAPIView.as_view(), name='user-login'),
    path('send-otp/', SendOtp.as_view(), name='otp'),
    path('update-profile/', CustomUserUpdateAPIView.as_view(), name='update_profile'),
    path('create_related_image/', UploadRelatedImageView.as_view(), name='create_related_image'),
    path("forgot/forgot-password", forgot_password_view, name="forgot_password"),
    path("forgot/reset-password/<str:token>", reset_password_view, name="reset_password"),
    path("account/change-password/<str:pk>",change_password, name="change-password"),
]
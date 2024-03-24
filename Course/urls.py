# urls.py

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, CourseSaveAPIView

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
urlpatterns = router.urls + [
     path('course-save/', CourseSaveAPIView.as_view(), name='course-save'),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, ShareViewSet,like_post,like_comment,CommentDeleteAPIView

router = DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'shares', ShareViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('posts/<int:post_id>/like/', like_post, name='like_post'),
    path('comments/<int:cmt_id>/like/', like_comment, name='like_cmt'),
     path('comments/<int:comment_id>/', CommentDeleteAPIView.as_view(), name='comment-delete'),
]

from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from Account.permissions import IsUser
from rest_framework.response import Response
from .models import Post, Like, Wall,LikeComment
from .serializers import PostSerializer, PostCreateSerializer, LikeSerializer, WallSerializer
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.views import APIView
from .models import Comment
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsUser]
    
    def get_queryset(self):
        # Sắp xếp các bài viết theo thời gian tạo, từ gần nhất đến xa nhất
        return Post.objects.order_by('-created_at')
    def get_serializer_class(self):
        if self.action == 'create':
            return PostCreateSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        # Assign the author before saving the Post instance
        serializer.save(author=self.request.user)
@api_view(['POST'])
def like_comment(request, cmt_id):
    if request.method == 'POST':
        # Kiểm tra xem user đã like bài viết này chưa
        existing_like = LikeComment.objects.filter(comment_id=cmt_id, user=request.user).first()
        if existing_like:
            # Nếu đã like, không thực hiện gì cả
            existing_like.delete()
            return Response({'message': 'Like deleted successfully'}, status=status.HTTP_200_OK)
        else:
            # Nếu chưa like, tạo mới một like
            like = LikeComment(comment_id=cmt_id, user=request.user)
            like.save()
            return Response({'message': 'Post liked successfully'}, status=status.HTTP_201_CREATED)
@api_view(['POST'])
def like_post(request, post_id):
    if request.method == 'POST':
        # Kiểm tra xem user đã like bài viết này chưa
        existing_like = Like.objects.filter(post_id=post_id, user=request.user).first()
        if existing_like:
            # Nếu đã like, không thực hiện gì cả
            existing_like.delete()
            return Response({'message': 'Like deleted successfully'}, status=status.HTTP_200_OK)
        else:
            # Nếu chưa like, tạo mới một like
            like = Like(post_id=post_id, user=request.user)
            like.save()
            return Response({'message': 'Post liked successfully'}, status=status.HTTP_201_CREATED)
class ShareViewSet(viewsets.ModelViewSet):
    queryset = Wall.objects.all()
    serializer_class = WallSerializer
    permission_classes = [IsUser]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
class CommentDeleteAPIView(APIView):
    def delete(self, request, comment_id):
        # Retrieve the comment
        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return Response({"message": "Comment does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user making the request is the owner of the comment
        if comment.author != request.user:
            return Response({"message": "You are not authorized to delete this comment"}, status=status.HTTP_403_FORBIDDEN)

        # Delete the comment
        comment.delete()
        return Response({"message": "Comment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
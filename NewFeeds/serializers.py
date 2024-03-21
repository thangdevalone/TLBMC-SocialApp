from rest_framework import serializers
from .models import Post, Comment, Wall, Like, LikeComment
from Account.serializers import CustomUserSerializer


class LikeCommentSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = LikeComment
        fields = ['id', 'user']


class CommentSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer()
    likes = LikeCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ['id','post', 'author', 'content',
                  'created_at', 'rep', 'tag', 'likes']


class LikeSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = Like
        fields = ['id', 'user']


class PostSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()
    author = CustomUserSerializer()
    likes = LikeSerializer(many=True)

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'created_at',
                  'comments', 'global_post', "likes"]

    def get_comments(self, obj):
        comments = obj.comments.all().order_by('-created_at')
        serialized_comments = CommentSerializer(comments, many=True).data
        # Lấy tất cả các like cho từng comment và bao gồm chúng trong serialized data
        for comment_data, comment in zip(serialized_comments, comments):
            likes = LikeComment.objects.filter(comment=comment)
            comment_data['likes'] = LikeCommentSerializer(likes, many=True).data
        return serialized_comments
class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['content', 'global_post']


class WallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wall
        fields = '__all__'

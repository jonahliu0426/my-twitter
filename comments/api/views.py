from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from comments.models import Comment
from comments.api.serializers import (
    CommentSerializerForCreate,
    CommentSerializer,
)


class CommentViewSet(viewsets.GenericViewSet):
    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()

    def get_permissions(self):
        # we need AllowAny() and IsAuthenticated() to initiate instance
        # not AllowAny or IsAuthenticated, which is just name for class
        if self.action == 'create':
            return [IsAuthenticated()]
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        data = {
            'user_id': request.user.id,
            'tweet_id': request.data.get('tweet_id'),
            'content': request.data.get('content'),
        }
        # 'data=' is required to pass data to the parameter 'data',
        # because the first parameter is 'instance=None' by default
        serializer = CommentSerializerForCreate(data=data)
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        # save method will call the create method in serializer
        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )

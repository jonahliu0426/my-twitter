from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from comments.models import Comment
from comments.api.permissions import IsObjectOwner
from comments.api.serializers import (
    CommentSerializerForCreate,
    CommentSerializer,
    CommentSerializerForUpdate,
)


class CommentViewSet(viewsets.GenericViewSet):
    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()

    def get_permissions(self):
        # we need AllowAny() and IsAuthenticated() to initiate instance
        # not AllowAny or IsAuthenticated, which is just name for class
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ['destroy', 'update']:
            return [IsAuthenticated(), IsObjectOwner()]
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

    def update(self, request, *args, **kwargs):
        # get_object 是 DRF 包装的一个函数，会在找不到的时候 raise 404 error
        # 所以这里无需做额外判断
        comment = self.get_object()

        # passing comment as instance to trigger update method in save method below.
        serializer = CommentSerializerForUpdate(
            instance=comment,
            data=request.data,
        )
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input'
            }, status=status.HTTP_400_BAD_REQUEST)

        # save method will trigger the update method in serializer,
        # check the implementation of save() by clicking on it
        # if self.instance is None, it will call create() method
        # otherwise, it will call save() method
        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.delete()
        return Response({
            'success': True,
        }, status=status.HTTP_200_OK)
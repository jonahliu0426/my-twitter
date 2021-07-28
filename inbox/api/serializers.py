from rest_framework import serializers
from notifications.models import Notification
from comments.models import Comment
from tweets.models import Tweet
from rest_framework.exceptions import ValidationError


class NotificationSerializer(serializers.ModelSerializer):
    actor_content_type = serializers.CharField()
    actor_object_id = serializers.CharField()

    
    class Meta:
        model = Notification
        fields = (
            'id',
            'actor_content_type',
            'actor_object_id',
            'verb',
            'action_object_content_type',
            'action_object_object_id',
            'target_content_type',
            'target_object_id',
            'timestamp',
            'unread',
        )

    """
    def _get_model_class(self, data):
        if data['actor_content_type'] == 'comment':
            return Comment
        if data['actor_content_type'] == 'tweet':
            return Tweet
        return None

    def validate(self, data):
        model_class = self._get_model_class(data)
        if not model_class:
            raise ValidationError({'actor_content_type': 'Content type does not exist'})
        liked_object = model_class.objects.filter(id=data['actor_object_id']).first()
        if not liked_object:
            raise ValidationError({'actor_object_id': 'Object does not exist'})
        return data
    """
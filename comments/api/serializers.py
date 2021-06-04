from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from comments.models import Comment
from tweets.models import Tweet
from accounts.api.serializers import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Comment
        fields = ('id', 'tweet_id', 'user', 'content', 'created_at', 'updated_at')


class CommentSerializerForCreate(serializers.ModelSerializer):
    # must manually add these two fields
    # because ModelSerializer contains only 'user' and 'tweet', not 'user_id' and 'tweet_id'
    tweet_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

    class Meta:
        model = Comment
        fields = ('content', 'tweet_id', 'user_id')

    def validate(self, data):
        if not Tweet.objects.filter(id=data['tweet_id']).exists():
            return ValidationError({
                'message': 'tweet does not exists.'
            })
        return data

    def create(self, validated_data):
        return Comment.objects.create(
            user_id=validated_data['user_id'],
            tweet_id=validated_data['tweet_id'],
            content=validated_data['content'],
        )


class CommentSerializerForUpdate(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('content', )

    def update(self, instance, validated_data):
        instance.content = validated_data['content']
        instance.save()
        return instance

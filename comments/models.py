from django.db import models
from django.contrib.auth.models import User
from tweets.models import Tweet
from likes.models import Like
from django.contrib.contenttypes.models import ContentType
from accounts.services import UserService
from utils.memcached_helper import MemcachedHelper
from comments.listeners import incr_comments_count, decr_comments_count
from django.db.models.signals import post_save, pre_delete

# Create your models here.
class Comment(models.Model):
    """
    We only implement comment of tweet, not comment of comment
    one-to-many relationship
    """
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    tweet = models.ForeignKey(Tweet, null=True, on_delete=models.SET_NULL)
    content = models.CharField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        index_together = (('tweet', 'created_at'), )

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Comment),
            object_id=self.id,
        ).order_by('-created_at')

    def __str__(self):
        return f'{self.created_at} - {self.user} says {self.content} at tweet {self.tweet_id}'

    @property
    def cached_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.user_id)


post_save.connect(incr_comments_count, sender=Comment)
pre_delete.connect(decr_comments_count, sender=Comment)

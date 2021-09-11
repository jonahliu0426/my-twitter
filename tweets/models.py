from django.db import models
from django.contrib.auth.models import User
from utils.time_helpers import utc_now
from likes.models import Like
from django.contrib.contenttypes.models import ContentType
from tweets.constants import TweetPhotoStatus, TWEET_PHOTO_STATUS_CHOICES
from accounts.services import UserService
from utils.time_helpers import utc_now
from utils.listeners import invalidate_object_cache
from utils.memcached_helper import MemcachedHelper
from django.db.models.signals import post_save

class Tweet(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text='who posts this tweet'
    )
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        index_together = (('user', 'created_at'),)
        ordering = ('user', '-created_at')

    @property
    def hours_to_now(self):
        # datetime.now 不带时区信息，需要增加上 utc 的时区信息
        return (utc_now() - self.created_at).seconds // 3600

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Tweet),
            object_id=self.id,
        ).order_by('-created_at')

    def __str__(self):
        return f'{self.created_at} {self.user}: {self.content}'

    @property
    def cached_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.user_id)




class TweetPhoto(models.Model):
    # which tweet that photo belongs to
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)

    # which user upload this photo,
    # faster if we store this directly in the database than retrieving the user from tweet obj.
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    # photo file
    file = models.FileField()
    order = models.IntegerField(default=0)

    # photo status, for the purpose of censorship
    status = models.IntegerField(
        default=TweetPhotoStatus.PENDING,
        choices=TWEET_PHOTO_STATUS_CHOICES,
    )

    # soft delete flag: first mark the photo-to-delete, then delete after awhile
    # purpose: delete will take some time, if delete immediately will affect the user experience,
    # so asynchronize is better
    has_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (
            ('user', 'created_at'),
            ('has_deleted', 'created_at'),
            ('status', 'created_at'),
            ('tweet', 'order'),
        )

    def __str__(self):
        return f'{self.tweet_id}: {self.file}'


post_save.connect(invalidate_object_cache, sender=Tweet)


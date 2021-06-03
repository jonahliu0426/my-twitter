from django.db import models
from django.contrib.auth.models import User
from tweets.models import Tweet


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

    def __str__(self):
        return f'{self.created_at} - {self.user} says {self.content} at tweet {self.tweet_id}'
from django.contrib.auth.models import User
from testing.testcases import TestCase
from tweets.models import Tweet
from datetime import timedelta
from utils.time_helpers import utc_now


class TweetTests(TestCase):

    def setUp(self):
        self.doge = User.objects.create_user(username='doge')
        self.tweet = Tweet.objects.create(user=self.doge, content='Do Only Good Everyday!')

    def test_hours_to_now(self):
        self.tweet.created_at = utc_now() - timedelta(hours=10)
        self.tweet.save()
        self.assertEqual(self.tweet.hours_to_now, 10)

    def test_like_set(self):
        self.create_like(self.doge, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        self.create_like(self.doge, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        shiba = self.create_user('shib')
        self.create_like(shiba, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 2)
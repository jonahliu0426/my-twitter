from django.contrib.auth.models import User
from testing.testcases import TestCase
from tweets.models import Tweet, TweetPhoto
from datetime import timedelta
from utils.time_helpers import utc_now
from tweets.constants import TweetPhotoStatus

class TweetTests(TestCase):

    def setUp(self):
        self.clear_cache()
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

    def test_create_photo(self):
        photo = TweetPhoto.objects.create(
            tweet=self.tweet,
            user=self.doge,
        )
        self.assertEqual(photo.user, self.doge)
        self.assertEqual(photo.status, TweetPhotoStatus.PENDING)
        self.assertEqual(self.tweet.tweetphoto_set.count(), 1)


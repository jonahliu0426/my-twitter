# from django.test import TestCase
from testing.testcases import TestCase
from rest_framework.test import APIClient


COMMENT_URL = '/api/comments/'


# Create your tests here.
class CommentModelTests(TestCase):

    def setUp(self):
        self.comment_test_user2 = self.create_user('comment_test_user2')
        self.comment_test_user2_client = APIClient()
        self.comment_test_user2_client.force_authenticate(self.comment_test_user2)

        self.comment_test_user3 = self.create_user('comment_test_user3')
        self.comment_test_user3_client = APIClient()
        self.comment_test_user3_client.force_authenticate(self.comment_test_user3)

        self.tweet = self.create_tweet(self.comment_test_user2)

    def test_comment(self):
        user1 = self.create_user('comment_test_user1')
        tweet1 = self.create_tweet(user1)
        comment1 = self.create_comment(user1, tweet1)
        self.assertNotEqual(comment1.__str__(), None)

    def test_create(self):
        # Anonymous user cannot create comment
        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 403)

        # No parameter not allowed
        response = self.comment_test_user2_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        # Only tweet_id not allowed
        response = self.comment_test_user2_client.post(COMMENT_URL, {'tweet_id': self.tweet.id})
        self.assertEqual(response.status_code, 400)

        # Only content not allowed
        response = self.comment_test_user2_client.post(COMMENT_URL, {'content': '1'})
        self.assertEqual(response.status_code, 400)

        # Cannot have more than 140 chars
        response = self.comment_test_user2_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1' * 141,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content' in response.data['errors'], True)

        # Must have both 'tweet_id', 'content'
        response = self.comment_test_user2_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1' * 140,
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.comment_test_user2.id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['content'], '1' * 140)


# from django.test import TestCase
from testing.testcases import TestCase
from rest_framework.test import APIClient
from comments.models import Comment
from django.utils import timezone

COMMENT_URL = '/api/comments/'
COMMENT_DETAIL_URL = COMMENT_URL + '{}/'
TWEET_LIST_API = '/api/tweets/'
TWEET_DETAIL_API = '/api/tweets/{}/'
NEWSFEED_LIST_API = '/api/newsfeeds/'


# Create your tests here.
class CommentModelTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.comment_test_user2 = self.create_user('comment_test_user2')
        self.comment_test_user2_client = APIClient()
        self.comment_test_user2_client.force_authenticate(self.comment_test_user2)

        self.comment_test_user3 = self.create_user('comment_test_user3')
        self.comment_test_user3_client = APIClient()
        self.comment_test_user3_client.force_authenticate(self.comment_test_user3)

        self.tweet = self.create_tweet(self.comment_test_user2)
        self.linghu = self.create_user('linghu')
        self.linghu_client = APIClient()
        self.linghu_client.force_authenticate(self.linghu)
        self.dongxie = self.create_user('dongxie')
        self.dongxie_client = APIClient()
        self.dongxie_client.force_authenticate(self.dongxie)

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

    def test_update(self):
        comment = self.create_comment(self.comment_test_user2, self.tweet, 'original')
        another_tweet = self.create_tweet(self.comment_test_user3)
        url = COMMENT_DETAIL_URL.format(comment.id)

        # when use put, anonymous user cannot update
        response = self.anonymous_client.put(url, {'content': 'new'})
        self.assertEqual(response.status_code, 403)

        # cannot update comments posted by other users
        response = self.comment_test_user3_client.put(url, {'content': 'new'})
        self.assertEqual(response.status_code, 403)
        comment.refresh_from_db()
        self.assertNotEqual(comment.content, 'new')

        # cannot update any content except for content,
        before_updated_at = comment.updated_at
        before_created_at = comment.created_at
        now = timezone.now()
        response = self.comment_test_user2_client.put(url, {
            'content': 'new',
            'user_id': self.comment_test_user3.id,
            'tweet_id': another_tweet.id,
            'created_at': now,
        })
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'new')
        self.assertEqual(comment.user, self.comment_test_user2)
        self.assertEqual(comment.tweet, self.tweet)
        self.assertEqual(comment.created_at, before_created_at)
        self.assertNotEqual(comment.created_at, now)
        self.assertNotEqual(comment.updated_at, before_updated_at)
        # self.assertEqual(comment.updated_at, now)

    def test_destroy(self):
        comment = self.create_comment(self.comment_test_user2, self.tweet)
        url = COMMENT_DETAIL_URL.format(comment.id)

        # anonymous user cannot delete
        response = self.anonymous_client.delete(url)
        self.assertEqual(response.status_code, 403)

        # cannot delete comments posted by other users
        response = self.comment_test_user3_client.delete(url)
        self.assertEqual(response.status_code, 403)

        # can delete comments posted by user itself
        count = Comment.objects.count()
        response = self.comment_test_user2_client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), count - 1)

    def test_list(self):
        # must have tweet_id
        response = self.anonymous_client.get(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        # Access allowed with tweet_id
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 0)

        # Test comments are ordered by created time
        self.create_comment(self.comment_test_user2, self.tweet, '1')
        self.create_comment(self.comment_test_user3, self.tweet, '2')
        self.create_comment(self.comment_test_user3, self.create_tweet(self.comment_test_user3), '3')
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
        })
        self.assertEqual(len(response.data['comments']), 2)
        self.assertEqual(response.data['comments'][0]['content'], '1')
        self.assertEqual(response.data['comments'][1]['content'], '2')

        # Test only 'tweet_id' will be applied to filter(),
        # when both 'tweet_id' and 'user_id' are provided in filterset_fields
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'user_id': self.comment_test_user2,
        })
        self.assertEqual(len(response.data['comments']), 2)

    def test_comments_count(self):
        # test tweet detail api
        tweet = self.create_tweet(self.comment_test_user2)
        url = TWEET_DETAIL_API.format(tweet.id)
        response = self.comment_test_user3_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments_count'], 0)

        # test tweet list api
        self.create_comment(self.comment_test_user2, tweet)
        response = self.comment_test_user3_client.get(TWEET_LIST_API, {'user_id': self.comment_test_user2.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['comments_count'], 1)

        # test newsfeeds list api
        self.create_comment(self.comment_test_user3, tweet)
        self.create_newsfeed(self.comment_test_user3, tweet)
        response = self.comment_test_user3_client.get(NEWSFEED_LIST_API)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['tweet']['comments_count'], 2)

    def test_comments_count_with_cache(self):
        tweet_url = '/api/tweets/{}/'.format(self.tweet.id)
        response = self.linghu_client.get(tweet_url)
        self.assertEqual(self.tweet.comments_count, 0)
        self.assertEqual(response.data['comments_count'], 0)

        data = {'tweet_id': self.tweet.id, 'content': 'a comment'}
        for i in range(2):
            _, client = self.create_user_and_client('user{}'.format(i))
            client.post(COMMENT_URL, data)
            response = client.get(tweet_url)
            self.assertEqual(response.data['comments_count'], i + 1)
            self.tweet.refresh_from_db()
            self.assertEqual(self.tweet.comments_count, i + 1)

        comment_data = self.dongxie_client.post(COMMENT_URL, data).data
        response = self.dongxie_client.get(tweet_url)
        self.assertEqual(response.data['comments_count'], 3)
        self.tweet.refresh_from_db()
        self.assertEqual(self.tweet.comments_count, 3)

        # update comment shouldn't update comments_count
        comment_url = '{}{}/'.format(COMMENT_URL, comment_data['id'])
        response = self.dongxie_client.put(comment_url, {'content': 'updated'})
        self.assertEqual(response.status_code, 200)
        response = self.dongxie_client.get(tweet_url)
        self.assertEqual(response.data['comments_count'], 3)
        self.tweet.refresh_from_db()
        self.assertEqual(self.tweet.comments_count, 3)

        # delete a comment will update comments_count
        response = self.dongxie_client.delete(comment_url)
        self.assertEqual(response.status_code, 200)
        response = self.linghu_client.get(tweet_url)
        self.assertEqual(response.data['comments_count'], 2)
        self.tweet.refresh_from_db()
        self.assertEqual(self.tweet.comments_count, 2)

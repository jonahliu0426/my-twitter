from testing.testcases import TestCase


class CommentModelTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.comment_test_user2 = self.create_user('comment_test_user2')
        self.tweet = self.create_tweet(self.comment_test_user2)
        self.comment = self.create_comment(self.comment_test_user2, self.tweet)

    def test_comment(self):
        self.assertNotEqual(self.comment.__str__(), None)

    def test_like_set(self):
        self.comment = self.create_comment(self.comment_test_user2, self.tweet)

        self.create_like(self.comment_test_user2, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        self.create_like(self.comment_test_user2, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        self.comment_test_user3 = self.create_user('comment_test_user3')
        self.create_like(self.comment_test_user3, self.comment)
        self.assertEqual(self.comment.like_set.count(), 2)

        self.create_like(self.comment_test_user3, self.tweet)
        self.assertEqual(self.comment.like_set.count(), 2)

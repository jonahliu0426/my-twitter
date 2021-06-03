# from django.test import TestCase
from testing.testcases import TestCase

# Create your tests here.
class CommentModelTests(TestCase):

    def test_comment(self):
        user1 = self.create_user('comment_test_user1')
        tweet1 = self.create_tweet(user1)
        comment1 = self.create_comment(user1, tweet1)
        self.assertNotEqual(comment1.__str__(), None)

from friendships.services import FriendshipService
from friendships.models import Friendship
from testing.testcases import TestCase


# Create your tests here.
class FriendshipServiceTest(TestCase):

    def setUp(self):
        self.clear_cache()
        self.tom = self.create_user('Tom')
        self.dave = self.create_user('Dave')


    def test_get_followings(self):
        user1 = self.create_user('user1')
        user2 = self.create_user('user2')
        for to_user in [user1, user2, self.tom]:
            Friendship.objects.create(from_user=self.dave, to_user=to_user)
        FriendshipService.invalidate_following_cache(self.dave.id)

        user_id_set = FriendshipService.get_following_user_id_set(self.dave.id)
        self.assertEqual(user_id_set, {user1.id, user2.id, self.tom.id})

        Friendship.objects.filter(from_user=self.dave, to_user=self.tom).delete()
        FriendshipService.invalidate_following_cache(self.dave.id)
        user_id_set = FriendshipService.get_following_user_id_set(self.dave.id)
        self.assertEqual(user_id_set, {user1.id, user2.id})


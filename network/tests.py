# myapp/tests.py
from django.db import IntegrityError
from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import User, Follow, Post


class UserModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", password="testpass1")
        self.user2 = User.objects.create_user(username="testuser2", password="testpass2")
        self.post1 = Post.objects.create(body="Test post 1", user=self.user1)
        self.post2 = Post.objects.create(body="Test post 2", user=self.user2)
        self.follow = Follow.objects.create(follower=self.user1, following=self.user2)

    def test_follower_count_property(self):
        self.assertEqual(self.user2.follower_count, 1)

    def test_follower_empty_count_property(self):
        self.assertEqual(self.user1.follower_count, 0)

    def test_following_count_property(self):
        self.assertEqual(self.user1.following_count, 1)

    def test_following_empty_count_property(self):
        self.assertEqual(self.user2.following_count, 0)

    def test_serialize_method(self):
        serialized_data = self.user1.serialize()
        self.assertEqual(serialized_data["id"], self.user1.id)
        self.assertEqual(serialized_data["username"], self.user1.username)
        self.assertEqual(serialized_data["email"], self.user1.email)
        self.assertEqual(serialized_data["following"], self.user1.following_count)
        self.assertEqual(serialized_data["followers"], self.user1.follower_count)
        self.assertEqual(serialized_data["likes"], [])
        self.assertEqual(serialized_data["posts"], [self.post1.serialize()])

    def test_follow_model_unique_together(self):
        with self.assertRaises(IntegrityError):
            Follow.objects.create(follower=self.user1, following=self.user2)


class FollowModelTest(TestCase):
    def setUp(self):
        # Create some users for testing
        self.user1 = User.objects.create(username="user1")
        self.user2 = User.objects.create(username="user2")
        self.user3 = User.objects.create(username="user3")

    def test_follow_model(self):
        # Test that creating a valid follow relationship works
        follow = Follow.objects.create(follower=self.user1, following=self.user2)
        self.assertEqual(follow.follower, self.user1)
        self.assertEqual(follow.following, self.user2)

    def test_follow_same_user(self):
        # Test that trying to create a follow relationship with the same user raises a ValidationError
        with self.assertRaises(ValidationError):
            Follow.objects.create(follower=self.user1, following=self.user1)

    def test_unique_follow_relationship(self):
        # Test that creating duplicate follow relationships raises a ValidationError
        Follow.objects.create(follower=self.user1, following=self.user2)

        # Attempt to create the same relationship again, should raise a ValidationError
        with self.assertRaises(IntegrityError):
            Follow.objects.create(follower=self.user1, following=self.user2)

    def test_follow_relationship_count(self):
        # Test that the number of followers and following are correct for a user
        Follow.objects.create(follower=self.user1, following=self.user2)
        Follow.objects.create(follower=self.user3, following=self.user2)

        self.assertEqual(self.user2.followers.count(), 2)  # User2 has 2 followers
        self.assertEqual(self.user1.following.count(), 1)  # User1 follows 1 user
        self.assertEqual(self.user3.following.count(), 1)  # User3 follows 1 user


class PostModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", password="testpass1")
        self.post1 = Post.objects.create(body="Test post 1", user=self.user1)

    def test_serialize_method(self):
        serialized_data = self.post1.serialize()
        self.assertEqual(serialized_data["id"], self.post1.id)
        self.assertEqual(serialized_data["body"], self.post1.body)
        self.assertEqual(serialized_data["user"], self.user1.username)
        self.assertEqual(serialized_data["likes"], [])

    def test_get_paginated_posts_all_source(self):
        serialized_posts, _, _, _ = Post.get_paginated_posts(page_number=1, posts_per_page=10)
        self.assertEqual(len(serialized_posts), 1)
        self.assertEqual(serialized_posts[0], self.post1.serialize())

    def test_get_paginated_posts_following_source(self):
        _, _, has_next, has_previous = Post.get_paginated_posts(
            page_number=1, posts_per_page=10, user=self.user1, source="following"
        )
        self.assertFalse(has_next)
        self.assertFalse(has_previous)

    def test_get_paginated_posts_profile_source(self):
        _, _, has_next, has_previous = Post.get_paginated_posts(
            page_number=1, posts_per_page=10, user=self.user1, source="profile"
        )
        self.assertFalse(has_next)
        self.assertFalse(has_previous)

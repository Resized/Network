# myapp/tests.py
from django.db import IntegrityError
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
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
        # Create some users for testing
        self.user1 = User.objects.create(username="user1")
        self.user2 = User.objects.create(username="user2")
        self.user3 = User.objects.create(username="user3")

        # Create some posts for testing
        self.post1 = Post.objects.create(body="Post 1", user=self.user1)
        self.post2 = Post.objects.create(body="Post 2", user=self.user2)
        self.post3 = Post.objects.create(body="Post 3", user=self.user1)
        self.post4 = Post.objects.create(body="Post 4", user=self.user3)

        # force a timestamp
        time_now = timezone.now()
        Post.objects.filter(pk=self.post1.id).update(timestamp=time_now)
        Post.objects.filter(pk=self.post2.id).update(timestamp=time_now - timezone.timedelta(seconds=1))
        Post.objects.filter(pk=self.post3.id).update(timestamp=time_now - timezone.timedelta(seconds=2))
        Post.objects.filter(pk=self.post4.id).update(timestamp=time_now - timezone.timedelta(seconds=3))

    def test_serialize_method(self):
        serialized_data = self.post1.serialize()
        self.assertEqual(serialized_data["id"], self.post1.id)
        self.assertEqual(serialized_data["body"], self.post1.body)
        self.assertEqual(serialized_data["user"], self.user1.username)
        self.assertEqual(serialized_data["likes"], [])

    def test_get_paginated_posts_all_source(self):
        serialized_posts, _, _, _ = Post.get_paginated_posts(page_number=1, posts_per_page=10)
        self.assertEqual(len(serialized_posts), 4)
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

    def test_like_post(self):
        # Test liking a post
        self.post1.likes.add(self.user1)
        self.assertTrue(self.post1.likes.filter(pk=self.user1.pk).exists())

    def test_unlike_post(self):
        # Test unliking a post
        self.post2.likes.add(self.user1)
        self.assertTrue(self.post2.likes.filter(pk=self.user1.pk).exists())

        self.post2.likes.remove(self.user1)
        self.assertFalse(self.post2.likes.filter(pk=self.user1.pk).exists())

    def test_get_liked_posts(self):
        # Test getting posts liked by a user
        self.post1.likes.add(self.user2)
        self.post3.likes.add(self.user2)
        self.post4.likes.add(self.user2)

        liked_posts = Post.get_liked_posts(self.user2)
        self.assertEqual(len(liked_posts), 3)

    def test_post_model_with_likes(self):
        # Test the full model workflow with likes
        self.post1.likes.add(self.user2)
        self.post2.likes.add(self.user3)
        self.post3.likes.add(self.user1)
        self.post3.likes.add(self.user2)

        # Test that the post is correctly serialized with likes
        serialized_data = self.post3.serialize()
        expected_data = {
            "id": self.post3.id,
            "body": "Post 3",
            "user": "user1",
            "timestamp": self.post3.timestamp.strftime("%b %d %Y, %I:%M:%S %p"),
            "likes": ["user1", "user2"]
        }
        self.assertEqual(serialized_data, expected_data)

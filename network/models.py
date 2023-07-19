from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage
from django.db import models


class User(AbstractUser):
    @property
    def follower_count(self):
        return self.followers.count()

    @property
    def following_count(self):
        return self.following.count()

    def __str__(self):
        return f"({self.id}) {self.username}"

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "following": self.following_count,
            "followers": self.follower_count,
            "likes": [post.user.username for post in self.likes.all()],
            "posts": [post.serialize() for post in self.posts.all()]
        }


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")

    def __str__(self):
        return f"{self.id} > {self.follower} is following {self.following}"

    def clean(self):
        if self.follower == self.following:
            raise ValidationError("Follower and following cannot be the same user.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ["follower", "following"]


class Post(models.Model):
    id = models.AutoField(primary_key=True)
    body = models.CharField(max_length=140)
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="posts")
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField("User", related_name="likes", blank=True, null=True)

    def __str__(self):
        return f"{self.user} wrote: {self.body}"

    def serialize(self):
        return {
            "id": self.id,
            "body": self.body,
            "user": self.user.username,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "likes": [user.username for user in self.likes.all()]
        }

    @classmethod
    def get_paginated_posts(cls, page_number, posts_per_page, user=None, source='all'):
        if user and source == 'following':
            following_users = user.following.values_list('following')
            queryset = cls.objects.filter(user__in=following_users).order_by("-timestamp")
        elif user and source == 'profile':
            queryset = cls.objects.filter(user=user).order_by("-timestamp")
        else:
            queryset = cls.objects.all().order_by("-timestamp")
        paginator = Paginator(queryset, posts_per_page)
        total_pages = paginator.num_pages
        try:
            posts = paginator.page(page_number)
        except EmptyPage:
            posts = paginator.page(total_pages)
        serialized_posts = [post.serialize() for post in posts]
        return serialized_posts, total_pages, posts.has_next(), posts.has_previous()

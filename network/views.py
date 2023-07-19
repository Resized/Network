import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import User, Post, Follow


def index(request, username=None):
    context = {
        'user': request.user.username
    }
    return render(request, "network/index.html")


def index_resource(request, resource):
    context = {
        'user': request.user.username,
        'url': resource
    }
    return render(request, "network/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/index.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/index.html")


def posts(request, page=1):
    serialized_posts, total_pages, has_next, has_previous = Post.get_paginated_posts(page, 10, request.user, 'all')
    response_data = {
        'posts': serialized_posts,
        'pagination': {
            'current_page': page,
            'total_pages': total_pages,
            'has_next': has_next,
            'has_previous': has_previous,
        }
    }
    return JsonResponse(response_data, safe=False)


@login_required(login_url='login')
def following(request, page=1):
    serialized_posts, total_pages, has_next, has_previous = Post.get_paginated_posts(page, 10, request.user,
                                                                                     'following')
    response_data = {
        'posts': serialized_posts,
        'pagination': {
            'current_page': page,
            'total_pages': total_pages,
            'has_next': has_next,
            'has_previous': has_previous,
        }
    }
    return JsonResponse(response_data, safe=False)


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    requesting_user = request.user if request.user.is_authenticated else None
    is_following = False

    if requesting_user:
        is_following = Follow.objects.filter(follower=requesting_user, following=profile_user).exists()

    response_data = {
        'user': profile_user.serialize(),
        'is_following': is_following,
    }
    return JsonResponse(response_data, safe=False)


def profile_posts(request, username, page):
    profile_user = get_object_or_404(User, username=username)
    serialized_posts, total_pages, has_next, has_previous = Post.get_paginated_posts(page, 10, profile_user,
                                                                                     'profile')
    response_data = {
        'posts': serialized_posts,
        'pagination': {
            'current_page': page,
            'total_pages': total_pages,
            'has_next': has_next,
            'has_previous': has_previous,
        }
    }

    return JsonResponse(response_data, safe=False)


@login_required(login_url='login')
def follow(request, username):
    if request.method == "POST":
        user_to_follow = User.objects.get(username=username)

        if request.user == user_to_follow:
            return JsonResponse({"message": "You cannot follow yourself."})

        # Check if the user is already being followed
        is_following = user_to_follow.followers.filter(follower=request.user, following=user_to_follow).exists()

        if not is_following:
            # Create a new Follow instance to establish the relationship
            follow = Follow(follower=request.user, following=user_to_follow)
            follow.save()

        return JsonResponse({"message": "Successfully followed."})

    return JsonResponse({"message": "Invalid request method."})


def unfollow(request, username):
    if request.method == "POST":
        user_to_unfollow = User.objects.get(username=username)

        follow_to_delete = user_to_unfollow.followers.filter(follower=request.user, following=user_to_unfollow)
        if follow_to_delete:
            follow_to_delete.delete()

        return JsonResponse({"message": "Successfully unfollowed."})

    return JsonResponse({"message": "Invalid request method."})


@login_required(login_url='login')
def post(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data."}, status=400)

    body = data.get("body")

    if not body:
        return JsonResponse({"error": "Message missing a 'body' parameter."}, status=400)

    max_body_length = Post._meta.get_field("body").max_length

    if len(body) > max_body_length:
        return JsonResponse({"error": f"Post body exceeds the maximum length of {max_body_length} characters."},
                            status=400)

    new_post = Post(
        user=request.user,
        body=body
    )

    try:
        new_post.full_clean()  # Run model validation before saving
    except ValidationError as e:
        return JsonResponse({"error": e.message_dict}, status=400)

    new_post.save()

    return JsonResponse({"message": "Post created successfully."})


def edit_post(request, post_id):
    if request.method != 'POST':
        return JsonResponse({"error": "POST request required."}, status=400)

    post = get_object_or_404(Post, pk=post_id)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data."}, status=400)

    body = data.get("body")

    if not body:
        return JsonResponse({"error": "Message missing a 'body' parameter."}, status=400)

    max_body_length = Post._meta.get_field("body").max_length

    if len(body) > max_body_length:
        return JsonResponse({"error": f"Post body exceeds the maximum length of {max_body_length} characters."},
                            status=400)

    if body == post.body:
        return JsonResponse({"message": "No changes were made to the post."}, status=400)

    if post.user != request.user:
        return JsonResponse({"error": "You are not authorized to edit this post."}, status=403)

    post.body = body

    post.save()

    return JsonResponse({"message": "Post updated successfully."})


def like(request, post_id):
    if request.method != 'POST':
        return JsonResponse({"error": "POST request required."}, status=400)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required."}, status=401)

    post = get_object_or_404(Post, pk=post_id)  # Use get_object_or_404 to retrieve the post or return 404 if not found

    post.likes.add(request.user)
    return JsonResponse({"message": "Post liked successfully."})


def unlike(request, post_id):
    if request.method != 'POST':
        return JsonResponse({"error": "POST request required."}, status=400)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required."}, status=401)

    post = get_object_or_404(Post, pk=post_id)

    if post.likes.filter(pk=request.user.id).exists():
        post.likes.remove(request.user)
        return JsonResponse({"message": "Post unliked successfully."})
    else:
        return JsonResponse({"error": "You have not liked this post."}, status=400)

from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('home', views.index, name='home'),
    path('profile/<str:username>', views.index, name='profile'),
    path('following', views.index, name='following'),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # API
    path("api/post", views.post, name="api_post"),
    path("api/posts", views.posts, name="api_posts"),
    path("api/posts/<int:page>", views.posts, name="api_posts_page"),
    path("api/following", views.following, name="api_following"),
    path("api/following/<int:page>", views.following, name="api_following_page"),
    path("api/profile/<str:username>", views.profile, name="api_profile"),
    path("api/profile/<str:username>/<int:page>", views.profile_posts, name="api_profile_posts_page"),
    path("api/follow/<str:username>", views.follow, name="api_follow"),
    path("api/posts/<int:post_id>/edit", views.edit_post, name="api_edit_post"),
    path("api/like/<int:post_id>", views.like, name="api_like"),
    path("api/unlike/<int:post_id>", views.unlike, name="api_unlike"),
    path("api/unfollow/<str:username>", views.unfollow, name="api_unfollow"),

    # Catch-All
    #path('<path:resource>', views.index_resource, name="index_resource")

]

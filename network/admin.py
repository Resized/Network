from django.contrib import admin

from .models import User, Follow, Post

# Register your models here.

admin.site.register(User)
admin.site.register(Follow)
admin.site.register(Post)

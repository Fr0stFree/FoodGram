from django.conf import settings
from django.contrib import admin

from .models import Follow, UserRole


@admin.register(UserRole)
class UserAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    list_filter = ("role", "user")
    search_fields = ("role", "user")
    empty_value_display = settings.EMPTY_VALUE


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("pk", "follower", "author")
    list_filter = ("follower", "author")
    search_fields = ("author",)
    empty_value_display = settings.EMPTY_VALUE

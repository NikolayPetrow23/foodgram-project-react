from django.contrib import admin
from users.models import Follow, User

IS_EMPTY_MESSAGE = '--пусто--'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "username",
        "email",
        "first_name",
        "last_name",
    )
    search_fields = (
        "username",
        "email",
    )
    list_filter = (
        "username",
        "email",
    )

    empty_value_display = IS_EMPTY_MESSAGE


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        "author",
        "user",
    )
    search_fields = (
        "author",
        "user",
    )
    list_filter = (
        "author",
        "user",
    )

    empty_value_display = IS_EMPTY_MESSAGE

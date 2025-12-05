from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Subscription, User


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'author',
    )
    search_fields = ('user__username', 'author__username')
    list_filter = ('author',)


ADDITIONAL_USER_FIELDS = (
    (None, {'fields': ('avatar',)}),
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    search_fields = ('username', 'email')
    list_filter = ('username', 'email')

    add_fieldsets = BaseUserAdmin.add_fieldsets + ADDITIONAL_USER_FIELDS
    fieldsets = BaseUserAdmin.fieldsets + ADDITIONAL_USER_FIELDS

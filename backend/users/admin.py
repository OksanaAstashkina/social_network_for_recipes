"""Модели приложения users в интерфейсе администратора."""

from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser, Subscription


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Отображение данных модели CustomUser в интерфейсе администратора."""

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name'
    )
    list_filter = (
        'username',
        'email'
    )
    search_fields = (
        'username',
        'email',
        'last_name'
    )
    list_per_page = 50
    empty_value_display = '-пусто-'


@admin.register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    """Отображение данных модели Subscription в интерфейсе администратора."""

    list_display = (
        'subscriber',
        'author'
    )
    list_filter = (
        'subscriber__username',
        'author__username'
    )
    search_fields = (
        'subscriber__username',
        'author__username'
    )
    list_per_page = 50
    empty_value_display = '-пусто-'

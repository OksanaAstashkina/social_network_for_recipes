"""Настройки конфигурации приложения users."""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Класс, конфигурирующий приложение users."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'Пользователи'

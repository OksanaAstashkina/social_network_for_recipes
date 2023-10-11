"""Настройки конфигурации приложения recipes."""

from django.apps import AppConfig


class RecipesConfig(AppConfig):
    """Класс, конфигурирующий приложение recipes."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'
    verbose_name = 'Рецепты'

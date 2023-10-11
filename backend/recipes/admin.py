"""Модели приложения recipes в интерфейсе администратора."""

from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline
from django.forms import BaseInlineFormSet, ValidationError

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    ShoppingCart,
    Tag,
)


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    """Отображение данных модели Tag в админ-зоне."""

    list_display = ('name', 'color', 'slug')
    list_filter = ('name', 'slug')
    search_fields = ('name', 'slug')
    list_per_page = 50
    empty_value_display = '-пусто-'


@admin.register(RecipeTag)
class RecipeTagAdmin(ModelAdmin):
    """Отображение данных модели RecipeTag в админ-зоне."""

    list_display = ('recipe', 'tag')
    list_filter = ('recipe__name', 'tag__name')
    search_fields = ('recipe__name', 'tag__name')
    list_per_page = 50
    empty_value_display = "-пусто-"


class RecipeTagInlineFormset(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if not any(self.errors) and not any(
            obj and not obj['DELETE'] for obj in self.cleaned_data
        ):
            raise ValidationError(
                'Для рецепта необходимо указать хотябы один тег')


class TagsInline(TabularInline):
    """Отображение и редактирование тегов непосредственно в модели Recipe."""

    model = Recipe.tags.through
    formset = RecipeTagInlineFormset
    extra = 5
    min_num = 1


@admin.register(Ingredient)
class IngredientAdmin(ModelAdmin):
    """Отображение данных модели Ingredient в админ-зоне."""

    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)
    list_per_page = 50
    empty_value_display = '-пусто-'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(ModelAdmin):
    """Отображение данных модели RecipeIngredient в админ-зоне."""

    list_display = ('recipe', 'ingredient', 'amount')
    list_filter = ('recipe__name', 'ingredient__name')
    search_fields = ('recipe__name', 'ingredient__name')
    list_per_page = 50
    empty_value_display = "-пусто-"


class RecipeIngredientInlineFormset(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if not any(self.errors) and not any(
            obj and not obj['DELETE'] for obj in self.cleaned_data
        ):
            raise ValidationError(
                'Для рецепта необходимо указать хотябы один ингредиент')


class IngredientsInline(TabularInline):
    """Отображение и редактирование ингредиентов
     непосредственно в модели Recipe."""

    model = Recipe.ingredients.through
    formset = RecipeIngredientInlineFormset
    extra = 5
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(ModelAdmin):
    """Отображение данных модели Recipe в админ-зоне."""

    list_display = ('name', 'author', 'favorites_count')
    list_filter = ('name', 'author__username', 'tags__name')
    readonly_fields = ('favorites_count',)
    search_fields = ('author__username', 'name', 'tags__name')
    date_hierarchy = 'pub_date'
    list_per_page = 50
    empty_value_display = '-пусто-'
    inlines = [TagsInline, IngredientsInline]

    @admin.display(description='Количество добавлений в избранное')
    def favorites_count(self, object):
        """Подсчет количества рецептов в избранном для интерфейса админа."""
        return object.recipes_favorite_related.count()

    @admin.display
    def author_username(self, object):
        """Отображает поле автора рецепта для админа через username."""
        return object.author.username


@admin.register(Favorite)
class FavoriteAdmin(ModelAdmin):
    """Отображение данных модели Favorite в админ-зоне."""

    list_display = ('recipe', 'user')
    list_filter = ('recipe__name', 'user__username')
    search_fields = ('recipe__name', 'user__username')
    list_per_page = 50
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingListAdmin(ModelAdmin):
    """Отображение данных модели Comment в админ-зоне."""

    list_display = ('recipe', 'user')
    list_filter = ('recipe__name', 'user__username')
    search_fields = ('recipe__name', 'user__username')
    list_per_page = 50
    empty_value_display = '-пусто-'

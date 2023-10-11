"""Кастомные фильтры для приложения API."""

from django_filters import (
    AllValuesFilter,
    CharFilter,
    FilterSet,
    ModelMultipleChoiceFilter,
    NumberFilter,
)

from recipes.models import Ingredient, Recipe, Tag

RECIPE_IS_INCLUDED_IN = 1


class RecipeFilter(FilterSet):
    """Фильтр рецептов."""

    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug'
    )
    author = AllValuesFilter(
        field_name="author__id",
    )
    is_favorited = NumberFilter(
        method='recipe_is_favorited',
    )
    is_in_shopping_cart = NumberFilter(
        method='recipe_is_in_shopping_cart',
    )

    class Meta:
        """Поля фильтрации рецептов."""

        fields = (
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
        )
        model = Recipe

    def filter_recipe(self, queryset, name, value, filter_parameters):
        """Фильтрует рецепт в зависимости от переданных параметров."""
        if value == RECIPE_IS_INCLUDED_IN:
            return queryset.filter(**filter_parameters)
        return queryset

    def recipe_is_favorited(self, queryset, name, value):
        """Проверяет наличие рецепта в избранном."""
        favorite_parameters = {
            'recipes_favorite_related__user': self.request.user
        }
        return self.filter_recipe(
            queryset, name, value, favorite_parameters)

    def recipe_is_in_shopping_cart(self, queryset, name, value):
        """Проверяет наличие рецепта в списке покупок."""
        shopping_cart_parameters = {
            'recipes_shoppingcart_related__user': self.request.user
        }
        return self.filter_recipe(
            queryset, name, value, shopping_cart_parameters)


class IngredientFilter(FilterSet):
    """Фильтр ингредиентов."""
    name = CharFilter(lookup_expr='istartswith')

    class Meta:
        """Поля фильтрации ингредиентов."""
        model = Ingredient
        fields = ('name',)

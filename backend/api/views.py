"""Представления для приложения API."""

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthorOrAdmin
from api.serializers import (
    CustomUserSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShoppingCartSerializer,
    ShortRecipeSerializer,
    SubscribeSerializer,
    SubscriptionSerializer,
    TagSerializer,
)
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import CustomUser, Subscription


class CustomUserSubscriptionViewSet(UserViewSet):
    """Вьюсет для моделей CustomUser и Subscription."""

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    filter_backends = (DjangoFilterBackend,)

    @action(
        methods=['get'],
        detail=False,
        url_path='me',
        url_name='me',
        permission_classes=(IsAuthenticated,)
    )
    def get_me(self, request):
        """Возвращает текущему пользователю подробную информацию о нем."""
        me = request.user
        serializer = CustomUserSerializer(
            me, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='subscribe',
        url_name='subscribe',
        permission_classes=(IsAuthenticated,)
    )
    def add_delete_subscribe(self, request, id):
        """Позволяет текущему пользователю подписаться на
         выбранного автора и отписаться от него."""
        subscriber = request.user
        author = get_object_or_404(CustomUser, id=id)
        if request.method == 'POST':
            data = {'subscriber': subscriber.id, 'author': author.id}
            serializer = SubscribeSerializer(
                data=data, context={'request': request, 'author_id': author.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            show_serializer = SubscriptionSerializer(
                author, context={'request': request}
            )
            return Response(
                show_serializer.data, status=status.HTTP_201_CREATED)
        subscription = get_object_or_404(
            Subscription, subscriber=subscriber, author=author
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'],
        detail=False,
        url_path='subscriptions',
        url_name='subscriptions',
        permission_classes=(IsAuthenticated,)
    )
    def get_subscriptions(self, request):
        """Возвращает рецепты авторов, на которых подписан текущий
         пользователь."""
        authors = CustomUser.objects.filter(author__subscriber=request.user)
        pages = self.paginate_queryset(authors)
        serializer = SubscriptionSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет для модели Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для модели Ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeFavoriteShoppingCartViewSet(ModelViewSet):
    """Вьюсет для моделей Recipe, Favorite и ShoppingCart."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeWriteSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Выбор сериализатора данных в зависимости от метода запроса."""
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def get_permissions(self):
        """Выбор разрешенного доступа в зависимости от метода запроса."""
        if self.request.method in SAFE_METHODS:
            return (AllowAny(),)
        if self.request.method == "POST":
            return (IsAuthenticated(),)
        return (IsAuthorOrAdmin(),)

    def perform_create(self, serializer):
        """Назначение автором текущего пользователя при создании объекта."""
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        """Назначение автором текущего пользователя при обновлении объекта."""
        serializer.save(author=self.request.user)

    def recipe__add_in__delete_out(self, request, pk, serializer_name, model):
        """Позволяет текущему пользователю добавить рецепт в список объектов
         передаваемой модели и удалить из него."""
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            data = {'user': user.id, 'recipe': recipe.id}
            serializer = serializer_name(
                data=data, context={'request': request, 'recipe_id': pk}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            show_serializer = ShortRecipeSerializer(
                recipe, context={'request': request})
            return Response(
                show_serializer.data, status=status.HTTP_201_CREATED
            )
        current_recipe = get_object_or_404(
            model, user=user, recipe=recipe
        )
        current_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='favorite',
        url_name='favorite',
        permission_classes=(IsAuthenticated,)
    )
    def add_delete_favorite(self, request, pk):
        """Позволяет текущему пользователю добавить рецепт в избранное
         и удалить из него."""
        return self.recipe__add_in__delete_out(
            request, pk, FavoriteSerializer, Favorite)

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='shopping_cart',
        url_name='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def add_delete_shopping_cart(self, request, pk):
        """Позволяет текущему пользователю добавить рецепт в свой список
         покупок и удалить из него."""
        return self.recipe__add_in__delete_out(
            request, pk, ShoppingCartSerializer, ShoppingCart)

    @action(
        methods=['get'],
        detail=False,
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Позволяет текущему пользователю скачать файл списка покупок."""
        recipes_in_shopping_cart = RecipeIngredient.objects.filter(
            recipe__recipes_shoppingcart_related__user=request.user)
        ingredients = (recipes_in_shopping_cart
                       .values('ingredient__name',
                               'ingredient__measurement_unit')
                       .order_by('ingredient__name')
                       .annotate(total=Sum('amount')))

        result = 'Список покупок с сайта Foodgram:\n\n'
        result += '\n'.join(
            (
                f"{ingredient['ingredient__name']} - {ingredient['total']},"
                f"{ingredient['ingredient__measurement_unit']}"
                for ingredient in ingredients
            )
        )
        response = HttpResponse(result, content_type='text/plain')
        response['Content-Disposition'] = (
            "attachment; filename='shopping-cart.txt'"
        )
        return response

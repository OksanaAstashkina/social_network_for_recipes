"""Эндпойнты для приложения API."""

from django.urls import include, path
from rest_framework import routers

from api.views import (
    CustomUserSubscriptionViewSet,
    IngredientViewSet,
    RecipeFavoriteShoppingCartViewSet,
    TagViewSet,
)

app_name = 'api'

router_version_1 = routers.DefaultRouter()

router_version_1.register(
    'users', CustomUserSubscriptionViewSet, basename='users')
router_version_1.register(
    'tags', TagViewSet, basename='tags')
router_version_1.register(
    'ingredients', IngredientViewSet, basename='ingredients')
router_version_1.register(
    'recipes', RecipeFavoriteShoppingCartViewSet, basename='recipes')

urlpatterns = [
    path('', include(router_version_1.urls)),
    path('auth/', include("djoser.urls.authtoken")),
]

"""Сериализаторы для приложения API."""

from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import (
    IntegerField,
    ModelSerializer,
    SerializerMethodField,
    SlugRelatedField,
    URLField,
)
from rest_framework.validators import ValidationError

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import CustomUser, Subscription


class CustomUserSerializer(UserSerializer):
    """Сериализатор для отображения пользователей."""

    is_subscribed = SerializerMethodField()

    class Meta:
        """Поля сериализации для отображения пользователей."""

        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )
        read_only_fields = ("is_subscribed",)
        model = CustomUser

    def get_is_subscribed(self, object):
        """Проверяет подписку текущего пользователя на выбранного автора."""
        request = self.context['request']
        user = request.user
        if request is None or user.is_anonymous:
            return False
        return object.author.filter(subscriber=user).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователей."""

    class Meta:
        """Поля сериализации для создания пользователей."""

        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        write_only_fields = ("password",)
        model = CustomUser

    def validate(self, data):
        """Валидация данных пользователя."""
        if CustomUser.objects.filter(username=data.get('username')):
            raise ValidationError(
                'Пользователь с таким username уже существует.'
                'Используйте другое пользователькое имя.'
            )
        if CustomUser.objects.filter(email=data.get('email')):
            raise ValidationError(
                'Пользователь с таким email уже существует.'
                'Используйте другую электронную почту.'
            )
        return data


class SubscriptionSerializer(CustomUserSerializer):
    """Сериализатор для отображения подписок."""

    recipes = SerializerMethodField(read_only=True)
    recipes_count = SerializerMethodField(read_only=True)

    class Meta:
        fields = CustomUserSerializer.Meta.fields + (
            'recipes',
            'recipes_count'
        )
        model = CustomUser

    def get_recipes(self, object):
        """Получает рецепты выбранного автора."""
        request = self.context['request']
        recipes_limit = request.query_params.get('recipes_limit')
        queryset = object.recipes.all()
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        serializer = ShortRecipeSerializer(queryset, many=True)
        return serializer.data

    def get_recipes_count(self, object):
        """Получает количество рецептов выбранного автора."""
        return object.recipes.count()


class SubscribeSerializer(ModelSerializer):
    """Сериализатор для создания подписок."""

    class Meta:
        """Поля сериализации для создания подписок."""

        fields = (
            'subscriber',
            'author'
        )
        model = Subscription

    def validate(self, data):
        """Валидация данных подписки."""
        request = self.context['request']
        subscriber = request.user.id
        author = self.context['author_id']
        if request.method == "POST" and subscriber == author:
            raise ValidationError(
                'Вы не можете подписаться на самого себя.'
            )
        if request.method == "POST" and Subscription.objects.filter(
                subscriber=subscriber, author=author).exists():
            raise ValidationError(
                'Вы уже подписаны на этого автора.'
            )
        if (request.method == "DELETE" and not Subscription.objects.filter(
                subscriber=subscriber, author=author).exists()):
            raise ValidationError(
                'Вы не подписаны на этого автора.'
            )
        return data


class TagSerializer(ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        """Поля сериализации тегов."""

        fields = (
            'id',
            'name',
            'color',
            'slug'
        )
        model = Tag


class IngredientSerializer(ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        """Поля сериализации ингредиентов."""

        fields = (
            'id',
            'name',
            'measurement_unit'
        )
        model = Ingredient


class RecipeIngredientReadSerializer(ModelSerializer):
    """Сериализатор ингредиентов в рецепте (режим чтения)."""

    id = PrimaryKeyRelatedField(source='ingredient', read_only=True)
    name = SlugRelatedField(
        source='ingredient', read_only=True, slug_field='name'
    )
    measurement_unit = SlugRelatedField(
        source='ingredient', read_only=True, slug_field='measurement_unit'
    )

    class Meta:
        """Поля сериализации ингредиентов в рецепте (режим чтения)."""

        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )
        model = RecipeIngredient


class RecipeIngredientWriteSerializer(ModelSerializer):
    """Сериализатор ингредиентов в рецепте (режим записи)."""

    id = IntegerField()
    amount = IntegerField(min_value=1)

    class Meta:
        """Поля сериализации ингредиентов в рецепте (режим записи)."""

        fields = (
            'id',
            'amount'
        )
        model = RecipeIngredient


class RecipeReadSerializer(ModelSerializer):
    """Сериализатор рецептов (режим чтения)."""

    ingredients = RecipeIngredientReadSerializer(
        source='recipeingredient_set', many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    image = URLField(source='image.url', read_only=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        """Поля сериализатора рецептов для режима чтения."""

        exclude = ('pub_date',)
        model = Recipe

    def recipe_in(self, obj, model):
        """Проверяет наличие рецепта среди объектов переданной модели."""
        request = self.context['request']
        user = request.user
        if request is None or user.is_anonymous:
            return False
        return model.objects.filter(user=user, recipe=obj).exists()

    def get_is_favorited(self, obj):
        """Проверяет наличие рецепта в избранном."""
        return self.recipe_in(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        """Проверяет наличие рецепта в списке покупок."""
        return self.recipe_in(obj, ShoppingCart)


class RecipeWriteSerializer(RecipeReadSerializer):
    """Сериализатор рецептов (режим записи)."""

    ingredients = RecipeIngredientWriteSerializer(
        source='recipeingredient_set', many=True)
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField(max_length=None,)
    author = None

    class Meta:
        """Поля сериализатора рецептов для режима записи."""

        exclude = ('pub_date', 'author')
        model = Recipe

    def validate(self, attrs):
        """Валидация данных рецепта."""
        tags = self.initial_data['tags']
        cooking_time = self.initial_data['cooking_time']
        ingredients = self.initial_data['ingredients']
        ingredients_id_list = []
        for ingredient in ingredients:
            ingredients_id_list.append(ingredient['id'])
            if int(ingredient['amount']) < 1:
                raise ValidationError(
                    'Необходимо указать количество ингредиента.'
                    'Минимальное количество - 1.'
                )
        if not tags:
            raise ValidationError(
                'У рецепта должен быть указан как минимум один тег.'
            )
        if not ingredients:
            raise ValidationError(
                'В рецепте должен быть указан как минимум один ингредиент.'
            )
        if len(tags) != len(set(tags)):
            raise ValidationError(
                'Вы указали один и тот же тег более одного раза.'
            )
        if len(ingredients_id_list) != len(set(ingredients_id_list)):
            raise ValidationError(
                'Вы указали один и тот же ингредиент более одного раза.'
            )
        if int(cooking_time) < 1:
            raise ValidationError(
                'Необходимо указать время приготовления.'
                'Минимальное время - 1 минута.'
            )
        return attrs

    def _add_tags(self, recipe, tags):
        """Добавляет список тегов в рецепт."""
        for tag in tags:
            recipe.tags.add(tag)
            recipe.save()

    def _add_ingredients(self, recipe, ingredients):
        """Добавляет список ингредиентов в рецепт."""
        data = []
        for ingredient in ingredients:
            data.append(RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            ))
        RecipeIngredient.objects.bulk_create(data)

    def create(self, validated_data):
        """Создание нового рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredient_set')
        recipe = Recipe.objects.create(**validated_data)
        self._add_tags(recipe, tags)
        self._add_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Редактирование объекта."""
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        ingredients = validated_data.pop('recipeingredient_set')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        instance.tags.clear()
        instance.save()
        self._add_ingredients(instance, ingredients)
        self._add_tags(instance, tags)
        return instance

    def to_representation(self, instance):
        """Выбор сериализатора для отображения результата записи."""
        serializer = RecipeReadSerializer(
            instance,
            context={'request': self.context.get('request')}
        )
        return serializer.data


class ShortRecipeSerializer(ModelSerializer):
    """Сериализатор для отображения рецептов в сокращенном виде."""

    class Meta:
        """Поля сериализации отображения рецептов в сокращенном виде."""

        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        read_only_fields = (
            'name',
            'image',
            'cooking_time'
        )
        model = Recipe


class FavoriteSerializer(ModelSerializer):
    """Сериализатор избранного."""

    post_massage = 'Вы уже добавили этот рецепт в избранное'
    delete_massage = 'Этот рецепт отсутствует в избранном'
    Model = Favorite

    class Meta:
        """Поля сериализации избранного."""

        fields = (
            'user',
            'recipe'
        )
        model = Favorite

    def validate(self, data):
        """Валидация данных избранного."""
        request = self.context['request']
        user = request.user
        recipe_id = self.context['recipe_id']
        if (request.method == "POST" and self.Model.objects.filter(
                user=user, recipe_id=recipe_id).exists()):
            raise serializers.ValidationError(self.post_massage)
        if (request.method == "DELETE" and not self.Model.objects.filter(
                user=user, recipe_id=recipe_id).exists()):
            raise serializers.ValidationError(self.delete_massage)
        return data


class ShoppingCartSerializer(FavoriteSerializer):
    """Сериализатор списка покупок."""

    post_massage = 'Вы уже добавили этот рецепт в список покупок'
    delete_massage = 'Этот рецепт отсутствует в списке покупок'
    Model = ShoppingCart

    class Meta:
        """Поля сериализации списка покупок."""

        fields = '__all__'
        model = ShoppingCart

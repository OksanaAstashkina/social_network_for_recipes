"""Описание моделей приложения recipes."""

from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    ForeignKey,
    ImageField,
    IntegerField,
    ManyToManyField,
    Model,
    PositiveSmallIntegerField,
    SlugField,
    TextField,
    UniqueConstraint,
)

from users.models import CustomUser


class Tag(Model):
    """Модель тегов."""
    name = CharField(
        'Название тега',
        max_length=200,
        unique=True
    )
    color = ColorField(
        'Цветовой код HEX',
        default='#FFFFFF',
        unique=True
    )
    slug = SlugField(
        'Уникальный слаг',
        max_length=200,
        unique=True
    )

    class Meta:
        """Общие параметры модели тегов."""

        """
        Определение имени модели тегов и порядка объектов модели
         Tag по умолчанию.
        """
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        """Строковое представление объекта Tag."""
        return f'{self.name}'


class Ingredient(Model):
    """Модель ингредиентов."""

    name = CharField(
        'Название ингредиента',
        max_length=200
    )
    measurement_unit = CharField(
        'Единица измерения',
        max_length=200
    )

    class Meta:
        """Общие параметры модели ингредиентов."""

        """
        Определение имени модели ингредиентов и порядка объектов модели
         Ingredient по умолчанию.
        """

        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']
        constraints = (
            UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_pair_name-measurement_unit'
            ),
        )

    def __str__(self):
        """Строковое представление объекта Ingredient."""
        return f'{self.name}, {self.measurement_unit}'


class Recipe(Model):
    """Модель рецептов."""

    author = ForeignKey(
        CustomUser,
        on_delete=CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = CharField(
        'Название рецепта',
        max_length=200,
        help_text='Введите название рецепта'
    )
    image = ImageField(
        'Фото блюда',
        upload_to='recipes/images/',
        help_text='Загрузите фото блюда'
    )
    text = TextField(
        'Описание рецепта',
        help_text='Введите описание рецепта'
    )
    ingredients = ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты',
        help_text='Выберите ингредиенты для рецепта'
    )
    tags = ManyToManyField(
        Tag,
        through='RecipeTag',
        related_name='recipes',
        verbose_name='Теги',
        help_text='Выберите теги для рецепта'
    )
    cooking_time = PositiveSmallIntegerField(
        'Время приготовления в минутах',
        validators=[
            MinValueValidator(
                1,
                message='Время приготовления должно быть не менее 1 минуты.'
            )
        ],
        help_text='Введите время приготовления блюда в минутах'
    )
    pub_date = DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        """Общие параметры модели рецептов."""

        """
        Определение имени модели подписок и порядка объектов модели
         Recipe по умолчанию.
        """

        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        """Строковое представление объекта Recipe."""
        return f'{self.name}'


class RecipeTag(Model):
    """Связующая рецепты и теги модель."""

    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        verbose_name='Рецепт'
    )
    tag = ForeignKey(
        Tag,
        on_delete=CASCADE,
        verbose_name='Таг'
    )

    class Meta:
        """Общие параметры связующей рецепты и теги модели."""

        """
        Определение имени связующей рецепты и теги модели, порядка объектов
         модели RecipeTag по умолчанию, а также уникальные ограничения
         модели для целостности данных БД.
        """

        verbose_name = 'Тег - Рецепт'
        verbose_name_plural = 'Тег - Рецепт'
        ordering = ['id']
        constraints = (
            UniqueConstraint(
                fields=('recipe', 'tag'),
                name='unique_pair_recipe-tag'
            ),
        )

    def __str__(self):
        """Строковое представление объекта RecipeTag."""
        return f'Тег {self.tag.name} для рецепта {self.recipe.name}'


class RecipeIngredient(Model):
    """Связующая рецепты и ингредиенты модель."""

    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = ForeignKey(
        Ingredient,
        on_delete=CASCADE,
        verbose_name='Ингредиент'
    )
    amount = IntegerField(
        validators=[
            MinValueValidator(
                1,
                message='Количество должно быть не менее 1'
            )
        ]
    )

    class Meta:
        """Общие параметры связующей рецепты и ингредиенты модели."""

        """
        Определение имени связующей рецепты и ингредиенты модели, порядка
         объектов модели RecipeIngredient по умолчанию, а также уникальные
         ограничения модели для целостности данных БД.
        """

        verbose_name = 'Ингредиент - Рецепт'
        verbose_name_plural = 'Ингредиент - Рецепт'
        ordering = ['id']
        constraints = (
            UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_pair_recipe-ingredient'
            ),
        )

    def __str__(self):
        """Строковое представление объекта RecipeIngredient."""
        return (f'Ингредиент {self.ingredient.name}'
                f' для рецепта {self.recipe.name}')


class CommonFavoriteShopingCart(Model):
    """Абстрактная модель с общими параметрами для моделей Favorite
    и ShopingCart."""

    user = ForeignKey(
        CustomUser,
        on_delete=CASCADE,
        related_name='%(app_label)s_%(class)s_related',
        verbose_name='Пользователь'
    )
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='%(app_label)s_%(class)s_related',
        verbose_name='Рецепт'
    )

    class Meta:
        """Общие параметры моделей избранного и списка покупок."""

        """
        Определение имени модели, порядка объектов модели
         по умолчанию, а также уникальные ограничения модели
         для целостности данных БД.
        """

        abstract = True
        ordering = ['id']
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_pair_user_recipe'
            )
        ]


class Favorite(CommonFavoriteShopingCart):
    """Модель избранного."""

    class Meta:
        """Общие параметры модели избранного."""

        """
        Определение имени модели избранного, порядка объектов модели
         Favorite по умолчанию, а также уникальные ограничения модели
         для целостности данных БД.
        """

        verbose_name = 'Избранный'
        verbose_name_plural = 'Избранные'

    def __str__(self):
        """Строковое представление объекта Favorite."""
        return (f'Рецепт {self.recipe.name} в избранном'
                f' у пользователя {self.user.username}')


class ShoppingCart(CommonFavoriteShopingCart):
    """Модель списка покупок."""

    class Meta:
        """Общие параметры модели списка покупок."""

        """
        Определение имени модели списка покупок, порядка объектов модели
         ShoppingCart по умолчанию, а также уникальные ограничения модели
         для целостности данных БД.
        """

        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        """Строковое представление объекта ShoppingCart."""
        return (f'Рецепт {self.recipe.name} в списке покупок'
                f'у пользователя {self.user.username}')

"""Описание моделей приложения users."""

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    EmailField,
    ForeignKey,
    Model,
    UniqueConstraint,
)

from users.validators import validate_username


class CustomUser(AbstractUser):
    """Кастомная модель пользователей."""

    username = CharField(
        'Пользовательское имя',
        max_length=150,
        unique=True,
        db_index=True,
        validators=[validate_username]
    )
    email = EmailField(
        'Адрес электронной почты',
        max_length=254,
        unique=True,
        db_index=True,
    )
    first_name = CharField(
        'Имя',
        max_length=150
    )
    last_name = CharField(
        'Фамилия',
        max_length=150
    )
    is_admin = BooleanField(
        'Администратор',
        default=False
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name'
    )

    class Meta:
        """Общие параметры модели пользователей."""

        """
        Определение имени модели пользователей и порядка объектов
         модели CustomUser по умолчанию.
        """

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        """Строковое представление объекта CustomUser."""
        return f'{self.username}'


class Subscription(Model):
    """Модель подписок."""

    subscriber = ForeignKey(
        CustomUser,
        on_delete=CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
    )
    author = ForeignKey(
        CustomUser,
        on_delete=CASCADE,
        related_name='author',
        verbose_name='Избранный автор',
    )

    class Meta:
        """Общие параметры модели пользователей."""

        """
        Определение имени модели подписок, порядка объектов модели
         CustomUser по умолчанию, а также уникальные и контрольные
         ограничения модели для целостности данных БД.
        """

        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['id']
        constraints = (
            UniqueConstraint(
                fields=['subscriber', 'author'],
                name='unique_pair_subscriber-author',
            ),
        )

    def clean(self):
        if self.subscriber == self.author:
            raise ValidationError(
                'Пара подписчик-автор должна быть уникальна. '
                'Этот пользователь уже подписан на этого автора.'
            )

    def __str__(self):
        """Строковое представление объекта Subscription."""
        return (f'Пользователь {self.subscriber.username} подписан'
                f'на автора {self.author.username}')

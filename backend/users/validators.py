"""Валидаторы для приложения Users."""

import re

from django.core.exceptions import ValidationError


class CustomUserNameValidator:
    """Валидация введенного username."""

    valid_symbols = '@, ., +, -, _'

    def __call__(self, value, pattern_username):
        """Проверка введенного username на наличие недопустимых символов."""
        if re.search(pattern_username, value) is None:
            invalid_symbols_set = set()
            pattern_symbol = r'\w'
            for symbol in value:
                if not re.search(pattern_symbol, symbol) and (
                    symbol not in self.valid_symbols
                ):
                    invalid_symbols_set.add(symbol)
            invalid_symbols = ', '.join(invalid_symbols_set)
            raise ValidationError(
                f'Недопустимые символы в пользовательском имени "{value}". '
                'Допустимы только буквы русского и латинского алфавита в '
                'нижнем и/или верхнем регистре, цифры и следующие символы: '
                f'{self.valid_symbols}. '
                f'Обнаружены следующие недопустимые символы: {invalid_symbols}'
            )
        if value.lower() == 'me':
            raise ValidationError(
                'Username <me> недоступно. '
                'Используйте другое пользователькое имя.'
            )


def validate_username(value):
    """Вызов валдатора username."""
    regex = r'^[\w.@+-]+$'
    CustomUserNameValidator()(value, regex)

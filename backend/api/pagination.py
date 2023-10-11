"""Кастомная пагинация для приложения API."""

from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """Пагинатор, позволяющий пользователю устанавливать
     размер страницы для каждого запроса."""

    page_size_query_param = 'limit'

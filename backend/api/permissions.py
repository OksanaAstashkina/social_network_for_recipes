"""Кастомные пермишены для приложения API."""

from rest_framework.permissions import BasePermission


class IsAuthorOrAdmin(BasePermission):
    """Дает полный доступ администратору и автору объектa."""

    def has_object_permission(self, request, view, obj):
        """Разрешения на уровне запроса и объекта."""
        return (obj.author == request.user
                or request.user.is_superuser
                or request.user.is_staff)

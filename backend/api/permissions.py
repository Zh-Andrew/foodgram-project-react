from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated and request.user.is_staff
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated and request.user.is_staff
        )


class IsAdminOrOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ('POST', 'PATCH', 'PUT'):
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS or request.user.is_superuser:
            return True
        return request.user == obj.author

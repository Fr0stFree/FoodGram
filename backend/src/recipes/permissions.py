from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return request.method in permissions.SAFE_METHODS

        return any(
            [
                request.method in permissions.SAFE_METHODS,
                request.user.userrole.is_admin,
            ]
        )

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return request.method in permissions.SAFE_METHODS

        return any(
            [
                request.method in permissions.SAFE_METHODS,
                request.user.userrole.is_admin,
            ]
        )


class IsAuthorOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and any(
            [
                obj.author == request.user,
                request.user.userrole.is_admin,
            ]
        ):
            return True

        return request.method in permissions.SAFE_METHODS

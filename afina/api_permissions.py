from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrReadOnly(BasePermission):
    """
    Объект можно читать всем (если хочется, оставь только IsAuthenticated),
    но изменять/удалять — только владельцу.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        # у категорий owner может быть None (общие) -> запрещаем изменения не-владельцам
        owner = getattr(obj, 'owner', None)
        return owner == request.user

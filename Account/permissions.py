from rest_framework.permissions import BasePermission,SAFE_METHODS

class IsUser(BasePermission):
    """
    Cho phép truy cập chỉ đối với người dùng có quyền admin.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_staff
class IsOwnerOrReadonly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user
    
class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.has_permission(request)

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_superuser
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
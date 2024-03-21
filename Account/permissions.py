from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    """
    Cho phép truy cập chỉ đối với người dùng có quyền admin.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_staff

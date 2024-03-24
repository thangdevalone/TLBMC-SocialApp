from rest_framework.permissions import BasePermission

class IsUser(BasePermission):
    """
    Cho phép truy cập chỉ đối với người dùng có quyền admin.
    """

    def has_permission(self, request, view):
        return request.user and request.user.id

# permissions.py

from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            # Chỉ cho phép admin thực hiện method POST
            return request.user and request.user.is_superuser
        # Cho phép tất cả người dùng authenticated thực hiện method GET
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Cho phép tất cả các phương thức SAFE_METHODS: GET, HEAD, OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True
        # Chỉ cho phép người dùng chỉnh sửa nếu là người tạo ra khóa học
        return request.user and request.user.is_superuser

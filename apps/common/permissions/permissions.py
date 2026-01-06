from rest_framework.permissions import BasePermission

class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'role') and request.user.role == 'superadmin' and getattr(request.user, 'is_super', True)

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'role') and request.user.role == 'ADMIN'

class IsHR(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'role') and request.user.role == 'HR'

class IsBranchManager(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'role') and request.user.role == 'MANAGER'

class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'role') and request.user.role == 'EMPLOYEE'

class IsAdminOrHR(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'role') and request.user.role in ['ADMIN', 'HR']

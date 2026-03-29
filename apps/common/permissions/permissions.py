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

class IsAdminOrHROrSuperAdmin(BasePermission):
    """
    Permission class for Admin, HR, or SuperAdmin only.
    Allows read access to all authenticated users but restricts write operations.
    """
    def has_permission(self, request, view):
        # Allow read-only access for authenticated users
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user and request.user.is_authenticated
        
        # Check if user has required role for write operations
        if hasattr(request.user, 'role'):
            if request.user.role in ['ADMIN', 'HR']:
                return True
            # Check for superadmin
            if getattr(request.user, 'is_super', False):
                return True
        return False

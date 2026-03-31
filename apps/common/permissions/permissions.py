from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            hasattr(request.user, "role") and request.user.role.upper() == "SUPERADMIN"
        )


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role.upper() == "ADMIN"


class IsHR(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role.upper() == "HR"


class IsBranchManager(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role.upper() == "MANAGER"


class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role.upper() == "EMPLOYEE"


class IsAdminOrHR(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role.upper() in [
            "ADMIN",
            "HR",
        ]


class IsAdminOrHROrSuperAdmin(BasePermission):
    """
    Permission class for Admin, HR, or SuperAdmin only.
    Allows read access to all authenticated users but restricts write operations.
    """

    def has_permission(self, request, view):
        # Allow read-only access for authenticated users
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return request.user and request.user.is_authenticated

        # Check if user has required role for write operations
        if hasattr(request.user, "role"):
            if request.user.role.upper() in ["ADMIN", "HR", "SUPERADMIN"]:
                return True
            # Check for superadmin
            if getattr(request.user, "is_super", False):
                return True
        return False

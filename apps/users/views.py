from apps.common.mixins.abstract_viewset import AbstractViewSet
from apps.common.mixins.company_filter_mixin import CompanyFilterMixin
from apps.common.permissions.permissions import (
    IsSuperAdmin,
    IsBranchManager,
    IsAdminOrHR,
)
from apps.users.serializers.company_serializers import CompanySerializer
from apps.users.serializers.Branch_serializers import BranchSerializer
from apps.users.serializers.employee_serializers import EmployeeSerializer
from apps.users.serializers.users_serializers import UserSerializer
from apps.users.models import Company, User, Branch, Employee
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """
    Returns the current authenticated user's profile
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class UserViewSet(CompanyFilterMixin, AbstractViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSuperAdmin | IsAdminOrHR]

    def perform_create(self, serializer):
        """
        Automatically set company from authenticated user when creating new users
        Only SUPERADMIN can select company, ADMIN/HR must use their own company
        """
        user = self.request.user
        role = serializer.validated_data.get('role', '').upper()
        
        # If authenticated user is not SUPERADMIN, force their company
        if hasattr(user, 'role') and user.role.upper() != 'SUPERADMIN':
            if role != 'SUPERADMIN' and hasattr(user, 'company') and user.company:
                serializer.save(company=user.company)
            else:
                serializer.save()
        else:
            # SUPERADMIN can create users with any company
            serializer.save()

    def get_queryset(self):
        # Handle case where self.request may not exist (e.g., during schema generation)
        if not hasattr(self, "request") or self.request is None:
            return super().get_queryset()
        user = self.request.user

        # CORRECT - superadmin sees all, others see their company only
        if hasattr(user, "role") and user.role.upper() == "SUPERADMIN":
            return User.objects.all()

        # Others see only their company's users
        return User.objects.filter(company=user.company)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Returns the current authenticated user's profile
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=True, methods=["post"], permission_classes=[IsSuperAdmin | IsAdminOrHR]
    )
    def change_role(self, request, pk=None):
        """
        Allows Admin/HR to change the role of a user (including promoting to Branch Manager, etc.)
        """
        user = self.get_object()
        new_role = request.data.get("role")
        allowed_roles = ["SUPERADMIN", "ADMIN", "HR", "MANAGER", "EMPLOYEE"]
        if new_role.upper() not in allowed_roles:
            return Response(
                {"detail": "Invalid role."}, status=status.HTTP_400_BAD_REQUEST
            )
        user.role = new_role
        user.save()
        return Response(
            {"detail": f"User role changed to {new_role}."}, status=status.HTTP_200_OK
        )


class CompanyViewSet(AbstractViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = None
        if hasattr(self, "request") and self.request:
            user_id = self.request.query_params.get("user_id", None)
        if user_id is not None:
            queryset = queryset.filter(users__id=user_id)
        return queryset


class BranchViewSet(CompanyFilterMixin, AbstractViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsSuperAdmin | IsAdminOrHR | IsBranchManager]


class EmployeeViewSet(CompanyFilterMixin, AbstractViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsSuperAdmin | IsAdminOrHR | IsBranchManager]

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        # Only restrict branch manager
        if hasattr(user, "role") and user.role.upper() == "MANAGER":
            try:
                branch = user.employee_profile.branch
                if obj.branch != branch:
                    from rest_framework.exceptions import PermissionDenied

                    raise PermissionDenied(
                        "You do not have permission to access this employee."
                    )
            except Exception:
                from rest_framework.exceptions import PermissionDenied

                raise PermissionDenied(
                    "You do not have permission to access this employee."
                )
        # Employees can only access their own profile
        if hasattr(user, "role") and user.role.upper() == "EMPLOYEE":
            if obj.user != user:
                from rest_framework.exceptions import PermissionDenied

                raise PermissionDenied(
                    "You do not have permission to access this employee."
                )
        return obj

    def get_queryset(self):
        # Handle case where self.request may not exist (e.g., during schema generation)
        if not hasattr(self, "request") or self.request is None:
            return super().get_queryset()
        user = self.request.user
        qs = super().get_queryset()
        # Branch Manager: only see employees in their branch
        if hasattr(user, "role") and user.role.upper() == "MANAGER":
            try:
                branch = user.employee_profile.branch
                if branch:
                    return qs.filter(branch=branch)
                else:
                    return qs.none()
            except Exception:
                return qs.none()
        # Employee: only see their own profile
        if hasattr(user, "role") and user.role.upper() == "EMPLOYEE":
            try:
                return qs.filter(user=user)
            except Exception:
                return qs.none()
        # Admin, SuperAdmin, HR: see all
        return qs

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsSuperAdmin | IsAdminOrHR | IsBranchManager],
    )
    def toggle_status(self, request, pk=None):
        """
        Toggle employee status between ACTIVE and INACTIVE
        """
        employee = self.get_object()

        if employee.employment_status == "ACTIVE":
            employee.employment_status = "INACTIVE"
            message = "Employee status changed to INACTIVE"
        else:
            employee.employment_status = "ACTIVE"
            message = "Employee status changed to ACTIVE"

        employee.save()
        serializer = self.get_serializer(employee)
        return Response(
            {"success": True, "message": message, "data": serializer.data},
            status=status.HTTP_200_OK,
        )

from apps.common.mixins.abstract_viewset import AbstractViewSet
from apps.common.mixins.company_filter_mixin import CompanyFilterMixin
from apps.common.permissions.permissions import (
    IsBranchManager,
    IsSuperAdmin,
    IsAdminOrHR,
)
from apps.department.serializers.department_serializers import DepartmentSerializer

from apps.department.serializers.DesignationSerializer import DesignationSerializer
from apps.department.models import Department, Designation


class DepartmentViewSet(CompanyFilterMixin, AbstractViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsSuperAdmin | IsAdminOrHR | IsBranchManager]


class DesignationViewSet(CompanyFilterMixin, AbstractViewSet):
    queryset = Designation.objects.all()
    serializer_class = DesignationSerializer
    permission_classes = [IsSuperAdmin | IsAdminOrHR | IsBranchManager]

from apps.common.mixins.abstract_viewset import AbstractViewSet
from apps.common.mixins.company_filter_mixin import CompanyFilterMixin
from rest_framework.permissions import IsAuthenticated
from apps.department.serializers.department_serializers import DepartmentSerializer
from apps.department.serializers.DesignationSerializer import DesignationSerializer
from apps.department.models import Department, Designation

class DepartmentViewSet(CompanyFilterMixin, AbstractViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    
    
class DesignationViewSet(CompanyFilterMixin, AbstractViewSet):
    queryset = Designation.objects.all()
    serializer_class = DesignationSerializer
    permission_classes = [IsAuthenticated]
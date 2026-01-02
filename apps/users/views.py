from apps.common.mixins.abstract_viewset import AbstractViewSet
from apps.common.mixins.company_filter_mixin import CompanyFilterMixin
from rest_framework.permissions import IsAuthenticated
from apps.users.serializers.company_serializers import CompanySerializer
from apps.users.serializers.Branch_serializers import BranchSerializer
from apps.users.serializers.employee_serializers import EmployeeSerializer
from apps.users.serializers.users_serializers import UserSerializer
from apps.users.models import (
    Company, User, Branch, Employee
)

class UserViewSet(CompanyFilterMixin, AbstractViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = []
    
    
class CompanyViewSet(AbstractViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

def get_queryset(self):
    queryset = super().get_queryset()
    user_id = None
    if hasattr(self, "request") and self.request:
        user_id = self.request.query_params.get('user_id', None)
    if user_id is not None:
        queryset = queryset.filter(users__id=user_id)
    return queryset
    
    
class BranchViewSet(CompanyFilterMixin, AbstractViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = []


class EmployeeViewSet(CompanyFilterMixin, AbstractViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = []
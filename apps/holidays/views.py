from apps.holidays.models import Holiday
from apps.holidays.serializers import (
    HolidaySerializer,
    HolidayListSerializer,
    HolidayCreateUpdateSerializer,
)
from apps.common.mixins.abstract_viewset import AbstractViewSet
from rest_framework.permissions import IsAuthenticated
from apps.common.mixins.company_filter_mixin import CompanyFilterMixin
from apps.common.permissions.permissions import IsAdminOrHROrSuperAdmin


class HolidayViewSet(AbstractViewSet, CompanyFilterMixin):
    """
    ViewSet for managing Holiday records
    Only Admin, HR, and SuperAdmin can create/update/delete holidays
    All authenticated users can view holidays
    """

    queryset = Holiday.objects.select_related(
        "branch", "created_by", "updated_by"
    ).all()
    serializer_class = HolidaySerializer
    filterset_fields = ["branch", "date"]
    search_fields = ["name", "description"]
    ordering_fields = ["date", "name", "created_at"]
    ordering = ["date"]

    def get_permissions(self):
        """
        Allow all authenticated users to view holidays
        Only Admin/HR/SuperAdmin can modify
        """
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminOrHROrSuperAdmin()]

    def get_serializer_class(self):
        """
        Return different serializers for different actions
        """
        if self.action == "list":
            return HolidayListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return HolidayCreateUpdateSerializer
        return HolidaySerializer

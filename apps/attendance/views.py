from apps.attendance.models import Attendance, FingerprintScan
from apps.attendance.serializers.Attendance_serializers import (
    AttendanceSerializer,
    AttendanceListSerializer,
    AttendanceCreateUpdateSerializer,
    FingerprintScanSerializer,
    FingerprintScanListSerializer,
)
from apps.common.mixins.abstract_viewset import AbstractViewSet
from rest_framework.permissions import IsAuthenticated
from apps.common.mixins.company_filter_mixin import CompanyFilterMixin
from apps.common.permissions.permissions import IsAdminOrHROrSuperAdmin


class AttendanceViewSet(AbstractViewSet, CompanyFilterMixin):
    """
    ViewSet for managing Attendance records
    Only Admin, HR, and SuperAdmin can create/update/delete attendance records
    """

    queryset = Attendance.objects.select_related(
        "employee", "check_in_scan", "check_out_scan", "created_by", "updated_by"
    ).all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated, IsAdminOrHROrSuperAdmin]
    filterset_fields = ["employee", "date", "status"]
    search_fields = ["employee__name", "employee__employee_id"]
    ordering_fields = ["date", "check_in", "check_out"]
    ordering = ["-date"]

    def get_serializer_class(self):
        """
        Return different serializers for different actions
        """
        if self.action == "list":
            return AttendanceListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return AttendanceCreateUpdateSerializer
        return AttendanceSerializer


class FingerprintScanViewSet(AbstractViewSet, CompanyFilterMixin):
    """
    ViewSet for managing Fingerprint Scan records
    """

    queryset = FingerprintScan.objects.select_related("employee", "attendance").all()
    serializer_class = FingerprintScanSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["employee", "scan_type", "scan_status", "device_id"]
    search_fields = ["employee__name", "employee__employee_id", "device_id"]
    ordering_fields = ["scan_time"]
    ordering = ["-scan_time"]

    def get_serializer_class(self):
        """
        Return different serializers for different actions
        """
        if self.action == "list":
            return FingerprintScanListSerializer
        return FingerprintScanSerializer

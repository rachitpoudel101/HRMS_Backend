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
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import date


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

    def get_permissions(self):
        """
        Allow all authenticated users to check-in/check-out and view their own status
        """
        if self.action in [
            "check_in",
            "check_out",
            "my_status",
            "my_attendance",
            "calendar_view",
        ]:
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=["post"], url_path="check-in")
    def check_in(self, request):
        """
        Automatic check-in for the current user's employee
        Creates or updates today's attendance record
        """
        try:
            employee = request.user.employee_profile
        except AttributeError:
            return Response(
                {"error": "No employee profile found for this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        today = date.today()
        now = timezone.now()

        # Check if attendance record already exists for today
        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={
                "check_in": now,
                "status": Attendance.EmployeeStatus.PRESENT,
                "created_by": request.user,
            },
        )

        if not created:
            if attendance.check_in:
                return Response(
                    {
                        "error": "Already checked in today",
                        "check_in": attendance.check_in,
                        "attendance_id": attendance.id,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            attendance.check_in = now
            attendance.status = Attendance.EmployeeStatus.PRESENT
            attendance.updated_by = request.user
            attendance.save()

        # Create fingerprint scan record
        device_id = request.data.get("device_id", "web_app")
        scan = FingerprintScan.objects.create(
            employee=employee,
            scan_type=FingerprintScan.scanType.IN,
            device_id=device_id,
            scan_status=FingerprintScan.scanStatus.SUCCESS,
            attendance=attendance,
        )
        attendance.check_in_scan = scan
        attendance.save()

        serializer = AttendanceSerializer(attendance)
        return Response(
            {"message": "Checked in successfully", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="check-out")
    def check_out(self, request):
        """
        Automatic check-out for the current user's employee
        Updates today's attendance record
        """
        try:
            employee = request.user.employee_profile
        except AttributeError:
            return Response(
                {"error": "No employee profile found for this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        today = date.today()
        now = timezone.now()

        # Get today's attendance record
        try:
            attendance = Attendance.objects.get(employee=employee, date=today)
        except Attendance.DoesNotExist:
            return Response(
                {"error": "No check-in record found for today. Please check in first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if already checked out
        if attendance.check_out:
            return Response(
                {
                    "error": "Already checked out today",
                    "check_out": attendance.check_out,
                    "attendance_id": attendance.id,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if checked in
        if not attendance.check_in:
            return Response(
                {"error": "Cannot check out without checking in first"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update check-out time
        attendance.check_out = now
        attendance.updated_by = request.user
        attendance.save()

        # Create fingerprint scan record
        device_id = request.data.get("device_id", "web_app")
        scan = FingerprintScan.objects.create(
            employee=employee,
            scan_type=FingerprintScan.scanType.OUT,
            device_id=device_id,
            scan_status=FingerprintScan.scanStatus.SUCCESS,
            attendance=attendance,
        )
        attendance.check_out_scan = scan
        attendance.save()

        serializer = AttendanceSerializer(attendance)
        return Response(
            {"message": "Checked out successfully", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="my-status")
    def my_status(self, request):
        """
        Get current user's attendance status for today
        """
        try:
            employee = request.user.employee_profile
        except AttributeError:
            return Response(
                {"error": "No employee profile found for this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        today = date.today()
        try:
            attendance = Attendance.objects.get(employee=employee, date=today)
            serializer = AttendanceSerializer(attendance)
            return Response(
                {
                    "has_checked_in": bool(attendance.check_in),
                    "has_checked_out": bool(attendance.check_out),
                    "attendance": serializer.data,
                }
            )
        except Attendance.DoesNotExist:
            return Response(
                {"has_checked_in": False, "has_checked_out": False, "attendance": None}
            )

    @action(detail=False, methods=["get"], url_path="my-attendance")
    def my_attendance(self, request):
        """
        Get current user's attendance history
        Supports filtering by date range and pagination
        """
        try:
            employee = request.user.employee_profile
        except AttributeError:
            return Response(
                {"error": "No employee profile found for this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get query parameters
        start_date = request.query_params.get("start_date", None)
        end_date = request.query_params.get("end_date", None)
        page_size = request.query_params.get("page_size", 10)

        # Filter attendance records for this employee
        queryset = Attendance.objects.filter(employee=employee).select_related(
            "check_in_scan", "check_out_scan"
        )

        # Apply date filters if provided
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        # Order by date descending (most recent first)
        queryset = queryset.order_by("-date")

        # Paginate the results
        from rest_framework.pagination import PageNumberPagination

        paginator = PageNumberPagination()
        paginator.page_size = page_size
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = AttendanceListSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=False, methods=["get"], url_path="calendar-view")
    def calendar_view(self, request):
        """
        Get attendance data for calendar view
        Returns attendance records from employee's joining date to current date
        Optimized for calendar display with check-in/check-out times
        """
        try:
            employee = request.user.employee_profile
        except AttributeError:
            return Response(
                {"error": "No employee profile found for this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get query parameters for month/year filter (optional)
        month = request.query_params.get("month", None)
        year = request.query_params.get("year", None)

        # Start from joining date
        start_date = employee.date_of_joining
        end_date = date.today()

        # If month and year provided, filter for that specific month
        if month and year:
            try:
                month = int(month)
                year = int(year)
                start_date = date(year, month, 1)
                # Get last day of month
                if month == 12:
                    end_date = date(year + 1, 1, 1)
                else:
                    end_date = date(year, month + 1, 1)
                from datetime import timedelta

                end_date = end_date - timedelta(days=1)
            except (ValueError, TypeError):
                return Response(
                    {"error": "Invalid month or year format"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Get all attendance records for the date range
        attendance_records = Attendance.objects.filter(
            employee=employee, date__gte=start_date, date__lte=end_date
        ).select_related("check_in_scan", "check_out_scan")

        # Create a dictionary for easy lookup by date
        attendance_dict = {}
        for record in attendance_records:
            attendance_dict[record.date.isoformat()] = {
                "id": record.id,
                "date": record.date.isoformat(),
                "status": record.status,
                "check_in": record.check_in.isoformat() if record.check_in else None,
                "check_out": record.check_out.isoformat() if record.check_out else None,
                "check_in_time": (
                    record.check_in.strftime("%I:%M %p") if record.check_in else None
                ),
                "check_out_time": (
                    record.check_out.strftime("%I:%M %p") if record.check_out else None
                ),
            }

        # Calculate summary statistics
        total_days = (end_date - start_date).days + 1
        present_days = attendance_records.filter(
            status=Attendance.EmployeeStatus.PRESENT
        ).count()
        absent_days = attendance_records.filter(
            status=Attendance.EmployeeStatus.ABSENT
        ).count()
        on_leave_days = attendance_records.filter(
            status=Attendance.EmployeeStatus.ON_LEAVE
        ).count()
        wfh_days = attendance_records.filter(
            status=Attendance.EmployeeStatus.WORK_FROM_HOME
        ).count()

        return Response(
            {
                "employee_id": employee.employee_id,
                "employee_name": employee.name,
                "joining_date": employee.date_of_joining.isoformat(),
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "summary": {
                    "total_days": total_days,
                    "present_days": present_days,
                    "absent_days": absent_days,
                    "on_leave_days": on_leave_days,
                    "work_from_home_days": wfh_days,
                    "attendance_percentage": (
                        round((present_days / total_days) * 100, 2)
                        if total_days > 0
                        else 0
                    ),
                },
                "attendance": attendance_dict,
            }
        )


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

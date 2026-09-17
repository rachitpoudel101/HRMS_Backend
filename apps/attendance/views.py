from apps.attendance.models import Attendance
from apps.attendance.serializers.Attendance_serializers import (
    AttendanceSerializer,
    AttendanceListSerializer,
    AttendanceCreateUpdateSerializer,
    AttendanceApprovalSerializer,
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
    - Employees can clock in/out and view their own attendance
    - Managers can approve timesheets for their team members
    - Admin/HR can manage all attendance records
    """

    queryset = Attendance.objects.select_related(
        "employee", "created_by", "updated_by", "approved_by"
    ).all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated, IsAdminOrHROrSuperAdmin]
    filterset_fields = ["employee", "date", "status", "is_approved"]
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
        elif self.action in ["approve_timesheet", "bulk_approve"]:
            return AttendanceApprovalSerializer
        return AttendanceSerializer

    def get_permissions(self):
        """
        Allow all authenticated users to check-in/check-out and view their own status
        Managers can approve timesheets
        """
        if self.action in [
            "check_in",
            "check_out",
            "my_status",
            "my_attendance",
            "calendar_view",
        ]:
            return [IsAuthenticated()]
        elif self.action in [
            "approve_timesheet",
            "bulk_approve",
            "pending_approvals",
            "team_attendance",
        ]:
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=["post"], url_path="check-in")
    def check_in(self, request):
        """
        Simple check-in for the current user's employee
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
                        "success": False,
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

        serializer = AttendanceSerializer(attendance)
        return Response(
            {
                "success": True,
                "message": "Checked in successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="check-out")
    def check_out(self, request):
        """
        Simple check-out for the current user's employee
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
                {
                    "success": False,
                    "error": "No check-in record found for today. Please check in first.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if already checked out
        if attendance.check_out:
            return Response(
                {
                    "success": False,
                    "error": "Already checked out today",
                    "check_out": attendance.check_out,
                    "attendance_id": attendance.id,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if checked in
        if not attendance.check_in:
            return Response(
                {
                    "success": False,
                    "error": "Cannot check out without checking in first",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update check-out time
        attendance.check_out = now
        attendance.updated_by = request.user
        attendance.save()

        serializer = AttendanceSerializer(attendance)
        return Response(
            {
                "success": True,
                "message": "Checked out successfully",
                "data": serializer.data,
            },
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
        Get current user's attendance history (READ ONLY)
        Supports filtering by date range and pagination
        Employees can only view, not edit their attendance
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
            "approved_by"
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
        ).select_related("approved_by")

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
                "is_approved": record.is_approved,
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

    @action(detail=True, methods=["post"], url_path="approve")
    def approve_timesheet(self, request, pk=None):
        """
        Approve a specific attendance record
        Managers can approve their team members' attendance
        Admin/HR can approve any attendance
        """
        attendance = self.get_object()

        # Check if already approved
        if attendance.is_approved:
            return Response(
                {
                    "success": False,
                    "error": "This attendance record is already approved",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check permissions
        try:
            employee = request.user.employee_profile
            # Check if user is admin/HR or the manager of this employee
            user_role = request.user.role
            is_admin_or_hr = user_role in ["ADMIN", "HR", "SUPERADMIN"]
            is_manager = (
                attendance.employee.manager
                and attendance.employee.manager.id == employee.id
            )

            if not (is_admin_or_hr or is_manager):
                return Response(
                    {
                        "success": False,
                        "error": "You do not have permission to approve this attendance",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
        except AttributeError:
            return Response(
                {"error": "No employee profile found for this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Approve the attendance
        attendance.is_approved = True
        attendance.approved_by = request.user
        attendance.approved_at = timezone.now()
        attendance.save()

        serializer = AttendanceSerializer(attendance)
        return Response(
            {
                "success": True,
                "message": "Attendance approved successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="bulk-approve")
    def bulk_approve(self, request):
        """
        Bulk approve multiple attendance records
        Request body: {"attendance_ids": [1, 2, 3, ...]}
        """
        attendance_ids = request.data.get("attendance_ids", [])

        if not attendance_ids:
            return Response(
                {"error": "No attendance IDs provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get attendance records
        attendances = Attendance.objects.filter(
            id__in=attendance_ids, is_approved=False
        )

        # Check permissions for each record
        try:
            employee = request.user.employee_profile
            user_role = request.user.role
            is_admin_or_hr = user_role in ["ADMIN", "HR", "SUPERADMIN"]

            approved_count = 0
            for attendance in attendances:
                is_manager = (
                    attendance.employee.manager
                    and attendance.employee.manager.id == employee.id
                )

                if is_admin_or_hr or is_manager:
                    attendance.is_approved = True
                    attendance.approved_by = request.user
                    attendance.approved_at = timezone.now()
                    attendance.save()
                    approved_count += 1

        except AttributeError:
            return Response(
                {"error": "No employee profile found for this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "success": True,
                "message": f"Approved {approved_count} attendance records",
                "approved_count": approved_count,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="pending-approvals")
    def pending_approvals(self, request):
        """
        Get all pending attendance approvals for the manager
        Shows team members' unapproved attendance records
        """
        try:
            employee = request.user.employee_profile
            user_role = request.user.role
            is_admin_or_hr = user_role in ["ADMIN", "HR", "SUPERADMIN"]

            if is_admin_or_hr:
                # Admin/HR can see all pending approvals
                queryset = Attendance.objects.filter(is_approved=False)
            else:
                # Managers see their team's pending approvals
                queryset = Attendance.objects.filter(
                    employee__manager=employee, is_approved=False
                )

            # Apply date filters if provided
            start_date = request.query_params.get("start_date", None)
            end_date = request.query_params.get("end_date", None)

            if start_date:
                queryset = queryset.filter(date__gte=start_date)
            if end_date:
                queryset = queryset.filter(date__lte=end_date)

            queryset = queryset.select_related("employee").order_by("-date")

            serializer = AttendanceListSerializer(queryset, many=True)
            return Response(
                {"count": queryset.count(), "results": serializer.data},
                status=status.HTTP_200_OK,
            )

        except AttributeError:
            return Response(
                {"error": "No employee profile found for this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["get"], url_path="team-attendance")
    def team_attendance(self, request):
        """
        Get attendance records for team members (for managers)
        Admin/HR can see all attendance
        """
        try:
            employee = request.user.employee_profile
            user_role = request.user.role
            is_admin_or_hr = user_role in ["ADMIN", "HR", "SUPERADMIN"]

            if is_admin_or_hr:
                # Admin/HR can see all attendance
                queryset = Attendance.objects.all()
            else:
                # Managers see their team's attendance
                queryset = Attendance.objects.filter(employee__manager=employee)

            # Apply filters
            employee_id = request.query_params.get("employee", None)
            start_date = request.query_params.get("start_date", None)
            end_date = request.query_params.get("end_date", None)
            approval_status = request.query_params.get("is_approved", None)

            if employee_id:
                queryset = queryset.filter(employee_id=employee_id)
            if start_date:
                queryset = queryset.filter(date__gte=start_date)
            if end_date:
                queryset = queryset.filter(date__lte=end_date)
            if approval_status is not None:
                is_approved = approval_status.lower() == "true"
                queryset = queryset.filter(is_approved=is_approved)

            queryset = queryset.select_related("employee", "approved_by").order_by(
                "-date"
            )

            # Paginate
            from rest_framework.pagination import PageNumberPagination

            paginator = PageNumberPagination()
            paginator.page_size = request.query_params.get("page_size", 20)
            paginated_queryset = paginator.paginate_queryset(queryset, request)

            serializer = AttendanceListSerializer(paginated_queryset, many=True)
            return paginator.get_paginated_response(serializer.data)

        except AttributeError:
            return Response(
                {"error": "No employee profile found for this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

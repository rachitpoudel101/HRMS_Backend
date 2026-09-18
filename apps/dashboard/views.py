from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import date, timedelta
from apps.attendance.models import Attendance
from apps.users.models import Employee
from apps.notice.models import Notic
from apps.holidays.models import Holiday


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_activities(request):
    """
    Dashboard activities endpoint
    Returns summary of recent activities, pending approvals, and statistics
    """
    try:
        user = request.user
        employee = user.employee_profile
        user_role = user.role
        is_admin_or_hr = user_role in ["ADMIN", "HR", "SUPERADMIN"]
        is_manager = user_role == "MANAGER"

        today = date.today()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        # Initialize response data
        data = {
            "user": {
                "name": employee.name,
                "employee_id": employee.employee_id,
                "role": user_role,
                "department": employee.department.name if employee.department else None,
                "designation": (
                    employee.designation.name if employee.designation else None
                ),
            },
            "today_status": {},
            "statistics": {},
            "recent_activities": [],
            "pending_approvals": {},
            "upcoming_events": {},
        }

        # 1. Today's attendance status for current user
        try:
            today_attendance = Attendance.objects.get(employee=employee, date=today)
            data["today_status"] = {
                "has_checked_in": bool(today_attendance.check_in),
                "has_checked_out": bool(today_attendance.check_out),
                "check_in_time": (
                    today_attendance.check_in.strftime("%I:%M %p")
                    if today_attendance.check_in
                    else None
                ),
                "check_out_time": (
                    today_attendance.check_out.strftime("%I:%M %p")
                    if today_attendance.check_out
                    else None
                ),
                "status": today_attendance.status,
                "is_approved": today_attendance.is_approved,
            }
        except Attendance.DoesNotExist:
            data["today_status"] = {
                "has_checked_in": False,
                "has_checked_out": False,
                "check_in_time": None,
                "check_out_time": None,
                "status": None,
                "is_approved": False,
            }

        # 2. Attendance Statistics
        if is_admin_or_hr:
            # Admin/HR sees company-wide stats
            total_employees = Employee.objects.filter(is_active=True).count()
            today_present = Attendance.objects.filter(
                date=today, status=Attendance.EmployeeStatus.PRESENT
            ).count()
            today_absent = Attendance.objects.filter(
                date=today, status=Attendance.EmployeeStatus.ABSENT
            ).count()
            today_on_leave = Attendance.objects.filter(
                date=today, status=Attendance.EmployeeStatus.ON_LEAVE
            ).count()
            today_wfh = Attendance.objects.filter(
                date=today, status=Attendance.EmployeeStatus.WORK_FROM_HOME
            ).count()

            data["statistics"] = {
                "total_employees": total_employees,
                "today_present": today_present,
                "today_absent": today_absent,
                "today_on_leave": today_on_leave,
                "today_wfh": today_wfh,
                "attendance_rate": (
                    round((today_present / total_employees) * 100, 1)
                    if total_employees > 0
                    else 0
                ),
            }
        elif is_manager:
            # Manager sees team stats
            team_members = Employee.objects.filter(manager=employee, is_active=True)
            total_team = team_members.count()
            today_present = Attendance.objects.filter(
                employee__in=team_members,
                date=today,
                status=Attendance.EmployeeStatus.PRESENT,
            ).count()

            data["statistics"] = {
                "total_team_members": total_team,
                "today_present": today_present,
                "team_attendance_rate": (
                    round((today_present / total_team) * 100, 1)
                    if total_team > 0
                    else 0
                ),
            }
        else:
            # Regular employee sees personal stats
            month_attendance = Attendance.objects.filter(
                employee=employee, date__gte=month_ago, date__lte=today
            )
            total_days = month_attendance.count()
            present_days = month_attendance.filter(
                status=Attendance.EmployeeStatus.PRESENT
            ).count()

            data["statistics"] = {
                "monthly_attendance_days": total_days,
                "monthly_present_days": present_days,
                "monthly_attendance_rate": (
                    round((present_days / total_days) * 100, 1) if total_days > 0 else 0
                ),
            }

        # 3. Recent Activities (Last 7 days)
        if is_admin_or_hr:
            recent_attendance = Attendance.objects.filter(
                date__gte=week_ago
            ).select_related("employee", "approved_by")[:10]
        elif is_manager:
            recent_attendance = Attendance.objects.filter(
                employee__manager=employee, date__gte=week_ago
            ).select_related("employee", "approved_by")[:10]
        else:
            recent_attendance = Attendance.objects.filter(
                employee=employee, date__gte=week_ago
            ).select_related("approved_by")[:10]

        activities = []
        for att in recent_attendance:
            activities.append(
                {
                    "id": att.id,
                    "type": "attendance",
                    "employee_name": att.employee.name,
                    "employee_id": att.employee.employee_id,
                    "date": att.date.isoformat(),
                    "check_in": att.check_in.isoformat() if att.check_in else None,
                    "check_out": att.check_out.isoformat() if att.check_out else None,
                    "status": att.status,
                    "is_approved": att.is_approved,
                    "approved_by": (
                        att.approved_by.username if att.approved_by else None
                    ),
                }
            )

        data["recent_activities"] = activities

        # 4. Pending Approvals (for managers and admins)
        if is_admin_or_hr or is_manager:
            if is_admin_or_hr:
                pending = Attendance.objects.filter(is_approved=False)
            else:
                pending = Attendance.objects.filter(
                    employee__manager=employee, is_approved=False
                )

            pending_count = pending.count()
            pending_today = pending.filter(date=today).count()
            pending_this_week = pending.filter(date__gte=week_ago).count()

            data["pending_approvals"] = {
                "total_pending": pending_count,
                "pending_today": pending_today,
                "pending_this_week": pending_this_week,
                "pending_list": [
                    {
                        "id": att.id,
                        "employee_name": att.employee.name,
                        "employee_id": att.employee.employee_id,
                        "date": att.date.isoformat(),
                        "check_in": att.check_in.isoformat() if att.check_in else None,
                        "check_out": att.check_out.isoformat()
                        if att.check_out
                        else None,
                    }
                    for att in pending.select_related("employee")[:5]
                ],
            }

        # 5. Upcoming Events (Holidays and Notices)
        # Get upcoming holidays
        upcoming_holidays = Holiday.objects.filter(date__gte=today).order_by("date")[:5]
        data["upcoming_events"]["holidays"] = [
            {
                "id": holiday.id,
                "title": holiday.title,
                "date": holiday.date.isoformat(),
                "holiday_type": holiday.holiday_type,
            }
            for holiday in upcoming_holidays
        ]

        # Get recent notices
        try:
            recent_notices = Notic.objects.filter(deleted_at__isnull=True).order_by(
                "-created_at"
            )[:5]
            data["upcoming_events"]["notices"] = [
                {
                    "id": notice.id,
                    "name": notice.name,
                    "date": notice.date.isoformat(),
                    "created_at": notice.created_at.isoformat(),
                }
                for notice in recent_notices
            ]
        except Exception:
            data["upcoming_events"]["notices"] = []

        return Response(data, status=status.HTTP_200_OK)

    except AttributeError:
        return Response(
            {"error": "No employee profile found for this user"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    """
    Dashboard summary endpoint - lightweight version
    Returns only essential statistics
    """
    try:
        user = request.user
        employee = user.employee_profile
        user_role = user.role
        is_admin_or_hr = user_role in ["ADMIN", "HR", "SUPERADMIN"]

        today = date.today()

        # Today's status
        today_attendance = None
        try:
            today_attendance = Attendance.objects.get(employee=employee, date=today)
        except Attendance.DoesNotExist:
            pass

        data = {
            "has_checked_in": bool(today_attendance and today_attendance.check_in),
            "has_checked_out": bool(today_attendance and today_attendance.check_out),
            "check_in_time": (
                today_attendance.check_in.strftime("%I:%M %p")
                if today_attendance and today_attendance.check_in
                else None
            ),
        }

        # Add pending approvals count for managers/admins
        if is_admin_or_hr:
            pending_count = Attendance.objects.filter(is_approved=False).count()
            data["pending_approvals"] = pending_count
        elif user_role == "MANAGER":
            pending_count = Attendance.objects.filter(
                employee__manager=employee, is_approved=False
            ).count()
            data["pending_approvals"] = pending_count

        return Response(data, status=status.HTTP_200_OK)

    except AttributeError:
        return Response(
            {"error": "No employee profile found for this user"},
            status=status.HTTP_400_BAD_REQUEST,
        )

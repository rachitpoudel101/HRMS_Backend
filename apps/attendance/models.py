from django.db import models
from django.conf import settings
from apps.common.models import (
    BaseTimeStampModelMixin,
    SoftDeleteModelMixin,
    BaseAuditModelMixin,
)
from apps.users.models import Employee


class Attendance(BaseTimeStampModelMixin, SoftDeleteModelMixin, BaseAuditModelMixin):
    """
    Model to track employee attendance with manager approval system
    """

    class EmployeeStatus(models.TextChoices):
        PRESENT = "PRESENT", "Present"
        ABSENT = "ABSENT", "Absent"
        ON_LEAVE = "ON_LEAVE", "On Leave"
        WORK_FROM_HOME = "WORK_FROM_HOME", "Work From Home"

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="attendances"
    )
    check_in = models.DateTimeField(
        null=True, blank=True, help_text="Check-in time of the employee"
    )
    check_out = models.DateTimeField(
        null=True, blank=True, help_text="Check-out time of the employee"
    )
    date = models.DateField(help_text="Date of the attendance record")
    status = models.CharField(
        max_length=20,
        choices=EmployeeStatus.choices,
        default=EmployeeStatus.PRESENT,
        help_text="Attendance status of the employee",
    )
    is_approved = models.BooleanField(
        default=False, help_text="Whether the attendance has been approved by manager"
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_attendances",
        help_text="Manager who approved this attendance",
    )
    approved_at = models.DateTimeField(
        null=True, blank=True, help_text="When the attendance was approved"
    )

    class Meta:
        db_table = "attendance"
        verbose_name = "Attendance"
        verbose_name_plural = "Attendances"
        unique_together = [["employee", "date"]]

    def __str__(self):
        return f"Attendance record for {self.employee} on {self.date}"

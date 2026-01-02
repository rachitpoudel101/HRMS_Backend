from django.db import models
from apps.common.models import BaseTimeStampModelMixin, SoftDeleteModelMixin, BaseAuditModelMixin
from apps.users.models import Employee
class Attendance(BaseTimeStampModelMixin, SoftDeleteModelMixin, BaseAuditModelMixin):
    """
    Model to track employee attendance
    """
    class EmployeeStatus(models.TextChoices):
        PRESENT = 'PRESENT', 'Present'
        ABSENT = 'ABSENT', 'Absent'
        ON_LEAVE = 'ON_LEAVE', 'On Leave'
        WORK_FROM_HOME = 'WORK_FROM_HOME', 'Work From Home'

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    check_in = models.DateTimeField(null=True, blank=True, help_text="Check-in time of the employee")
    check_out = models.DateTimeField(null=True, blank=True, help_text="Check-out time of the employee")
    check_in_scan = models.ForeignKey(
        'FingerprintScan',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendance_checkin',
        help_text="Fingerprint scan record for check-in"
    )
    check_out_scan = models.ForeignKey(
        'FingerprintScan',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendance_checkout',
        help_text="Fingerprint scan record for check-out"
    )
    date = models.DateField(help_text="Date of the attendance record")
    status = models.CharField(
        max_length=20,
        choices=EmployeeStatus.choices,
        default=EmployeeStatus.PRESENT,
        help_text="Attendance status of the employee"
    )

    class Meta:
        db_table = 'attendance'
        verbose_name = "Attendance"
        verbose_name_plural = "Attendances"

    def __str__(self):
        return f"Attendance record for {self.employee} on {self.date}"
    
class FingerprintScan(models.Model):
    """Model to store fingerprint scan records"""
    
    class scanStatus(models.TextChoices):
        SUCCESS = 'SUCCESS', 'Success'
        FAIL = 'FAIL', 'Fail'
        DUPLICATE = 'DUPLICATE', 'Duplicate'
    
    class scanType(models.TextChoices):
        IN = 'IN', 'Check In'
        OUT = 'OUT', 'Check Out'

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='fingerprint_scans')
    scan_time = models.DateTimeField(auto_now_add=True)
    scan_type = models.CharField(max_length=10, choices=scanType.choices)
    device_id = models.CharField(max_length=50, blank=True, null=True)
    scan_status = models.CharField(max_length=20, choices=scanStatus.choices, null=True, blank=True, default=scanStatus.SUCCESS)
    attendance = models.ForeignKey('Attendance', on_delete=models.SET_NULL, null=True, blank=True, related_name='fingerprint_scans')

    class Meta:
        db_table = 'fingerprint_scan'
        verbose_name = "Fingerprint Scan"
        verbose_name_plural = "Fingerprint Scans"

    def __str__(self):
        return f"{self.employee} - {self.scan_type} at {self.scan_time}"
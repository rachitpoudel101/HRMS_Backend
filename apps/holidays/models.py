from django.db import models
from apps.common.models import (
    SoftDeleteModelMixin,
    BaseTimeStampModelMixin,
    BaseAuditModelMixin,
)
from apps.users.models import Employee, Branch


class Holiday(SoftDeleteModelMixin, BaseTimeStampModelMixin, BaseAuditModelMixin):
    """
    Model to represent holidays for employees
    """

    name = models.CharField(max_length=200, help_text="Name of the holiday")
    date = models.DateField(help_text="Date of the holiday")
    description = models.TextField(blank=True, help_text="Description of the holiday")
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="holidays",
        help_text="Branch associated with this holiday",
    )
    employees = models.ManyToManyField(
        Employee,
        related_name="holidays",
        blank=True,
        help_text="Employees associated with this holiday",
    )

    class Meta:
        db_table = "holiday"
        verbose_name = "Holiday"
        verbose_name_plural = "Holidays"
        unique_together = ["name", "date"]

    def __str__(self):
        return f"{self.name} on {self.date}"


class HolidayType(SoftDeleteModelMixin, BaseTimeStampModelMixin, BaseAuditModelMixin):
    """
    Model to represent types of holidays
    """

    type_name = models.CharField(
        max_length=100, unique=True, help_text="Name of the holiday type"
    )
    description = models.TextField(
        blank=True, help_text="Description of the holiday type"
    )

    class Meta:
        db_table = "holiday_type"
        verbose_name = "Holiday Type"
        verbose_name_plural = "Holiday Types"

    def __str__(self):
        return self.type_name

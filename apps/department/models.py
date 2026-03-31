from django.db import models
from apps.common.models import (
    SoftDeleteModelMixin,
    BaseTimeStampModelMixin,
    BaseAuditModelMixin,
)


class Department(SoftDeleteModelMixin, BaseTimeStampModelMixin, BaseAuditModelMixin):
    """Department/Division"""

    company = models.ForeignKey(
        "users.Company", on_delete=models.CASCADE, related_name="departments"
    )
    name = models.CharField(max_length=200)
    branch = models.ForeignKey(
        "users.Branch",
        on_delete=models.CASCADE,
        related_name="departments",
        null=True,
        blank=True,
    )
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    parent_department = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "department"
        unique_together = ["company", "code"]

    def __str__(self):
        return self.name


class Designation(SoftDeleteModelMixin, BaseTimeStampModelMixin, BaseAuditModelMixin):
    """Job positions/titles"""

    company = models.ForeignKey(
        "users.Company", on_delete=models.CASCADE, related_name="designations"
    )
    title = models.CharField(max_length=200)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="designations",
        null=True,
        blank=True,
    )
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    level = models.IntegerField(default=1, help_text="Hierarchy level")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "designation"
        unique_together = ["company", "code"]

    def __str__(self):
        return self.title

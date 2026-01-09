from django.db import models
from apps.common.models import SoftDeleteModelMixin, BaseTimeStampModelMixin, BaseAuditModelMixin
from apps.users.models import Employee, Branch
class Notic(SoftDeleteModelMixin, BaseTimeStampModelMixin, BaseAuditModelMixin):
    """
    Model to represent holidays for employees
    """
    name = models.CharField(max_length=200, help_text="Name of the holiday")
    date = models.DateField(help_text="Date of the holiday")
    description = models.TextField(blank=True, help_text="Description of the holiday")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True, related_name='notices', help_text="Branch associated with this notice")
    employees = models.ManyToManyField(Employee, related_name='notices', blank=True, help_text="Employees associated with this notice")

    class Meta:
        db_table = 'notice'
        verbose_name = "Notice"
        verbose_name_plural = "Notices"
        unique_together = ['name', 'date']

    def __str__(self):
        return f"{self.name} on {self.date}"
class NoticeType(SoftDeleteModelMixin, BaseTimeStampModelMixin, BaseAuditModelMixin):
    """
    Model to represent types of notices
    """
    type_name = models.CharField(max_length=100, unique=True, help_text="Name of the notice type")
    description = models.TextField(blank=True, help_text="Description of the notice type")

    class Meta:
        db_table = 'notice_type'
        verbose_name = "Notice Type"
        verbose_name_plural = "Notice Types"

    def __str__(self):
        return self.type_name

class NoticeAttachment(SoftDeleteModelMixin, BaseTimeStampModelMixin, BaseAuditModelMixin):
    """
    Model to represent attachments for notices
    """
    notice = models.ForeignKey(Notic, on_delete=models.CASCADE, related_name='attachments', help_text="Notice associated with this attachment")
    file = models.FileField(upload_to='notice_attachments/', help_text="File attachment for the notice")
    description = models.TextField(blank=True, help_text="Description of the attachment")

    class Meta:
        db_table = 'notice_attachment'
        verbose_name = "Notice Attachment"
        verbose_name_plural = "Notice Attachments"

    def __str__(self):
        return f"Attachment for {self.notice.name}"
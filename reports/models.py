import os
from datetime import date

from django.conf import settings
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models

ALLOWED_EXTENSIONS = ["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx"]
MONTHS = [(i, date(2000, i, 1).strftime("%B")) for i in range(1, 13)]


def report_upload_path(instance, filename):
    return f"reports/{instance.year}/{instance.month:02d}/dept{instance.department_id}/{filename}"


class MonthlyReportQuerySet(models.QuerySet):
    def visible_to(self, user):
        """Top executives see all; department heads see their own department's reports."""
        if user.is_superuser or user.is_top_executive:
            return self.all()
        return self.filter(department__head=user)


class MonthlyReport(models.Model):
    """A department head's monthly report, written offline and attached as a file."""

    department = models.ForeignKey(
        "departments.Department", on_delete=models.PROTECT, related_name="monthly_reports"
    )
    year = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(2017), MaxValueValidator(2100)]
    )
    month = models.PositiveSmallIntegerField(choices=MONTHS)
    file = models.FileField(
        upload_to=report_upload_path,
        validators=[FileExtensionValidator(ALLOWED_EXTENSIONS)],
        help_text="PDF, Word, Excel or PowerPoint, up to 10 MB.",
    )
    summary = models.CharField(
        max_length=300, blank=True, help_text="Optional one-line summary."
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reports_uploaded",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reports_reviewed",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    objects = MonthlyReportQuerySet.as_manager()

    class Meta:
        ordering = ["-year", "-month", "department__name", "-uploaded_at"]

    def __str__(self):
        return f"{self.department} report, {self.period_label}"

    @property
    def period_label(self):
        return date(self.year, self.month, 1).strftime("%B %Y")

    @property
    def filename(self):
        return os.path.basename(self.file.name)

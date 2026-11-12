from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Programme(models.Model):
    class Kind(models.TextChoices):
        EVENT = "event", "Event"
        WORKSHOP = "workshop", "Workshop / Training"
        COMPETITION = "competition", "Competition (e.g. PetroBowl)"
        OUTREACH = "outreach", "Outreach / School visit"
        MEETING = "meeting", "Meeting"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        ONGOING = "ongoing", "Ongoing"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    title = models.CharField(max_length=200)
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.EVENT)
    description = models.TextField(blank=True)
    expected_outcome = models.TextField(
        blank=True, help_text="Measurable outcome this programme must produce."
    )
    department = models.ForeignKey(
        "departments.Department", on_delete=models.PROTECT, related_name="programmes"
    )
    coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="coordinated_programmes",
    )
    date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    venue = models.CharField(max_length=200, blank=True)
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.PLANNED
    )
    expected_attendance = models.PositiveIntegerField(null=True, blank=True)
    actual_attendance = models.PositiveIntegerField(null=True, blank=True)
    outcome_summary = models.TextField(
        blank=True, help_text="What actually happened and what was achieved."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("programme_detail", args=[self.pk])

    @property
    def is_closed(self):
        return self.status in (self.Status.COMPLETED, self.Status.CANCELLED)

    @property
    def is_upcoming(self):
        return not self.is_closed and self.date >= timezone.localdate()

    @property
    def status_badge(self):
        return {
            self.Status.PLANNED: "secondary",
            self.Status.ONGOING: "primary",
            self.Status.COMPLETED: "success",
            self.Status.CANCELLED: "dark",
        }.get(self.status, "secondary")

    def can_be_edited_by(self, user):
        if not user.is_authenticated:
            return False
        return bool(
            user.is_superuser
            or self.coordinator_id == user.pk
            or (self.department_id and self.department.head_id == user.pk)
        )


class ProgrammeSpeaker(models.Model):
    programme = models.ForeignKey(
        Programme, on_delete=models.CASCADE, related_name="speakers"
    )
    contact = models.ForeignKey(
        "contacts.Contact", on_delete=models.PROTECT, related_name="speaking_engagements"
    )
    topic = models.CharField(max_length=200, blank=True)
    confirmed = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.contact} at {self.programme}"


class ProgrammeVolunteer(models.Model):
    programme = models.ForeignKey(
        Programme, on_delete=models.CASCADE, related_name="volunteers"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="volunteering"
    )
    role = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["programme", "user"], name="unique_programme_volunteer"
            )
        ]

    def __str__(self):
        return f"{self.user} at {self.programme}"


class FollowUp(models.Model):
    programme = models.ForeignKey(
        Programme, on_delete=models.CASCADE, related_name="follow_ups"
    )
    action = models.CharField(max_length=255)
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="followups",
    )
    due_date = models.DateField(null=True, blank=True)
    done = models.BooleanField(default=False)

    class Meta:
        ordering = ["done", "due_date", "id"]

    def __str__(self):
        return self.action

    @property
    def is_overdue(self):
        return bool(self.due_date and not self.done and self.due_date < timezone.localdate())

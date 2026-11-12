from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Project(models.Model):
    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        IN_PROGRESS = "in_progress", "In progress"
        ON_HOLD = "on_hold", "On hold"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    expected_outcome = models.TextField(
        blank=True,
        help_text="Measurable outcome this project must produce for SPE Kyambogo.",
    )
    department = models.ForeignKey(
        "departments.Department", on_delete=models.PROTECT, related_name="projects"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="owned_projects",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PLANNED
    )
    priority = models.CharField(
        max_length=10, choices=Priority.choices, default=Priority.MEDIUM
    )
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    challenges = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_date", "title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("project_detail", args=[self.pk])

    @property
    def is_closed(self):
        return self.status in (self.Status.COMPLETED, self.Status.CANCELLED)

    @property
    def is_overdue(self):
        return bool(
            self.due_date and not self.is_closed and self.due_date < timezone.localdate()
        )

    @property
    def status_badge(self):
        return {
            self.Status.PLANNED: "secondary",
            self.Status.IN_PROGRESS: "primary",
            self.Status.ON_HOLD: "warning",
            self.Status.COMPLETED: "success",
            self.Status.CANCELLED: "dark",
        }.get(self.status, "secondary")

    def can_be_edited_by(self, user):
        if not user.is_authenticated:
            return False
        return bool(
            user.is_superuser
            or self.owner_id == user.pk
            or (self.department_id and self.department.head_id == user.pk)
        )


class Milestone(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="milestones"
    )
    title = models.CharField(max_length=200)
    due_date = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)

    class Meta:
        ordering = ["due_date", "id"]

    def __str__(self):
        return self.title


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = "todo", "To do"
        DOING = "doing", "In progress"
        DONE = "done", "Done"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=200)
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
    )
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.TODO
    )

    class Meta:
        ordering = ["due_date", "id"]

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        return bool(
            self.due_date
            and self.status != self.Status.DONE
            and self.due_date < timezone.localdate()
        )

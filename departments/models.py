from django.conf import settings
from django.db import models


class Department(models.Model):
    """An executive department. Reports flow: Department Head -> CAO -> President/VP."""

    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    head = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="headed_departments",
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="departments"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

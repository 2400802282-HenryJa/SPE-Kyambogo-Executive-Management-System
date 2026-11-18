from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import reverse


class DepartmentQuerySet(models.QuerySet):
    def visible_to(self, user):
        if user.is_superuser or user.is_top_executive:
            return self.all()
        mine = self.model.objects.filter(Q(members=user) | Q(head=user)).values("pk")
        return self.filter(pk__in=mine)


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

    objects = DepartmentQuerySet.as_manager()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("department_detail", args=[self.pk])

    def can_manage_members(self, user):
        return bool(
            user.is_superuser or user.is_top_executive or self.head_id == user.pk
        )

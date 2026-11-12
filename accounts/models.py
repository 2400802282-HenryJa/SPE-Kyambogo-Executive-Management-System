from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Executive / officer account for SK-EMIS."""

    class Position(models.TextChoices):
        PRESIDENT = "president", "President"
        VICE_PRESIDENT = "vice_president", "Vice President"
        CAO = "cao", "Chief Administrative Officer (CAO)"
        DEPARTMENT_HEAD = "department_head", "Department Head"
        OFFICER = "officer", "Authorised Officer"

    position = models.CharField(
        max_length=20, choices=Position.choices, default=Position.OFFICER
    )
    phone = models.CharField(max_length=30, blank=True)

    @property
    def is_top_executive(self):
        return self.position in (
            self.Position.PRESIDENT,
            self.Position.VICE_PRESIDENT,
            self.Position.CAO,
        )

    def __str__(self):
        return self.get_full_name() or self.username

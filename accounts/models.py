from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Executive / officer account for SK-EMIS."""

    class Position(models.TextChoices):
        PRESIDENT = "president", "President"
        VICE_PRESIDENT = "vice_president", "Vice President"
        CAO = "cao", "Chief Administrative Officer (CAO)"
        TREASURER = "treasurer", "Treasurer"
        DEPARTMENT_HEAD = "department_head", "Department Head"
        OFFICER = "officer", "Authorised Officer"

    position = models.CharField(
        max_length=20, choices=Position.choices, default=Position.OFFICER
    )
    phone = models.CharField(max_length=30, blank=True)

    @property
    def is_top_executive(self):
        """President, Vice President and CAO: unrestricted access to chapter data."""
        return self.position in (
            self.Position.PRESIDENT,
            self.Position.VICE_PRESIDENT,
            self.Position.CAO,
        )

    @property
    def is_treasury_authorised(self):
        """May see confidential treasury/finance records."""
        return bool(
            self.is_superuser
            or self.is_top_executive
            or self.position == self.Position.TREASURER
        )

    @property
    def can_access_contacts(self):
        """Contacts hold personal details: top executives (and developer) only."""
        return bool(self.is_superuser or self.is_top_executive)

    @property
    def can_view_mobilisation(self):
        """Resource-mobilisation money records: treasury-authorised users and department heads."""
        return bool(self.is_treasury_authorised or self.headed_departments.exists())

    def save(self, *args, **kwargs):
        # Admin-site access is reserved for the developer (superuser) and the
        # three top executives. Nobody else can be made staff.
        if not self.is_superuser:
            self.is_staff = self.is_top_executive
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_full_name() or self.username

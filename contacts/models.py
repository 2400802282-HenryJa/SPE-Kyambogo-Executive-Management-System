from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Organisation(models.Model):
    class Kind(models.TextChoices):
        COMPANY = "company", "Company / Industry"
        UNIVERSITY = "university", "University"
        SCHOOL = "school", "School"
        PROFESSIONAL_BODY = "professional_body", "Professional body"
        GOVERNMENT_NGO = "government_ngo", "Government / NGO"
        OTHER = "other", "Other"

    name = models.CharField(max_length=200, unique=True)
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.OTHER)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Contact(models.Model):
    class Category(models.TextChoices):
        INDUSTRY_EXPERT = "industry_expert", "Industry expert"
        PARTNER = "partner", "Partner"
        SCHOOL_CONTACT = "school_contact", "School contact"
        ACADEMIC = "academic", "Academic"
        ALUMNI = "alumni", "Alumni"
        OTHER = "other", "Other"

    full_name = models.CharField(max_length=200)
    organisation = models.ForeignKey(
        Organisation,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="contacts",
    )
    job_title = models.CharField(max_length=200, blank=True)
    category = models.CharField(
        max_length=20, choices=Category.choices, default=Category.OTHER
    )
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    expertise = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="contacts_added",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name

    def get_absolute_url(self):
        return reverse("contact_detail", args=[self.pk])

    def can_be_edited_by(self, user):
        if not user.is_authenticated:
            return False
        return bool(
            user.is_superuser
            or self.added_by_id == user.pk
            or user.is_top_executive
            or user.position == user.Position.DEPARTMENT_HEAD
        )


class Interaction(models.Model):
    """A logged engagement with a contact (meeting, call, email, visit)."""

    contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, related_name="interactions"
    )
    date = models.DateField(default=timezone.localdate)
    summary = models.TextField()
    follow_up = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="interactions_recorded",
    )

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.contact} on {self.date}"

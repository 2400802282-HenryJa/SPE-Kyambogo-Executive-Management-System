from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from departments.models import Department
from projects.models import Project

User = get_user_model()


class ProjectTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner", password="pass12345")
        self.other = User.objects.create_user("other", password="pass12345")
        self.dept = Department.objects.create(name="Projects, Innovation and Resources")
        self.project = Project.objects.create(
            title="Test project",
            department=self.dept,
            owner=self.owner,
            status=Project.Status.IN_PROGRESS,
            due_date=timezone.localdate() - timedelta(days=1),
        )

    def test_overdue_logic(self):
        self.assertTrue(self.project.is_overdue)
        self.project.status = Project.Status.COMPLETED
        self.assertFalse(self.project.is_overdue)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_owner_can_edit(self):
        self.client.login(username="owner", password="pass12345")
        response = self.client.get(reverse("project_update", args=[self.project.pk]))
        self.assertEqual(response.status_code, 200)

    def test_other_user_cannot_edit(self):
        self.client.login(username="other", password="pass12345")
        response = self.client.get(reverse("project_update", args=[self.project.pk]))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_user_sees_dashboard(self):
        self.client.login(username="other", password="pass12345")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)

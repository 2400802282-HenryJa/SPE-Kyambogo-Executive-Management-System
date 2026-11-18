from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from departments.models import Department
from projects.models import Milestone, Project, Task

User = get_user_model()


class TaskMilestoneTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner", password="pass12345")
        self.assignee = User.objects.create_user("assignee", password="pass12345")
        self.other = User.objects.create_user("other", password="pass12345")
        dept = Department.objects.create(name="Test dept")
        self.project = Project.objects.create(title="P", department=dept, owner=self.owner)
        self.task = Task.objects.create(project=self.project, title="T", assignee=self.assignee)
        self.milestone = Milestone.objects.create(project=self.project, title="M")

    def test_owner_can_add_task(self):
        self.client.login(username="owner", password="pass12345")
        r = self.client.post(
            reverse("task_create", args=[self.project.pk]),
            {"title": "New task", "status": "todo"},
        )
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Task.objects.filter(title="New task", project=self.project).exists())

    def test_other_user_cannot_add_task(self):
        self.client.login(username="other", password="pass12345")
        r = self.client.get(reverse("task_create", args=[self.project.pk]))
        self.assertEqual(r.status_code, 404)  # project not visible to outsiders

    def test_assignee_can_update_own_task_status(self):
        self.client.login(username="assignee", password="pass12345")
        self.client.post(reverse("task_set_status", args=[self.task.pk]), {"status": "done"})
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, "done")

    def test_other_user_cannot_update_task_status(self):
        self.client.login(username="other", password="pass12345")
        r = self.client.post(reverse("task_set_status", args=[self.task.pk]), {"status": "done"})
        self.assertEqual(r.status_code, 403)

    def test_owner_can_toggle_milestone(self):
        self.client.login(username="owner", password="pass12345")
        self.client.post(reverse("milestone_toggle", args=[self.milestone.pk]))
        self.milestone.refresh_from_db()
        self.assertTrue(self.milestone.completed)

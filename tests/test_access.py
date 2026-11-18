from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from departments.models import Department
from projects.models import Project

User = get_user_model()
PW = "pass12345"


class RoleRuleTests(TestCase):
    def test_top_executives_become_staff_and_join_group(self):
        for pos in ("president", "vice_president", "cao"):
            u = User.objects.create_user(f"u_{pos}", password=PW, position=pos)
            u.refresh_from_db()
            self.assertTrue(u.is_staff, pos)
            self.assertTrue(u.groups.filter(name="Top Executives").exists(), pos)

    def test_others_cannot_be_staff(self):
        u = User.objects.create_user("off", password=PW, is_staff=True)
        u.refresh_from_db()
        self.assertFalse(u.is_staff)
        t = User.objects.create_user("tre", password=PW, position="treasurer")
        self.assertFalse(t.is_staff)

    def test_demotion_removes_admin_access(self):
        u = User.objects.create_user("pres", password=PW, position="president")
        u.position = "officer"
        u.save()
        u.refresh_from_db()
        self.assertFalse(u.is_staff)
        self.assertFalse(u.groups.filter(name="Top Executives").exists())

    def test_superuser_keeps_staff(self):
        u = User.objects.create_superuser("dev", password=PW)
        self.assertTrue(u.is_staff)

    def test_treasury_authorisation(self):
        mk = lambda n, p: User.objects.create_user(n, password=PW, position=p)
        self.assertTrue(mk("t1", "treasurer").is_treasury_authorised)
        self.assertTrue(mk("t2", "president").is_treasury_authorised)
        self.assertTrue(mk("t3", "cao").is_treasury_authorised)
        self.assertFalse(mk("t4", "officer").is_treasury_authorised)
        self.assertFalse(mk("t5", "department_head").is_treasury_authorised)


class ScopedAccessTests(TestCase):
    def setUp(self):
        self.head = User.objects.create_user("head", password=PW, position="department_head")
        self.member = User.objects.create_user("member", password=PW)
        self.outsider = User.objects.create_user("outsider", password=PW)
        self.president = User.objects.create_user("pres", password=PW, position="president")
        self.dept = Department.objects.create(name="Finance and Treasury", head=self.head)
        self.dept.members.add(self.member)
        self.other_dept = Department.objects.create(name="Other")
        self.secret = Project.objects.create(title="Secret budget", department=self.dept)
        self.public = Project.objects.create(title="Other project", department=self.other_dept)

    def login(self, name):
        self.client.login(username=name, password=PW)

    def test_member_sees_own_department_projects_only(self):
        self.login("member")
        r = self.client.get(reverse("project_list"))
        self.assertContains(r, "Secret budget")
        self.assertNotContains(r, "Other project")

    def test_outsider_cannot_open_project(self):
        self.login("outsider")
        self.assertEqual(self.client.get(self.secret.get_absolute_url()).status_code, 404)
        r = self.client.get(reverse("project_list"))
        self.assertNotContains(r, "Secret budget")

    def test_president_sees_everything_and_can_edit(self):
        self.login("pres")
        r = self.client.get(reverse("project_list"))
        self.assertContains(r, "Secret budget")
        self.assertContains(r, "Other project")
        self.assertEqual(self.client.get(reverse("project_update", args=[self.secret.pk])).status_code, 200)

    def test_member_cannot_edit_but_can_view(self):
        self.login("member")
        self.assertEqual(self.client.get(self.secret.get_absolute_url()).status_code, 200)
        self.assertEqual(self.client.get(reverse("project_update", args=[self.secret.pk])).status_code, 403)

    def test_outsider_dashboard_hides_other_projects(self):
        self.login("outsider")
        r = self.client.get(reverse("dashboard"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context["active_count"], 0)

    def test_head_can_add_and_remove_member(self):
        self.login("head")
        self.client.post(reverse("department_add_member", args=[self.dept.pk]), {"person": self.outsider.pk})
        self.assertTrue(self.dept.members.filter(pk=self.outsider.pk).exists())
        self.client.post(reverse("department_remove_member", args=[self.dept.pk, self.outsider.pk]))
        self.assertFalse(self.dept.members.filter(pk=self.outsider.pk).exists())

    def test_plain_member_cannot_add_members(self):
        self.login("member")
        r = self.client.post(reverse("department_add_member", args=[self.dept.pk]), {"person": self.outsider.pk})
        self.assertEqual(r.status_code, 403)

    def test_departments_list_scoped(self):
        self.login("member")
        r = self.client.get(reverse("department_list"))
        self.assertContains(r, "Finance and Treasury")
        self.assertNotContains(r, ">Other<")

    def test_login_failure_shows_friendly_message(self):
        r = self.client.post(reverse("login"), {"username": "nobody", "password": "wrong"})
        self.assertContains(r, "couldn&#x27;t sign you in")

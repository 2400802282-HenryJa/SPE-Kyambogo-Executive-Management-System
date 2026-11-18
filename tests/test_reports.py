import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from departments.models import Department
from reports.models import MonthlyReport

User = get_user_model()
PW = "pass12345"


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ReportTests(TestCase):
    def setUp(self):
        self.head = User.objects.create_user("head", password=PW, position="department_head")
        self.head2 = User.objects.create_user("head2", password=PW, position="department_head")
        self.member = User.objects.create_user("member", password=PW)
        self.cao = User.objects.create_user("cao", password=PW, position="cao")
        self.dept = Department.objects.create(name="Programs", head=self.head)
        self.dept2 = Department.objects.create(name="Finance", head=self.head2)

    def login(self, name):
        self.client.login(username=name, password=PW)

    def upload(self, name="april.pdf", dept=None):
        return self.client.post(reverse("report_create"), {
            "department": (dept or self.dept).pk, "year": 2026, "month": 10,
            "file": SimpleUploadedFile(name, b"%PDF-1.4 test"), "summary": "ok",
        })

    def test_head_uploads_own_department_report(self):
        self.login("head")
        self.assertEqual(self.upload().status_code, 302)
        r = MonthlyReport.objects.get()
        self.assertEqual(r.uploaded_by, self.head)
        self.assertEqual(r.period_label, "October 2026")

    def test_head_cannot_upload_for_another_department(self):
        self.login("head")
        r = self.upload(dept=self.dept2)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(MonthlyReport.objects.count(), 0)

    def test_bad_extension_rejected(self):
        self.login("head")
        self.assertEqual(self.upload("virus.exe").status_code, 200)
        self.assertEqual(MonthlyReport.objects.count(), 0)

    def test_plain_member_has_no_access(self):
        self.login("member")
        self.assertEqual(self.client.get(reverse("report_list")).status_code, 403)
        self.assertEqual(self.client.get(reverse("report_create")).status_code, 403)

    def test_other_head_cannot_download(self):
        self.login("head")
        self.upload()
        pk = MonthlyReport.objects.get().pk
        self.login("head2")
        self.assertEqual(self.client.get(reverse("report_download", args=[pk])).status_code, 404)
        self.login("head")
        self.assertEqual(self.client.get(reverse("report_download", args=[pk])).status_code, 200)

    def test_cao_sees_all_and_can_review(self):
        self.login("head")
        self.upload()
        pk = MonthlyReport.objects.get().pk
        self.login("cao")
        self.assertContains(self.client.get(reverse("report_list")), "april.pdf")
        self.client.post(reverse("report_review", args=[pk]))
        r = MonthlyReport.objects.get()
        self.assertTrue(r.reviewed)
        self.assertEqual(r.reviewed_by, self.cao)

    def test_head_cannot_review(self):
        self.login("head")
        self.upload()
        pk = MonthlyReport.objects.get().pk
        self.assertEqual(self.client.post(reverse("report_review", args=[pk])).status_code, 403)

    def test_dashboard_shows_missing_reports_to_cao(self):
        self.login("cao")
        r = self.client.get(reverse("dashboard"))
        self.assertContains(r, "Reports not yet received")
        self.login("member")
        self.assertNotContains(self.client.get(reverse("dashboard")), "Reports not yet received")

from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from contacts.models import Contact, Interaction
from departments.models import Department
from programmes.models import FollowUp, Programme, ProgrammeVolunteer

User = get_user_model()


class ProgrammeTests(TestCase):
    def setUp(self):
        self.coord = User.objects.create_user("coord", password="pass12345")
        self.other = User.objects.create_user("other", password="pass12345")
        dept = Department.objects.create(name="Programs")
        self.programme = Programme.objects.create(
            title="PetroBowl prep", department=dept, coordinator=self.coord, date=date(2030, 1, 1)
        )
        self.followup = FollowUp.objects.create(
            programme=self.programme, action="Send thank-you", assignee=self.other
        )

    def test_list_requires_login(self):
        r = self.client.get(reverse("programme_list"))
        self.assertEqual(r.status_code, 302)

    def test_coordinator_can_edit_other_cannot(self):
        self.client.login(username="coord", password="pass12345")
        self.assertEqual(self.client.get(reverse("programme_update", args=[self.programme.pk])).status_code, 200)
        self.client.login(username="other", password="pass12345")
        self.assertEqual(self.client.get(reverse("programme_update", args=[self.programme.pk])).status_code, 403)

    def test_duplicate_volunteer_rejected(self):
        self.client.login(username="coord", password="pass12345")
        url = reverse("volunteer_create", args=[self.programme.pk])
        self.client.post(url, {"user": self.other.pk, "role": "Ushering"})
        r = self.client.post(url, {"user": self.other.pk, "role": "Again"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(ProgrammeVolunteer.objects.filter(programme=self.programme).count(), 1)

    def test_assignee_can_complete_followup(self):
        self.client.login(username="other", password="pass12345")
        self.client.post(reverse("followup_toggle", args=[self.followup.pk]))
        self.followup.refresh_from_db()
        self.assertTrue(self.followup.done)

    def test_dashboard_still_loads(self):
        self.client.login(username="coord", password="pass12345")
        self.assertEqual(self.client.get(reverse("dashboard")).status_code, 200)


class ContactTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("u1", password="pass12345")
        self.other = User.objects.create_user("u2", password="pass12345")

    def test_create_and_search_contact(self):
        self.client.login(username="u1", password="pass12345")
        r = self.client.post(reverse("contact_create"), {
            "full_name": "Dr Test Expert", "category": "industry_expert", "expertise": "Reservoir modelling",
        })
        self.assertEqual(r.status_code, 302)
        contact = Contact.objects.get(full_name="Dr Test Expert")
        self.assertEqual(contact.added_by, self.user)
        r = self.client.get(reverse("contact_list"), {"q": "reservoir"})
        self.assertContains(r, "Dr Test Expert")

    def test_only_allowed_users_edit_contact(self):
        contact = Contact.objects.create(full_name="X", added_by=self.user)
        self.client.login(username="u2", password="pass12345")
        self.assertEqual(self.client.get(reverse("contact_update", args=[contact.pk])).status_code, 403)

    def test_any_user_can_log_engagement(self):
        contact = Contact.objects.create(full_name="X", added_by=self.user)
        self.client.login(username="u2", password="pass12345")
        self.client.post(reverse("interaction_create", args=[contact.pk]), {
            "date": "2026-11-10", "summary": "Met at event",
        })
        self.assertEqual(Interaction.objects.filter(contact=contact, recorded_by=self.other).count(), 1)

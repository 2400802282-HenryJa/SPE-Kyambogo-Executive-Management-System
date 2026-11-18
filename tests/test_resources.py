from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from departments.models import Department
from resources.models import Item, Mobilisation, StockMovement

User = get_user_model()
PW = "pass12345"


class ResourceTests(TestCase):
    def setUp(self):
        self.head = User.objects.create_user("head", password=PW, position="department_head")
        self.member = User.objects.create_user("member", password=PW)
        self.outsider = User.objects.create_user("outsider", password=PW)
        self.treasurer = User.objects.create_user("tres", password=PW, position="treasurer")
        self.dept = Department.objects.create(name="Resources", head=self.head)
        self.dept.members.add(self.member)
        self.item = Item.objects.create(
            name="SPE T-shirt", department=self.dept, unit_price=30000, unit_cost=18000, reorder_level=5
        )

    def login(self, name):
        self.client.login(username=name, password=PW)

    def move(self, user, kind, qty, price=None):
        self.login(user)
        data = {"kind": kind, "quantity": qty, "date": "2026-11-10"}
        if price is not None:
            data["unit_price"] = price
        return self.client.post(reverse("movement_create", args=[self.item.pk]), data)

    def test_stock_calculation(self):
        self.move("member", "restock", 20, 18000)
        self.move("member", "sale", 6, 30000)
        self.assertEqual(self.item.quantity_on_hand, 14)

    def test_cannot_oversell(self):
        self.move("member", "restock", 3, 18000)
        r = self.move("member", "sale", 5, 30000)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.item.quantity_on_hand, 3)

    def test_outsider_cannot_record_movements(self):
        self.login("outsider")
        r = self.client.get(reverse("movement_create", args=[self.item.pk]))
        self.assertEqual(r.status_code, 403)

    def test_everyone_can_view_catalogue(self):
        self.login("outsider")
        self.assertContains(self.client.get(reverse("resource_list")), "SPE T-shirt")

    def test_finance_details_hidden_from_plain_members(self):
        self.move("member", "restock", 10, 18000)
        self.move("member", "sale", 2, 30000)
        self.login("member")
        self.assertNotContains(self.client.get(self.item.get_absolute_url()), "Total revenue")
        for name in ("head", "tres"):
            self.login(name)
            self.assertContains(self.client.get(self.item.get_absolute_url()), "Total revenue")

    def test_low_stock_shows_on_dashboard(self):
        self.move("member", "restock", 4, 18000)
        self.login("member")
        r = self.client.get(reverse("dashboard"))
        self.assertContains(r, "SPE T-shirt")

    def test_mobilisation_access(self):
        self.login("outsider")
        self.assertEqual(self.client.get(reverse("mobilisation_list")).status_code, 403)
        self.login("member")
        self.assertEqual(self.client.get(reverse("mobilisation_list")).status_code, 403)

    def test_head_records_own_department_mobilisation_only(self):
        other = Department.objects.create(name="Other dept")
        self.login("head")
        data = {"title": "Sponsor", "kind": "cash", "source": "Oil Co", "amount": 500000,
                "status": "received", "date": "2026-11-10", "department": self.dept.pk}
        self.assertEqual(self.client.post(reverse("mobilisation_create"), data).status_code, 302)
        data["department"] = other.pk
        self.assertEqual(self.client.post(reverse("mobilisation_create"), data).status_code, 200)
        self.assertEqual(Mobilisation.objects.count(), 1)

    def test_treasurer_sees_all_mobilisation(self):
        Mobilisation.objects.create(title="Gift", amount=100, department=self.dept, status="received")
        self.login("tres")
        self.assertContains(self.client.get(reverse("mobilisation_list")), "Gift")

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Case, F, IntegerField, Sum, When
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils import timezone

OUT_KINDS = ("sale", "issue", "loss")


def _stock_expression(prefix=""):
    return Sum(
        Case(
            When(**{f"{prefix}kind__in": OUT_KINDS}, then=-F(f"{prefix}quantity")),
            default=F(f"{prefix}quantity"),
            output_field=IntegerField(),
        )
    )


class ItemQuerySet(models.QuerySet):
    def with_stock(self):
        return self.annotate(on_hand=Coalesce(_stock_expression("movements__"), 0))


class Item(models.Model):
    """A catalogue entry: merchandise, an asset, or a consumable."""

    class Category(models.TextChoices):
        MERCHANDISE = "merchandise", "Merchandise"
        ASSET = "asset", "Asset / equipment"
        CONSUMABLE = "consumable", "Consumable"
        OTHER = "other", "Other"

    name = models.CharField(max_length=200)
    category = models.CharField(
        max_length=20, choices=Category.choices, default=Category.MERCHANDISE
    )
    description = models.TextField(blank=True)
    department = models.ForeignKey(
        "departments.Department", on_delete=models.PROTECT, related_name="resource_items"
    )
    unit_price = models.DecimalField(
        max_digits=12, decimal_places=0, default=0, help_text="Selling price per unit (UGX)."
    )
    unit_cost = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        help_text="Purchase cost per unit (UGX). Confidential.",
    )
    reorder_level = models.PositiveIntegerField(
        default=0, help_text="Warn when stock falls to this number (0 = no warning)."
    )
    storage_location = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ItemQuerySet.as_manager()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("resource_detail", args=[self.pk])

    @property
    def quantity_on_hand(self):
        total = self.movements.aggregate(total=_stock_expression())["total"]
        return total or 0

    @property
    def is_low_stock(self):
        return self.reorder_level > 0 and self.quantity_on_hand <= self.reorder_level

    def can_be_managed_by(self, user):
        """Record stock and sales: top executives, and the owning department's head/members."""
        if not user.is_authenticated:
            return False
        return bool(
            user.is_superuser
            or user.is_top_executive
            or self.department.head_id == user.pk
            or self.department.members.filter(pk=user.pk).exists()
        )

    def finance_visible_to(self, user):
        """Costs, revenue and profit: treasury-authorised users and the department head."""
        return bool(user.is_treasury_authorised or self.department.head_id == user.pk)


class StockMovement(models.Model):
    class Kind(models.TextChoices):
        RESTOCK = "restock", "Restock (purchased)"
        DONATION = "donation", "Donation received"
        RETURN = "return", "Returned to stock"
        SALE = "sale", "Sale"
        ISSUE = "issue", "Issued / used"
        LOSS = "loss", "Lost / damaged"

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="movements")
    kind = models.CharField(max_length=10, choices=Kind.choices)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True,
        help_text="Per unit: selling price for sales, purchase cost for restocks.",
    )
    date = models.DateField(default=timezone.localdate)
    note = models.CharField(max_length=255, blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="stock_movements",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.get_kind_display()} {self.quantity} x {self.item}"

    @property
    def is_outgoing(self):
        return self.kind in OUT_KINDS

    @property
    def signed_quantity(self):
        return -self.quantity if self.is_outgoing else self.quantity

    @property
    def total_value(self):
        return (self.unit_price or 0) * self.quantity


class MobilisationQuerySet(models.QuerySet):
    def visible_to(self, user):
        if user.is_treasury_authorised:
            return self.all()
        return self.filter(department__head=user)


class Mobilisation(models.Model):
    """Funds or in-kind support raised or pledged (confidential)."""

    class Kind(models.TextChoices):
        CASH = "cash", "Cash"
        IN_KIND = "in_kind", "In-kind"
        SPONSORSHIP = "sponsorship", "Sponsorship"

    class Status(models.TextChoices):
        PLEDGED = "pledged", "Pledged"
        RECEIVED = "received", "Received"

    title = models.CharField(max_length=200)
    kind = models.CharField(max_length=15, choices=Kind.choices, default=Kind.CASH)
    source = models.CharField(max_length=200, blank=True, help_text="Donor / sponsor.")
    amount = models.DecimalField(
        max_digits=14, decimal_places=0, default=0, help_text="Value in UGX."
    )
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PLEDGED
    )
    date = models.DateField(default=timezone.localdate)
    department = models.ForeignKey(
        "departments.Department", on_delete=models.PROTECT, related_name="mobilisations"
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="mobilisations_recorded",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = MobilisationQuerySet.as_manager()

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return self.title

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import ItemForm, MobilisationForm, MovementForm
from .models import Item, Mobilisation, StockMovement


class ResourceListView(LoginRequiredMixin, ListView):
    template_name = "resources/resource_list.html"
    context_object_name = "items"

    def get_queryset(self):
        qs = Item.objects.with_stock().select_related("department")
        q = self.request.GET.get("q", "").strip()
        category = self.request.GET.get("category", "")
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(storage_location__icontains=q))
        if category:
            qs = qs.filter(category=category)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Item.Category.choices
        ctx["q"] = self.request.GET.get("q", "")
        ctx["selected_category"] = self.request.GET.get("category", "")
        return ctx


class ResourceDetailView(LoginRequiredMixin, DetailView):
    model = Item
    template_name = "resources/resource_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        item, user = self.object, self.request.user
        movements = list(item.movements.select_related("recorded_by"))
        finance_ok = item.finance_visible_to(user)
        ctx.update(
            can_manage=item.can_be_managed_by(user),
            finance_ok=finance_ok,
            movements=movements,
            on_hand=item.quantity_on_hand,
        )
        if finance_ok:
            sales = [m for m in movements if m.kind == StockMovement.Kind.SALE]
            restocks = [m for m in movements if m.kind == StockMovement.Kind.RESTOCK]
            revenue = sum(m.total_value for m in sales)
            spent = sum(m.total_value for m in restocks)
            ctx.update(
                units_sold=sum(m.quantity for m in sales),
                revenue=revenue,
                restock_cost=spent,
                net=revenue - spent,
            )
        return ctx


class ResourceCreateView(LoginRequiredMixin, CreateView):
    model = Item
    form_class = ItemForm
    template_name = "form_page.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(heading="New resource item", back_url=reverse("resource_list"))
        return ctx


class ResourceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Item
    form_class = ItemForm
    template_name = "form_page.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def test_func(self):
        return self.get_object().can_be_managed_by(self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(heading="Edit resource item", back_url=self.object.get_absolute_url())
        return ctx


class MovementCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = StockMovement
    form_class = MovementForm
    template_name = "form_page.html"

    def get_item(self):
        if not hasattr(self, "_item"):
            self._item = get_object_or_404(Item, pk=self.kwargs["item_pk"])
        return self._item

    def test_func(self):
        return self.get_item().can_be_managed_by(self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["item"] = self.get_item()
        return kwargs

    def form_valid(self, form):
        form.instance.item = self.get_item()
        form.instance.recorded_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return self.get_item().get_absolute_url()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        item = self.get_item()
        ctx.update(
            heading="Record stock movement",
            subheading=f"{item.name}: {item.quantity_on_hand} currently in stock",
            back_url=item.get_absolute_url(),
        )
        return ctx


class MobilisationAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.can_view_mobilisation


class MobilisationListView(MobilisationAccessMixin, ListView):
    template_name = "resources/mobilisation_list.html"
    context_object_name = "records"

    def get_queryset(self):
        return Mobilisation.objects.visible_to(self.request.user).select_related("department")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        ctx["received_total"] = (
            qs.filter(status=Mobilisation.Status.RECEIVED).aggregate(t=Sum("amount"))["t"] or 0
        )
        ctx["pledged_total"] = (
            qs.filter(status=Mobilisation.Status.PLEDGED).aggregate(t=Sum("amount"))["t"] or 0
        )
        return ctx


class MobilisationCreateView(MobilisationAccessMixin, CreateView):
    model = Mobilisation
    form_class = MobilisationForm
    template_name = "form_page.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.recorded_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("mobilisation_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(heading="Record resource mobilisation", back_url=reverse("mobilisation_list"))
        return ctx


class MobilisationUpdateView(MobilisationAccessMixin, UpdateView):
    form_class = MobilisationForm
    template_name = "form_page.html"

    def get_queryset(self):
        return Mobilisation.objects.visible_to(self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse("mobilisation_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(heading="Edit mobilisation record", back_url=reverse("mobilisation_list"))
        return ctx

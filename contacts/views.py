from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import ContactForm, InteractionForm, OrganisationForm
from .models import Contact


class ContactListView(LoginRequiredMixin, ListView):
    model = Contact
    template_name = "contacts/contact_list.html"
    context_object_name = "contacts"

    def get_queryset(self):
        qs = Contact.objects.select_related("organisation")
        q = self.request.GET.get("q", "").strip()
        category = self.request.GET.get("category", "")
        if q:
            qs = qs.filter(
                Q(full_name__icontains=q)
                | Q(organisation__name__icontains=q)
                | Q(expertise__icontains=q)
                | Q(job_title__icontains=q)
            )
        if category:
            qs = qs.filter(category=category)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Contact.Category.choices
        ctx["q"] = self.request.GET.get("q", "")
        ctx["selected_category"] = self.request.GET.get("category", "")
        return ctx


class ContactDetailView(LoginRequiredMixin, DetailView):
    model = Contact
    template_name = "contacts/contact_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["can_edit"] = self.object.can_be_edited_by(self.request.user)
        return ctx


class ContactCreateView(LoginRequiredMixin, CreateView):
    model = Contact
    form_class = ContactForm
    template_name = "form_page.html"

    def form_valid(self, form):
        form.instance.added_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(heading="New contact", back_url=reverse("contact_list"))
        return ctx


class ContactUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Contact
    form_class = ContactForm
    template_name = "form_page.html"

    def test_func(self):
        return self.get_object().can_be_edited_by(self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(heading="Edit contact", back_url=self.object.get_absolute_url())
        return ctx


class OrganisationCreateView(LoginRequiredMixin, CreateView):
    form_class = OrganisationForm
    template_name = "form_page.html"

    def get_success_url(self):
        return reverse("contact_create")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            heading="New organisation",
            subheading="After saving you will go straight to the new-contact form.",
            back_url=reverse("contact_list"),
        )
        return ctx

    def get_queryset(self):
        from .models import Organisation
        return Organisation.objects.all()


class InteractionCreateView(LoginRequiredMixin, CreateView):
    form_class = InteractionForm
    template_name = "form_page.html"

    def get_contact(self):
        if not hasattr(self, "_contact"):
            self._contact = get_object_or_404(Contact, pk=self.kwargs["contact_pk"])
        return self._contact

    def form_valid(self, form):
        form.instance.contact = self.get_contact()
        form.instance.recorded_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return self.get_contact().get_absolute_url()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            heading="Log engagement",
            subheading=f"Contact: {self.get_contact()}",
            back_url=self.get_contact().get_absolute_url(),
        )
        return ctx

    def get_queryset(self):
        from .models import Interaction
        return Interaction.objects.all()

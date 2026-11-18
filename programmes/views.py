from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from departments.models import Department

from .forms import FollowUpForm, ProgrammeForm, SpeakerForm, VolunteerForm
from .models import FollowUp, Programme, ProgrammeSpeaker, ProgrammeVolunteer


class ProgrammeListView(LoginRequiredMixin, ListView):
    model = Programme
    template_name = "programmes/programme_list.html"
    context_object_name = "programmes"

    def get_queryset(self):
        qs = Programme.objects.select_related("department", "coordinator")
        status = self.request.GET.get("status")
        department = self.request.GET.get("department")
        if status:
            qs = qs.filter(status=status)
        if department:
            qs = qs.filter(department_id=department)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["statuses"] = Programme.Status.choices
        ctx["departments"] = Department.objects.all()
        ctx["selected_status"] = self.request.GET.get("status", "")
        ctx["selected_department"] = self.request.GET.get("department", "")
        return ctx


class ProgrammeDetailView(LoginRequiredMixin, DetailView):
    model = Programme
    template_name = "programmes/programme_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["can_edit"] = self.object.can_be_edited_by(self.request.user)
        return ctx


class ProgrammeCreateView(LoginRequiredMixin, CreateView):
    model = Programme
    form_class = ProgrammeForm
    template_name = "form_page.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(heading="New programme", back_url="/programmes/")
        return ctx


class ProgrammeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Programme
    form_class = ProgrammeForm
    template_name = "form_page.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def test_func(self):
        return self.get_object().can_be_edited_by(self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(heading="Edit programme", back_url=self.object.get_absolute_url())
        return ctx


class ProgrammeChildCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = "form_page.html"
    heading = ""

    def get_programme(self):
        if not hasattr(self, "_programme"):
            self._programme = get_object_or_404(Programme, pk=self.kwargs["programme_pk"])
        return self._programme

    def test_func(self):
        return self.get_programme().can_be_edited_by(self.request.user)

    def form_valid(self, form):
        form.instance.programme = self.get_programme()
        return super().form_valid(form)

    def get_success_url(self):
        return self.get_programme().get_absolute_url()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            heading=self.heading,
            subheading=f"Programme: {self.get_programme()}",
            back_url=self.get_programme().get_absolute_url(),
        )
        return ctx


class SpeakerCreateView(ProgrammeChildCreateView):
    model = ProgrammeSpeaker
    form_class = SpeakerForm
    heading = "Add invited speaker"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        contact = form.cleaned_data.get("contact")
        if contact and ProgrammeSpeaker.objects.filter(
            programme=self.get_programme(), contact=contact
        ).exists():
            form.add_error("contact", "This contact is already listed as a speaker.")
            return self.form_invalid(form)
        return super().form_valid(form)


class VolunteerCreateView(ProgrammeChildCreateView):
    model = ProgrammeVolunteer
    form_class = VolunteerForm
    heading = "Add volunteer"

    def form_valid(self, form):
        if ProgrammeVolunteer.objects.filter(
            programme=self.get_programme(), user=form.cleaned_data["user"]
        ).exists():
            form.add_error("user", "This person is already a volunteer.")
            return self.form_invalid(form)
        return super().form_valid(form)


class FollowUpCreateView(ProgrammeChildCreateView):
    model = FollowUp
    form_class = FollowUpForm
    heading = "Add follow-up action"


@login_required
@require_POST
def followup_toggle(request, pk):
    item = get_object_or_404(FollowUp, pk=pk)
    allowed = item.programme.can_be_edited_by(request.user) or item.assignee_id == request.user.pk
    if not allowed:
        raise PermissionDenied
    item.done = not item.done
    item.save(update_fields=["done"])
    return redirect(item.programme)

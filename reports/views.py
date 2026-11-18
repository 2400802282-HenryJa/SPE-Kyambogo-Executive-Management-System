from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, ListView

from departments.models import Department

from .forms import ReportForm
from .models import MonthlyReport


class ReportAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.can_view_reports


class ReportListView(ReportAccessMixin, ListView):
    template_name = "reports/report_list.html"
    context_object_name = "reports"

    def get_queryset(self):
        qs = MonthlyReport.objects.visible_to(self.request.user).select_related(
            "department", "uploaded_by", "reviewed_by"
        )
        department = self.request.GET.get("department")
        year = self.request.GET.get("year", "").strip()
        if department:
            qs = qs.filter(department_id=department)
        if year.isdigit():
            qs = qs.filter(year=int(year))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["is_reviewer"] = user.is_superuser or user.is_top_executive
        ctx["departments"] = (
            Department.objects.all()
            if ctx["is_reviewer"]
            else Department.objects.filter(head=user)
        )
        ctx["selected_department"] = self.request.GET.get("department", "")
        ctx["year"] = self.request.GET.get("year", "")
        return ctx


class ReportCreateView(ReportAccessMixin, CreateView):
    model = MonthlyReport
    form_class = ReportForm
    template_name = "form_page.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        messages.success(self.request, "Report uploaded.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("report_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            heading="Upload monthly report",
            subheading="Write the report offline (Word, Excel, PDF...) and attach it here.",
            back_url=reverse("report_list"),
        )
        return ctx


@login_required
def report_download(request, pk):
    report = get_object_or_404(MonthlyReport.objects.visible_to(request.user), pk=pk)
    return FileResponse(
        report.file.open("rb"), as_attachment=True, filename=report.filename
    )


@login_required
@require_POST
def report_review(request, pk):
    if not (request.user.is_superuser or request.user.is_top_executive):
        raise PermissionDenied
    report = get_object_or_404(MonthlyReport, pk=pk)
    report.reviewed = not report.reviewed
    report.reviewed_by = request.user if report.reviewed else None
    report.reviewed_at = timezone.now() if report.reviewed else None
    report.save(update_fields=["reviewed", "reviewed_by", "reviewed_at"])
    return redirect("report_list")

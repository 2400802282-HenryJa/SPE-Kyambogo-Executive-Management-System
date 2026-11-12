from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView

from departments.models import Department
from programmes.models import FollowUp, Programme

from .forms import MilestoneForm, ProjectForm, TaskForm
from .models import Milestone, Project, Task


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "projects/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = timezone.localdate()
        active = Project.objects.exclude(
            status__in=[Project.Status.COMPLETED, Project.Status.CANCELLED]
        )
        labels = dict(Project.Status.choices)
        counts = Project.objects.values("status").annotate(n=Count("id"))
        open_tasks = Task.objects.exclude(status=Task.Status.DONE)

        ctx["active_count"] = active.count()
        ctx["status_counts"] = [(labels[c["status"]], c["n"]) for c in counts]
        ctx["overdue_projects"] = active.filter(due_date__lt=today).select_related(
            "department", "owner"
        )
        ctx["overdue_tasks"] = open_tasks.filter(due_date__lt=today).select_related(
            "project", "assignee"
        )
        ctx["upcoming_programmes"] = (
            Programme.objects.exclude(
                status__in=[Programme.Status.COMPLETED, Programme.Status.CANCELLED]
            )
            .filter(date__gte=today)
            .order_by("date")[:5]
        )
        ctx["open_followups"] = (
            FollowUp.objects.filter(done=False)
            .select_related("programme", "assignee")
            .order_by("due_date")[:8]
        )
        ctx["my_tasks"] = open_tasks.filter(assignee=self.request.user).select_related(
            "project"
        )
        return ctx


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"

    def get_queryset(self):
        qs = Project.objects.select_related("department", "owner")
        status = self.request.GET.get("status")
        department = self.request.GET.get("department")
        if status:
            qs = qs.filter(status=status)
        if department:
            qs = qs.filter(department_id=department)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["statuses"] = Project.Status.choices
        ctx["departments"] = Department.objects.all()
        ctx["selected_status"] = self.request.GET.get("status", "")
        ctx["selected_department"] = self.request.GET.get("department", "")
        return ctx


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = "projects/project_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["can_edit"] = self.object.can_be_edited_by(self.request.user)
        ctx["task_statuses"] = Task.Status.choices
        return ctx


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/project_form.html"


class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/project_form.html"

    def test_func(self):
        return self.get_object().can_be_edited_by(self.request.user)


class ProjectChildCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Base view for adding a milestone or task to a project."""

    template_name = "projects/child_form.html"
    heading = ""

    def get_project(self):
        if not hasattr(self, "_project"):
            self._project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        return self._project

    def test_func(self):
        return self.get_project().can_be_edited_by(self.request.user)

    def form_valid(self, form):
        form.instance.project = self.get_project()
        return super().form_valid(form)

    def get_success_url(self):
        return self.get_project().get_absolute_url()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["project"] = self.get_project()
        ctx["heading"] = self.heading
        return ctx


class MilestoneCreateView(ProjectChildCreateView):
    model = Milestone
    form_class = MilestoneForm
    heading = "Add milestone"


class TaskCreateView(ProjectChildCreateView):
    model = Task
    form_class = TaskForm
    heading = "Add task"


@login_required
@require_POST
def milestone_toggle(request, pk):
    milestone = get_object_or_404(Milestone, pk=pk)
    if not milestone.project.can_be_edited_by(request.user):
        raise PermissionDenied
    milestone.completed = not milestone.completed
    milestone.save(update_fields=["completed"])
    return redirect(milestone.project)


@login_required
@require_POST
def task_set_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    allowed = task.project.can_be_edited_by(request.user) or task.assignee_id == request.user.pk
    if not allowed:
        raise PermissionDenied
    status = request.POST.get("status")
    if status in Task.Status.values:
        task.status = status
        task.save(update_fields=["status"])
    return redirect(task.project)

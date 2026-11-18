from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView

from projects.models import Project

from .forms import AddMemberForm
from .models import Department


class DepartmentListView(LoginRequiredMixin, ListView):
    template_name = "departments/department_list.html"
    context_object_name = "departments"

    def get_queryset(self):
        return Department.objects.visible_to(self.request.user).select_related("head")


class DepartmentDetailView(LoginRequiredMixin, DetailView):
    template_name = "departments/department_detail.html"

    def get_queryset(self):
        return Department.objects.visible_to(self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        dept = self.object
        can_manage = dept.can_manage_members(self.request.user)
        ctx["can_manage"] = can_manage
        ctx["members"] = dept.members.order_by("first_name", "username")
        ctx["projects"] = Project.objects.visible_to(self.request.user).filter(
            department=dept
        )
        ctx["programmes"] = dept.programmes.all()[:10]
        if can_manage:
            ctx["add_form"] = AddMemberForm(department=dept)
        return ctx


@login_required
@require_POST
def add_member(request, pk):
    dept = get_object_or_404(Department.objects.visible_to(request.user), pk=pk)
    if not dept.can_manage_members(request.user):
        raise PermissionDenied
    form = AddMemberForm(request.POST, department=dept)
    if form.is_valid():
        person = form.cleaned_data["person"]
        dept.members.add(person)
        messages.success(request, f"{person} added to {dept}.")
    else:
        messages.error(request, "Please choose a person to add.")
    return redirect(dept)


@login_required
@require_POST
def remove_member(request, pk, user_pk):
    dept = get_object_or_404(Department.objects.visible_to(request.user), pk=pk)
    if not dept.can_manage_members(request.user):
        raise PermissionDenied
    person = get_object_or_404(get_user_model(), pk=user_pk)
    dept.members.remove(person)
    messages.success(request, f"{person} removed from {dept}.")
    return redirect(dept)

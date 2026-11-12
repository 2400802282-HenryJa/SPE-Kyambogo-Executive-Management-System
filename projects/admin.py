from django.contrib import admin

from .models import Milestone, Project, Task


class MilestoneInline(admin.TabularInline):
    model = Milestone
    extra = 1


class TaskInline(admin.TabularInline):
    model = Task
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "department", "owner", "status", "priority", "due_date")
    list_filter = ("status", "priority", "department")
    search_fields = ("title", "description")
    inlines = [MilestoneInline, TaskInline]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "assignee", "status", "due_date")
    list_filter = ("status",)

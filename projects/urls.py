from django.urls import path

from . import views

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("projects/", views.ProjectListView.as_view(), name="project_list"),
    path("projects/new/", views.ProjectCreateView.as_view(), name="project_create"),
    path("projects/<int:pk>/", views.ProjectDetailView.as_view(), name="project_detail"),
    path("projects/<int:pk>/edit/", views.ProjectUpdateView.as_view(), name="project_update"),
    path("projects/<int:project_pk>/milestones/new/", views.MilestoneCreateView.as_view(), name="milestone_create"),
    path("projects/<int:project_pk>/tasks/new/", views.TaskCreateView.as_view(), name="task_create"),
    path("milestones/<int:pk>/toggle/", views.milestone_toggle, name="milestone_toggle"),
    path("tasks/<int:pk>/status/", views.task_set_status, name="task_set_status"),
]

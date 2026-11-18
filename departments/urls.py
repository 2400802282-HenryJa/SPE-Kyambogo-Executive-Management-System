from django.urls import path

from . import views

urlpatterns = [
    path("departments/", views.DepartmentListView.as_view(), name="department_list"),
    path("departments/<int:pk>/", views.DepartmentDetailView.as_view(), name="department_detail"),
    path("departments/<int:pk>/members/add/", views.add_member, name="department_add_member"),
    path("departments/<int:pk>/members/<int:user_pk>/remove/", views.remove_member, name="department_remove_member"),
]

from django.urls import path

from . import views

urlpatterns = [
    path("reports/", views.ReportListView.as_view(), name="report_list"),
    path("reports/upload/", views.ReportCreateView.as_view(), name="report_create"),
    path("reports/<int:pk>/download/", views.report_download, name="report_download"),
    path("reports/<int:pk>/review/", views.report_review, name="report_review"),
]

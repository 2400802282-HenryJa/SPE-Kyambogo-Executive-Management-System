from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "SPE Kyambogo EMIS Administration"
admin.site.site_title = "SK-EMIS Admin"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("projects.urls")),
]

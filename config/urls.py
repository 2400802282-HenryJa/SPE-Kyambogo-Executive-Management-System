from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import include, path

from config.forms import StyledAuthenticationForm

admin.site.site_header = "SPE Kyambogo EMIS Administration"
admin.site.site_title = "SK-EMIS Admin"

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "accounts/login/",
        LoginView.as_view(authentication_form=StyledAuthenticationForm),
        name="login",
    ),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("projects.urls")),
    path("", include("departments.urls")),
    path("", include("contacts.urls")),
    path("", include("programmes.urls")),
    path("", include("resources.urls")),
    path("", include("reports.urls")),
]

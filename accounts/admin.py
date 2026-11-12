from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("SPE Kyambogo", {"fields": ("position", "phone")}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("SPE Kyambogo", {"fields": ("position", "phone")}),
    )
    list_display = ("username", "get_full_name", "position", "email", "is_active")
    list_filter = DjangoUserAdmin.list_filter + ("position",)

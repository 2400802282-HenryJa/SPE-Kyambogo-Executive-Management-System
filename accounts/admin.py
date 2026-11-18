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
    list_filter = ("position", "is_active")

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser:
            # Only the developer can change privilege flags.
            readonly += ["is_superuser", "is_staff", "user_permissions", "groups"]
        return readonly

    def has_change_permission(self, request, obj=None):
        if obj is not None and obj.is_superuser and not request.user.is_superuser:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.is_superuser and not request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)

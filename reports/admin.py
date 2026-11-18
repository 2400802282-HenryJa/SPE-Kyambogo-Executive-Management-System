from django.contrib import admin

from .models import MonthlyReport


@admin.register(MonthlyReport)
class MonthlyReportAdmin(admin.ModelAdmin):
    list_display = ("department", "year", "month", "uploaded_by", "uploaded_at", "reviewed")
    list_filter = ("year", "month", "department", "reviewed")

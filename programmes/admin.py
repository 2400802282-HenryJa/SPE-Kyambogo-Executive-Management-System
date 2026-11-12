from django.contrib import admin

from .models import FollowUp, Programme, ProgrammeSpeaker, ProgrammeVolunteer


class SpeakerInline(admin.TabularInline):
    model = ProgrammeSpeaker
    extra = 0


class VolunteerInline(admin.TabularInline):
    model = ProgrammeVolunteer
    extra = 0


class FollowUpInline(admin.TabularInline):
    model = FollowUp
    extra = 0


@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "department", "coordinator", "date", "status")
    list_filter = ("status", "kind", "department")
    search_fields = ("title", "venue")
    inlines = [SpeakerInline, VolunteerInline, FollowUpInline]

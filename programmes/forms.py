from django import forms
from django.contrib.auth import get_user_model

from config.forms import limit_department_choices, style_form

from .models import FollowUp, Programme, ProgrammeSpeaker, ProgrammeVolunteer

DATE = {"type": "date"}


class ProgrammeForm(forms.ModelForm):
    class Meta:
        model = Programme
        fields = [
            "title", "kind", "description", "expected_outcome", "department",
            "coordinator", "date", "end_date", "venue", "status",
            "expected_attendance", "actual_attendance", "outcome_summary",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "expected_outcome": forms.Textarea(attrs={"rows": 2}),
            "outcome_summary": forms.Textarea(attrs={"rows": 3}),
            "date": forms.DateInput(attrs=DATE, format="%Y-%m-%d"),
            "end_date": forms.DateInput(attrs=DATE, format="%Y-%m-%d"),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["coordinator"].queryset = get_user_model().objects.filter(is_active=True)
        limit_department_choices(self, user)
        style_form(self)

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get("date"), cleaned.get("end_date")
        if start and end and end < start:
            self.add_error("end_date", "End date cannot be before the start date.")
        return cleaned


class SpeakerForm(forms.ModelForm):
    class Meta:
        model = ProgrammeSpeaker
        fields = ["contact", "name", "organisation", "topic", "confirmed"]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Only users allowed to see Contacts may pick from the contacts directory.
        if user is None or not user.can_access_contacts:
            del self.fields["contact"]
        style_form(self)

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("contact") and not (cleaned.get("name") or "").strip():
            raise forms.ValidationError("Enter the speaker's name (or pick a contact).")
        return cleaned


class VolunteerForm(forms.ModelForm):
    class Meta:
        model = ProgrammeVolunteer
        fields = ["user", "role"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = get_user_model().objects.filter(is_active=True)
        style_form(self)


class FollowUpForm(forms.ModelForm):
    class Meta:
        model = FollowUp
        fields = ["action", "assignee", "due_date"]
        widgets = {"due_date": forms.DateInput(attrs=DATE, format="%Y-%m-%d")}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assignee"].queryset = get_user_model().objects.filter(is_active=True)
        style_form(self)

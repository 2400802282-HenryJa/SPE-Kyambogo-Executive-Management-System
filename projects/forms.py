from django import forms
from django.contrib.auth import get_user_model

from .models import Milestone, Project, Task


def style_form(form):
    """Apply Bootstrap classes to every widget except checkboxes."""
    for field in form.fields.values():
        if isinstance(field.widget, forms.CheckboxInput):
            field.widget.attrs["class"] = "form-check-input"
        elif isinstance(field.widget, forms.Select):
            field.widget.attrs["class"] = "form-select"
        else:
            field.widget.attrs["class"] = "form-control"


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "expected_outcome",
            "department",
            "owner",
            "status",
            "priority",
            "start_date",
            "due_date",
            "challenges",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "expected_outcome": forms.Textarea(attrs={"rows": 2}),
            "challenges": forms.Textarea(attrs={"rows": 3}),
            "start_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "due_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["owner"].queryset = get_user_model().objects.filter(is_active=True)
        style_form(self)


class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ["title", "due_date", "completed"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form(self)


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "assignee", "due_date", "status"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assignee"].queryset = get_user_model().objects.filter(is_active=True)
        style_form(self)

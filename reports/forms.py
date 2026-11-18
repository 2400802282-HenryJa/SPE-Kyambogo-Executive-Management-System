from django import forms
from django.utils import timezone

from config.forms import style_form
from departments.models import Department

from .models import MonthlyReport

MAX_BYTES = 10 * 1024 * 1024


class ReportForm(forms.ModelForm):
    class Meta:
        model = MonthlyReport
        fields = ["department", "year", "month", "file", "summary"]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.localdate()
        self.fields["year"].initial = today.year
        self.fields["month"].initial = today.month
        if user is not None and not (user.is_superuser or user.is_top_executive):
            self.fields["department"].queryset = Department.objects.filter(head=user)
        style_form(self)

    def clean_file(self):
        f = self.cleaned_data["file"]
        if f.size > MAX_BYTES:
            raise forms.ValidationError("File is larger than 10 MB.")
        return f

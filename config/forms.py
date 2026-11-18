from django import forms
from django.contrib.auth.forms import AuthenticationForm


def style_form(form):
    """Apply Bootstrap classes to every widget in a form."""
    for field in form.fields.values():
        if isinstance(field.widget, forms.CheckboxInput):
            field.widget.attrs["class"] = "form-check-input"
        elif isinstance(field.widget, forms.Select):
            field.widget.attrs["class"] = "form-select"
        else:
            field.widget.attrs["class"] = "form-control"


def limit_department_choices(form, user, field="department"):
    """Non-top-executives may only pick departments they belong to or head."""
    from django.db.models import Q

    from departments.models import Department

    if user is None or user.is_superuser or user.is_top_executive:
        return
    allowed = Department.objects.visible_to(user)
    q = Q(pk__in=allowed.values("pk"))
    if form.instance.pk and form.instance.department_id:
        q |= Q(pk=form.instance.department_id)
    form.fields[field].queryset = Department.objects.filter(q)


class StyledAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form(self)
        self.fields["username"].widget.attrs.update(
            {"autofocus": True, "placeholder": "Username"}
        )
        self.fields["password"].widget.attrs.update({"placeholder": "Password"})

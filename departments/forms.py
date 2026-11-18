from django import forms
from django.contrib.auth import get_user_model

from config.forms import style_form


class AddMemberForm(forms.Form):
    person = forms.ModelChoiceField(queryset=get_user_model().objects.none())

    def __init__(self, *args, department, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["person"].queryset = (
            get_user_model()
            .objects.filter(is_active=True)
            .exclude(pk__in=department.members.values("pk"))
            .order_by("first_name", "username")
        )
        style_form(self)

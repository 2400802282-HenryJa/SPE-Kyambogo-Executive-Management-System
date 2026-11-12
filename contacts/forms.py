from django import forms

from config.forms import style_form

from .models import Contact, Interaction, Organisation


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = [
            "full_name",
            "organisation",
            "job_title",
            "category",
            "email",
            "phone",
            "expertise",
            "notes",
        ]
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form(self)


class OrganisationForm(forms.ModelForm):
    class Meta:
        model = Organisation
        fields = ["name", "kind", "website", "location", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form(self)


class InteractionForm(forms.ModelForm):
    class Meta:
        model = Interaction
        fields = ["date", "summary", "follow_up"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "summary": forms.Textarea(attrs={"rows": 3}),
            "follow_up": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form(self)

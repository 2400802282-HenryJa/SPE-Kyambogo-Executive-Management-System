from django import forms

from config.forms import limit_department_choices, style_form

from .models import Item, Mobilisation, StockMovement

DATE = {"type": "date"}


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            "name", "category", "description", "department", "unit_price",
            "unit_cost", "reorder_level", "storage_location", "is_active",
        ]
        widgets = {"description": forms.Textarea(attrs={"rows": 2})}

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        limit_department_choices(self, user)
        # Cost price is confidential.
        if user is not None:
            if self.instance.pk:
                can_cost = self.instance.finance_visible_to(user)
            else:
                can_cost = user.is_treasury_authorised or user.headed_departments.exists()
            if not can_cost:
                del self.fields["unit_cost"]
        style_form(self)


class MovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ["kind", "quantity", "unit_price", "date", "note"]
        widgets = {"date": forms.DateInput(attrs=DATE, format="%Y-%m-%d")}

    def __init__(self, *args, item, **kwargs):
        super().__init__(*args, **kwargs)
        self.item = item
        self.fields["unit_price"].initial = item.unit_price
        style_form(self)

    def clean(self):
        cleaned = super().clean()
        kind, qty = cleaned.get("kind"), cleaned.get("quantity")
        if kind and qty and kind in ("sale", "issue", "loss"):
            on_hand = self.item.quantity_on_hand
            if qty > on_hand:
                self.add_error("quantity", f"Only {on_hand} in stock.")
        return cleaned


class MobilisationForm(forms.ModelForm):
    class Meta:
        model = Mobilisation
        fields = ["title", "kind", "source", "amount", "description", "status", "date", "department"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
            "date": forms.DateInput(attrs=DATE, format="%Y-%m-%d"),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        limit_department_choices(self, user)
        style_form(self)

    def clean_department(self):
        dept = self.cleaned_data["department"]
        if self.user and not self.user.is_treasury_authorised and dept.head_id != self.user.pk:
            raise forms.ValidationError("You can only record mobilisation for a department you head.")
        return dept

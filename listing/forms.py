from django import forms
from .models import Listing

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ("link", "description", "tags")
        widgets = {
            "links": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "required": True,
                }
            )
        }

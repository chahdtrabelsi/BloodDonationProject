from django import forms
from .models import Don

class DonForm(forms.ModelForm):
    class Meta:
        model = Don
        fields = ['hopital', 'date_don', 'notes']
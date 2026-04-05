from django import forms
from .models import Campagne

class CampagneForm(forms.ModelForm):
    class Meta:
        model = Campagne
        fields = ['nom', 'date', 'lieu', 'groupes_cibles', 'capacite_totale', 'hopital']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'lieu': forms.TextInput(attrs={'class': 'form-control'}),
            'groupes_cibles': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: A+, B+, O-, ...'}),
            'capacite_totale': forms.NumberInput(attrs={'class': 'form-control'}),
            'hopital': forms.Select(attrs={'class': 'form-select'}),
        }
from django import forms
from django.forms import inlineformset_factory
from .models import Campagne, Creneau

# =========================
# Campagne Form
# =========================
class CampagneForm(forms.ModelForm):

    class Meta:
        model = Campagne
        fields = ['nom', 'date', 'lieu', 'groupes_cibles', 'capacite_totale']

        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de la campagne'
            }),

            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),

            'lieu': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lieu de la campagne'
            }),

            'groupes_cibles': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: A+, O-, B+'
            }),

            'capacite_totale': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
        }



class CreneauForm(forms.ModelForm):
    class Meta:
        model = Creneau
        fields = ['heure_debut', 'heure_fin', 'capacite']
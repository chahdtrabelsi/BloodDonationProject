from django import forms
from .models import Donneur, Hopital,MedicalProfile


class DonneurRegisterForm(forms.ModelForm):
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Donneur
        fields = ['groupe_sanguin', 'sexe', 'date_naissance', 'ville']


class HopitalRegisterForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Hopital
        fields = ['nom', 'adresse', 'ville', 'agrement']
        


class MedicalProfileForm(forms.ModelForm):

    class Meta:
        model = MedicalProfile
        fields = ['poids', 'a_tension', 'diabete', 'anemie', 'maladie_sanguine']

class DonneurUpdateForm(forms.ModelForm):
    class Meta:
        model = Donneur
        fields = ['groupe_sanguin', 'sexe', 'date_naissance', 'ville']
        
from django import forms

class MedicalProfileForm(forms.ModelForm):

    poids = forms.FloatField(required=True)

    class Meta:
        model = MedicalProfile
        exclude = ['donneur']
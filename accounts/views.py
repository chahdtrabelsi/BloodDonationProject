from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import DonneurRegisterForm, HopitalRegisterForm
from .models import Donneur, Hopital
from demandes.models import DemandeUrgente
from dons.models import Don

from django.shortcuts import render

def index(request):
    return render(request, 'accounts/index.html')

def register_donneur(request):
    if request.method == 'POST':
        form = DonneurRegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            Donneur.objects.create(
                user=user,
                groupe_sanguin=form.cleaned_data['groupe_sanguin'],
                sexe=form.cleaned_data['sexe'],
                date_naissance=form.cleaned_data['date_naissance'],
                ville=form.cleaned_data['ville']
            )
            messages.success(request, "Inscription réussie ! Vous pouvez vous connecter.")
            return redirect('dashboard_donneur')
    else:
        form = DonneurRegisterForm()
    return render(request, 'accounts/register_donneur.html', {'form': form})

def register_hopital(request):
    if request.method == 'POST':
        form = HopitalRegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            Hopital.objects.create(
                user=user,
                nom=form.cleaned_data['nom'],
                adresse=form.cleaned_data['adresse'],
                ville=form.cleaned_data['ville'],
                agrement=form.cleaned_data['agrement']
            )
            messages.success(request, "Inscription réussie ! En attente de validation admin.")
            return redirect('dashboard_hopital')
    else:
        form = HopitalRegisterForm()
    return render(request, 'accounts/register_hopital.html', {'form': form})
def dashboard_donneur(request):
    return render(request, 'accounts/dashboard_donneur.html')


def dashboard_hopital(request):
    return render(request, 'accounts/dashboard_hopital.html')
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import date

from .forms import DonneurRegisterForm, HopitalRegisterForm, MedicalProfileForm
from .models import Donneur, Hopital, MedicalProfile

from dons.models import Don
from demandes.models import DemandeUrgente, ReponseAppel


# =========================
# HOME
# =========================
def home(request):
    return render(request, 'accounts/home.html')


def index(request):
    role = None
    if request.user.is_authenticated:
        if hasattr(request.user, 'donneur'):
            role = 'donneur'
        elif hasattr(request.user, 'hopital'):
            role = 'hopital'

    return render(request, 'accounts/index.html', {'role': role})


# =========================
# REGISTER DONNEUR (STEP 1)
# =========================
def register_donneur(request):
    form = DonneurRegisterForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():

        username = form.cleaned_data['username']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username déjà utilisé")
            return redirect('register_donneur')

        user = User.objects.create_user(
            username=username,
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password']
        )

        donneur = Donneur.objects.create(
            user=user,
            groupe_sanguin=form.cleaned_data['groupe_sanguin'],
            sexe=form.cleaned_data['sexe'],
            date_naissance=form.cleaned_data['date_naissance'],
            ville=form.cleaned_data['ville']
        )

        return redirect('register_medicale', donneur_id=donneur.id)

    return render(request, 'accounts/register_donneur.html', {'form': form})
# =========================
# MEDICAL PROFILE (STEP 2)
# =========================

def register_medicale(request, donneur_id):
    donneur = get_object_or_404(Donneur, id=donneur_id)

    form = MedicalProfileForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():

        medical = form.save(commit=False)
        medical.donneur = donneur
        medical.save()

        
        login(request, donneur.user)

        return redirect('dashboard_donneur')

    return render(request, 'accounts/register_medicale.html', {
        'form': form,
        'donneur': donneur
    })
# =========================
# REGISTER HOPITAL
# =========================
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

            login(request, user)
            return redirect('dashboard_hopital')

    else:
        form = HopitalRegisterForm()

    return render(request, 'accounts/register_hopital.html', {'form': form})


# =========================
# LOGIN
# =========================
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if hasattr(user, 'donneur'):
                return redirect('dashboard_donneur')
            elif hasattr(user, 'hopital'):
                return redirect('dashboard_hopital')
            else:
                return redirect('index')

    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


# =========================
# LOGOUT
# =========================
def logout_view(request):
    logout(request)
    return redirect('index')


# =========================
# DASHBOARD DONNEUR
# =========================
@login_required
def dashboard_donneur(request):
    donneur = request.user.donneur

    medical = getattr(donneur, 'medicalprofile', None)

    historique_dons = Don.objects.filter(
        donneur=donneur,
        valide=True
    ).order_by('-date_don')

    compatibles = groupes_compatibles(donneur.groupe_sanguin)

    appels_compatibles = DemandeUrgente.objects.filter(
        groupe_sanguin__in=compatibles
    )

    repondu_ids = ReponseAppel.objects.filter(
        donneur=donneur
    ).values_list('demande_id', flat=True)

    return render(request, "accounts/dashboard_donneur.html", {
        "donneur": donneur,
        "medical": medical,
        "historique_dons": historique_dons,
        "appels_compatibles": appels_compatibles,
        "repondu_ids": repondu_ids,
        "est_eligible": donneur.est_eligible(),
    })


# =========================
# DASHBOARD HOPITAL
# =========================
@login_required
def dashboard_hopital(request):
    hopital = request.user.hopital

    demandes_publiees = DemandeUrgente.objects.filter(hopital=hopital)

    return render(request, "accounts/dashboard_hopital.html", {
        "hopital": hopital,
        "demandes_publiees": demandes_publiees
    })


# =========================
# ELIGIBILITE PAGE
# =========================
def fiche_eligibilite(request):
    donneur = request.user.donneur
    dernier_don = donneur.dons.order_by('-date_don').first()

    return render(request, 'accounts/fiche_eligibilite.html', {
        'donneur': donneur,
        'dernier_don': dernier_don,
        'date_today': date.today()
    })


def eligibilite(request):
    return render(request, 'accounts/eligibiliteGlobale.html')


# =========================
# COMPATIBILITE BLOOD GROUP
# =========================
def groupes_compatibles(groupe):
    compat = {
        'O-': ['O-', 'O+', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-'],
        'O+': ['O+', 'A+', 'B+', 'AB+'],
        'A-': ['A-', 'A+', 'AB-', 'AB+'],
        'A+': ['A+', 'AB+'],
        'B-': ['B-', 'B+', 'AB-', 'AB+'],
        'B+': ['B+', 'AB+'],
        'AB-': ['AB-', 'AB+'],
        'AB+': ['AB+'],
    }
    return compat.get(groupe, [])
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import date
from django.utils.timezone import now
from datetime import timedelta
from accounts.models import Notification

from .forms import DonneurRegisterForm, HopitalRegisterForm,DonneurUpdateForm,MedicalProfileForm
from .models import Donneur, Hopital, MedicalProfile

from dons.models import Don
from demandes.models import DemandeUrgente, ReponseAppel
from campagnes.models import Campagne,InscriptionCampagne,Creneau
from core.utils import groupes_compatibles
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
# REGISTER DONNEUR
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

        messages.success(request, "Compte créé, complétez votre dossier médical")

        return redirect('register_medicale', donneur_id=donneur.id)

    return render(request, 'accounts/register_donneur.html', {'form': form})


# =========================
# MEDICAL PROFILE
# =========================
def register_medicale(request, donneur_id):

    donneur = get_object_or_404(Donneur, id=donneur_id)

    # prevent duplicate medical profile
    medical, created = MedicalProfile.objects.get_or_create(donneur=donneur)

    form = MedicalProfileForm(
        request.POST or None,
        instance=medical
    )

    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.donneur = donneur
        obj.save()

        login(request, donneur.user)

        messages.success(request, "Inscription terminée avec succès")

        return redirect('dashboard_donneur')

    return render(request, 'accounts/register_medicale.html', {
        'form': form,
        'donneur': donneur
    })

# =========================
# REGISTER HOPITAL
# =========================
def register_hopital(request):
    form = HopitalRegisterForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():

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

        messages.success(request, "Compte hôpital créé avec succès")

        return redirect('dashboard_hopital')

    return render(request, 'accounts/register_hopital.html', {'form': form})


# =========================
# LOGIN
# =========================
def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)

        # 🟡 Admin
        if user.is_superuser:
            return redirect('admin_dashboard')

        # 🟢 Donneur
        if hasattr(user, 'donneur'):
            return redirect('dashboard_donneur')

        # 🔵 Hopital (IMPORTANT: check existence)
        if hasattr(user, 'hopital'):
            return redirect('dashboard_hopital')

        # 🔴 fallback (safety)
        return redirect('index')

    return render(request, 'accounts/login.html', {'form': form})
# =========================
# LOGOUT
# =========================
def logout_view(request):
    logout(request)
    request.session.flush() 
    messages.info(request, "Déconnecté avec succès")
    return redirect('home')


# =========================
# DASHBOARD DONNEUR
# =========================
@login_required
def dashboard_donneur(request):

    donneur = request.user.donneur
    medical = getattr(donneur, 'medicalprofile', None)

    historique_dons = Don.objects.filter(
        donneur=donneur
    ).select_related('hopital').order_by('-date_don')

    dernier_don = historique_dons.first()

    compatibles = groupes_compatibles(donneur.groupe_sanguin)

    # 🏥 campagnes futures compatibles
    all_campagnes = Campagne.objects.prefetch_related('creneaux').filter(
        date__gte=date.today()
    )

    participations = InscriptionCampagne.objects.filter(
        donneur=donneur
    ).select_related('creneau', 'creneau__campagne').order_by('-id')

    campagnes = [
        c for c in all_campagnes
        if any(
            g.strip().upper() in compatibles
            for g in (c.groupes_cibles or "").split(",")
        )
    ]

    # 🚨 appels urgents compatibles
    appels_compatibles = DemandeUrgente.objects.filter(
        groupe_sanguin__in=compatibles,
        statut='Ouvert',
        delai__gte=now().date()
    ).exclude(
        reponseappel__donneur=donneur
    ).order_by('delai')

    repondu_ids = set(
        ReponseAppel.objects.filter(donneur=donneur)
        .values_list('demande_id', flat=True)
    )

    appels_compatibles = [
        a for a in appels_compatibles if a.id not in repondu_ids
    ]

    # 📅 prochain don
    prochain_don = None
    if dernier_don:
        delai = 56 if donneur.sexe == 'Homme' else 84
        prochain_don = dernier_don.date_don + timedelta(days=delai)

    # 🔔 NOTIFICATIONS (CORRIGÉ)
    notifications = Notification.objects.filter(
        donneur=donneur
    ).order_by('-created_at')[:5]
    #Rappel compagne
    today = date.today()
    tomorrow = today + timedelta(days=1)

    rappels = InscriptionCampagne.objects.filter(
    donneur=donneur,
    creneau__campagne__date=tomorrow).select_related(
    "creneau__campagne")
    eligible, reason = donneur.est_eligible()
    return render(request, "accounts/dashboard_donneur.html", {
        "donneur": donneur,
        "prochain_don": prochain_don,
        "medical": medical,
        "historique_dons": historique_dons,
        "dernier_don": dernier_don,
        "appels_compatibles": appels_compatibles,
        "repondu_ids": repondu_ids,
        "is_eligible": eligible,
        "eligibility_reason": reason,
        "campagnes": campagnes,
        "participations": participations,
        "date_today": date.today(),

        # 🔔 notifications
        "notifications": notifications,
        "rappels": rappels,
    })
# =========================
# DASHBOARD HOPITAL
# =========================
from django.db.models import Count

@login_required
def dashboard_hopital(request):

    hopital = request.user.hopital

    demandes_publiees = DemandeUrgente.objects.filter(
        hopital=hopital
    ).annotate(
        total_reponses=Count('reponseappel')
    ).order_by('-delai')

    campagnes = Campagne.objects.filter(
        hopital=hopital
    ).prefetch_related('creneaux').order_by('-date')

    return render(request, "accounts/dashboard_hopital.html", {
        "hopital": hopital,
        "demandes_publiees": demandes_publiees,
        "campagnes": campagnes,
        "today": date.today()
    })
# =========================
# FICHE ELIGIBILITE
# =========================
@login_required
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



@login_required
def edit_donneur(request):
    donneur = request.user.donneur
    

    form = DonneurRegisterForm(request.POST or None, instance=donneur)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profil mis à jour avec succès")
        return redirect("dashboard_donneur")

    return render(request, "accounts/donneur_form.html", {
        "form": form,
        "mode": "edit"
    })
    
#update données personelles
@login_required
def edit_medical(request):

    donneur = request.user.donneur

    medical, created = MedicalProfile.objects.get_or_create(
        donneur=donneur
    )

    form = MedicalProfileForm(
        request.POST or None,
        instance=medical
    )

    if request.method == "POST" and form.is_valid():

        obj = form.save(commit=False)
        obj.donneur = donneur
        obj.save()

        return redirect("dashboard_donneur")

    return render(request, "accounts/edit_medical.html", {
        "form": form
    })

def processus_don(request):
    return render(request, "accounts/processus-don.html")


def notre_histoire(request):
    return render(request, 'accounts/notre_histoire.html')
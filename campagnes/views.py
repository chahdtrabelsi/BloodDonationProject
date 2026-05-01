from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CreneauForm, CampagneForm
from campagnes.models import Campagne, InscriptionCampagne, Creneau
from core.utils import est_compatible_campagne
from django.utils.timezone import now

@login_required
def creer_campagne(request):
    form = CampagneForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        campagne = form.save(commit=False)
        campagne.hopital = request.user.hopital
        campagne.save()

        messages.success(request, "Campagne créée avec succès")
        return redirect('campagnes:mes_campagnes')

    return render(request, 'campagnes/creer_campagne.html', {'form': form})


@login_required
def mes_campagnes(request):
    hopital = request.user.hopital

    campagnes = Campagne.objects.filter(
        hopital=hopital
    ).prefetch_related('creneaux')

    return render(request, 'campagnes/mes_campagnes.html', {
        'campagnes': campagnes,
        'hopital': hopital
    })


def index(request):
    return render(request, 'campagnes/index.html')


# ✅ INSCRIPTION CRÉNEAU (ONLY ONE FUNCTION)
@login_required
def inscrire_creneau(request, creneau_id):

    donneur = request.user.donneur
    creneau = get_object_or_404(Creneau, id=creneau_id)
    campagne = creneau.campagne

    # compatibility check
    if not est_compatible_campagne(donneur, campagne):
        messages.error(request, "❌ Groupe sanguin non compatible")
        return redirect('dashboard_donneur')

    # already registered
    if InscriptionCampagne.objects.filter(
        donneur=donneur,
        creneau=creneau
    ).exists():
        messages.warning(request, "Déjà inscrit")
        return redirect('dashboard_donneur')

    # capacity check
    if creneau.est_complet():
        messages.error(request, "Créneau complet")
        return redirect('dashboard_donneur')

    InscriptionCampagne.objects.create(
        donneur=donneur,
        creneau=creneau
    )

    messages.success(request, "Inscription réussie 🎉")
    return redirect('dashboard_donneur')


@login_required
def ajouter_creneau(request, campagne_id):

    campagne = get_object_or_404(Campagne, id=campagne_id)
    form = CreneauForm(request.POST or None)
    error = None

    if request.method == "POST" and form.is_valid():

        total = sum(c.capacite for c in campagne.creneaux.all())
        new_cap = form.cleaned_data['capacite']

        if total + new_cap > campagne.capacite_totale:
            error = "❌ Capacité dépassée"
        else:
            creneau = form.save(commit=False)
            creneau.campagne = campagne
            creneau.save()

            messages.success(request, "Créneau ajouté")
            return redirect('campagnes:mes_campagnes')

    return render(request, 'campagnes/ajouter_creneau.html', {
        'form': form,
        'campagne': campagne,
        'error': error
    })

@login_required
def annuler_participation(request, inscription_id):

    donneur = request.user.donneur

    inscription = get_object_or_404(
        InscriptionCampagne,
        id=inscription_id,
        donneur=donneur
    )

    # ❌ sécurité : vérifier si déjà passé
    if inscription.creneau.campagne.date < now().date():
        messages.error(request, "❌ Impossible d'annuler une campagne passée")
        return redirect('dashboard_donneur')

    inscription.delete()

    messages.success(request, "✔ Participation annulée avec succès")
    return redirect('dashboard_donneur')
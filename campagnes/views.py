from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CreneauForm, CampagneForm
from campagnes.models import Campagne, InscriptionCampagne, Creneau
from core.utils import est_compatible_campagne
from django.utils.timezone import now
from accounts.models import Notification
from campagnes.models import Campagne, InscriptionCampagne, Creneau
from accounts.models import Notification,Donneur

@login_required
def creer_campagne(request):
    form = CampagneForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        campagne = form.save(commit=False)
        campagne.hopital = request.user.hopital
        campagne.save()

        messages.success(request, "Campagne créée avec succès")
        return redirect('dashboard_hopital')

    return render(request, 'campagnes/creer_campagne.html', {'form': form})




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
            return redirect('dashboard_hopital')

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

def annuler_creneau(request, id):

    creneau = get_object_or_404(Creneau, id=id)

    # 👥 récupérer les donneurs inscrits
    inscriptions = InscriptionCampagne.objects.filter(creneau=creneau)
    donneurs = [i.donneur for i in inscriptions]

    # ❌ supprimer inscriptions
    inscriptions.delete()

    # 🔔 notifications
    for d in donneurs:
        Notification.objects.create(
            donneur=d,
            message=f"⚠️ Le créneau {creneau} a été annulé.",
            type="creneau"
        )

    # ❌ supprimer créneau
    creneau.delete()

    return redirect('dashboard_hopital')

def annuler_campagne(request, id):

    campagne = get_object_or_404(Campagne, id=id)

    # 👥 tous les inscrits à la campagne
    inscriptions = InscriptionCampagne.objects.filter(
        creneau__campagne=campagne
    )
    donneurs = Donneur.objects.filter(
    id__in=inscriptions.values_list('donneur_id', flat=True)
)

    # ❌ supprimer inscriptions
    inscriptions.delete()

    # ❌ supprimer créneaux
    campagne.creneaux.all().delete()

    # 🔔 notifications
    for d in donneurs:
        Notification.objects.create(
            donneur=d,
            message=f"🚨 La campagne {campagne.nom} a été annulée.",
            type="campagne"
        )

    # ❌ supprimer campagne
    campagne.delete()

    return redirect('accounts:dashboard_hopital')

def voir_participants_creneau(request, id):
    creneau = get_object_or_404(Creneau, id=id)

    participants = InscriptionCampagne.objects.filter(
        creneau=creneau
    ).select_related('donneur', 'donneur__user')

    return render(request, "campagnes/participants_creneau.html", {
        "creneau": creneau,
        "participants": participants
    })
from django.shortcuts import render,redirect
from .forms import DemandeUrgenteForm
from .models import DemandeUrgente
from django.contrib.auth.decorators import login_required
from .models import DemandeUrgente
from django.shortcuts import render, get_object_or_404

def creer_demande(request):
    if request.method == "POST":
        form = DemandeUrgenteForm(request.POST)

        if form.is_valid():
            demande = form.save(commit=False)  

            demande.hopital = request.user.hopital  

            demande.statut = "Ouvert"  

            demande.save()

            return redirect('demandes:liste_demandes')

    else:
        form = DemandeUrgenteForm()

    return render(request, 'demandes/creer_demande.html', {
        'form': form
    })
def liste_demandes(request):
    demandes = DemandeUrgente.objects.all().order_by('-id')
    return render(request, 'demandes/liste_demandes.html', {
        'demandes': demandes
    })

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import DemandeUrgente, ReponseAppel

@login_required
def repondre(request, id):
    demande = get_object_or_404(DemandeUrgente, id=id)
    donneur = request.user.donneur

    if request.method == "POST":

        
        existe = ReponseAppel.objects.filter(
            donneur=donneur,
            demande=demande
        ).exists()

        if not existe:
            ReponseAppel.objects.create(
                donneur=donneur,
                demande=demande
            )

        return redirect('dashboard_donneur')

    return render(request, 'demandes/repondre.html', {
        'demande': demande
    })
def modifier_demande(request, id):
    demande = get_object_or_404(DemandeUrgente, id=id)

    form = DemandeUrgenteForm(request.POST or None, instance=demande)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect('demandes:liste_demandes')

    return render(request, "demandes/modifier.html", {
        "form": form,
        "demande": demande
    })
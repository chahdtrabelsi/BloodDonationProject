from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import DonForm

@login_required
def ajouter_don(request):
    donneur = request.user.donneur

    
    if not donneur.est_eligible():
        messages.error(request, "Vous n'êtes pas éligible pour donner du sang.")
        return redirect("dashboard_donneur")

    if request.method == "POST":
        form = DonForm(request.POST)

        if form.is_valid():
            don = form.save(commit=False)
            don.donneur = donneur
            don.valide = False
            don.save()

            messages.success(request, "Don ajouté avec succès.")
            return redirect("dashboard_donneur")

    else:
        form = DonForm()

    return render(request, "dons/ajouter_don.html", {"form": form})
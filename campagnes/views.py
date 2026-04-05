from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from campagnes.models import Campagne
from accounts.models import Hopital
from django.contrib import messages
from .forms import CampagneForm

def creer_campagne(request):
    if request.method == "POST":
        form = CampagneForm(request.POST)
        if form.is_valid():
            campagne = form.save(commit=False)
            campagne.hopital = request.user.hopital
            campagne.save()
            return redirect('campagnes:mes_campagnes')
    else:
        form = CampagneForm()

    return render(request, 'campagnes/creer_campagne.html', {'form': form})
def mes_campagnes(request):
    campagnes = Campagne.objects.all()  
    return render(request, 'campagnes/mes_campagnes.html', {'campagnes': campagnes})
def index(request):
    return render(request, 'campagnes/index.html')
from django.shortcuts import render

from .models import Don
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
@login_required
def ajouter_don(request):
    if request.method == "POST":
        hopital_id = request.POST.get("hopital")
        date_don = request.POST.get("date_don")
        notes = request.POST.get("notes")

        Don.objects.create(
            donneur=request.user.donneur,
            hopital_id=hopital_id,
            date_don=date_don,
            notes=notes,
            valide=False
        )

        return redirect("accounts:dashboard_donneur")
    
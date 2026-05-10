from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.db.models import Count
import csv
from campagnes.models import Campagne
from accounts.models import Donneur, Hopital
from dons.models import Don
from demandes.models import DemandeUrgente

from django.db.models.functions import ExtractMonth
import calendar
from datetime import date,timedelta
from django.utils import timezone




class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/admin/dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # =========================
        # 📊 KPIs (cards)
        # =========================
        context["total_donneurs"] = Donneur.objects.count()
        context["total_dons"] = Don.objects.count()
        context["demandes_actives"] = DemandeUrgente.objects.filter(statut="Ouvert").count()
        context["hopitals_en_attente"] = Hopital.objects.filter(valide=False).count()

        # =========================
        # 🩸 Donneurs par groupe sanguin
        # =========================
        donneurs_par_groupe = (
            Donneur.objects.values("groupe_sanguin")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

        context["donneurs_group_labels"] = [
            item["groupe_sanguin"] for item in donneurs_par_groupe
        ]
        context["donneurs_group_data"] = [
            item["total"] for item in donneurs_par_groupe
        ]

        # =========================
        # 📋 Demandes par groupe sanguin
        # =========================
        demandes_par_groupe = (
            DemandeUrgente.objects
            .filter(statut="Ouvert")
            .values("groupe_sanguin")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

        context["demandes_group_labels"] = [
            item["groupe_sanguin"] for item in demandes_par_groupe
        ]
        context["demandes_group_data"] = [
            item["total"] for item in demandes_par_groupe
        ]

        # =========================
        # 📈 Donneurs par mois
        # =========================
        donneurs_stats = (
            Donneur.objects
            .annotate(month=ExtractMonth("user__date_joined"))
            .values("month")
            .annotate(total=Count("id"))
            .order_by("month")
        )

        context["donneurs_labels"] = [
            calendar.month_name[item["month"]] for item in donneurs_stats
        ]
        context["donneurs_data"] = [
            item["total"] for item in donneurs_stats
        ]

        # =========================
        # 🏥 Hôpitaux par mois
        # =========================
        hopital_stats = (
            Hopital.objects
            .annotate(month=ExtractMonth("user__date_joined"))
            .values("month")
            .annotate(total=Count("id"))
            .order_by("month")
        )

        context["hopital_labels"] = [
            calendar.month_name[item["month"]] for item in hopital_stats
        ]
        context["hopital_data"] = [
            item["total"] for item in hopital_stats
        ]

        
        campagnes = Campagne.objects.prefetch_related("creneaux__inscriptions")

        total = campagnes.count()

        succes = 0
        partiel = 0
        faible = 0

        for c in campagnes:

            total_places = 0
            total_taken = 0

            for cr in c.creneaux.all():
                total_places += cr.capacite
                total_taken += cr.inscriptions.count()

            if total_places and total_taken >= total_places:
                succes += 1
            elif total_taken > 0:
                partiel += 1
            else:
                faible += 1
                
        

        context["campagnes_total"] = total
        context["campagnes_chart_labels"] = ["Succès", "Partiel", "Non satisfaites"]
        context["campagnes_chart_data"] = [succes, partiel, faible]
        today = timezone.now().date()
        next_week = today + timedelta(days=7)

        context["campagnes_bientot"] = Campagne.objects.filter(
        date__range=(today, next_week)
        ).count()
        context["total_hopitals"] = Hopital.objects.count()
        context["donneurs_eligible"] = Donneur.objects.filter(dons__isnull=True).count()
        return context
# =========================
# VALIDATE HOPITAL
# =========================
class ValidateHopitalView(View):

    def post(self, request, pk):
        if not request.user.is_superuser:
            raise PermissionDenied

        hopital = get_object_or_404(Hopital, pk=pk)
        hopital.valide = True
        hopital.save()

        return redirect("admin_dashboard")


# =========================
# EXPORT CSV
# =========================
class ExportDonneursCSV(View):

    def get(self, request):

        if not request.user.is_superuser:
            raise PermissionDenied

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="donneurs.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'ID',
            'Username',
            'Email',
            'Groupe sanguin',
            'Ville',
            'Sexe'
        ])

        for d in Donneur.objects.all():
            writer.writerow([
                d.id,
                d.user.username,
                d.user.email,
                d.groupe_sanguin,
                d.ville,
                d.sexe
            ])

        return response


# =========================
# MAP VIEW
# =========================
class AdminMapView(TemplateView):
    template_name = "accounts/admin/map.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["data"] = (
            DemandeUrgente.objects
            .values("hopital__ville")   # ✔ FIXED
            .annotate(total=Count("id"))
            .order_by("-total")
        )

        return context

class AdminHopitalListView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/admin/hopitaux.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["hopitaux"] = Hopital.objects.all().order_by("-id")

        return context
# =========================
# LISTE DONNEURS
# =========================
class AdminDonneurListView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/admin/donneurs.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["donneurs"] = Donneur.objects.select_related("user").all().order_by("-id")

        return context


# =========================
# Demandes actives
# =========================
    
from django.db.models import Count

from django.db.models import Count

class AdminDemandesActivesView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/admin/demandes_actives.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 🔵 demandes actives
        context["demandes_actives"] = (
            DemandeUrgente.objects
            .filter(statut="Ouvert")
            .select_related("hopital")
            .annotate(nb_reponses=Count("reponseappel"))
        )

        # 🔴 demandes clôturées
        context["demandes_cloturees"] = (
            DemandeUrgente.objects
            .filter(statut="Clôturé")
            .select_related("hopital")
            .annotate(nb_reponses=Count("reponseappel"))
        )

        return context

class AdminCampagnesView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/admin/campagnes.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        campagnes = (
            Campagne.objects
            .select_related("hopital")
            .prefetch_related("creneaux__inscriptions")
        )

        grouped = {}

        for c in campagnes:
            total_places = 0
            total_taken = 0

            for cr in c.creneaux.all():
                total_places += cr.capacite
                total_taken += cr.inscriptions.count()

            if total_places and total_taken >= total_places:
                status = "Succès"
            elif total_taken > 0:
                status = "Partiel"
            else:
                status = "Faible"

            hopital_name = c.hopital.nom

            if hopital_name not in grouped:
                grouped[hopital_name] = []

            grouped[hopital_name].append({
                "campagne": c,
                "places": total_places,
                "taken": total_taken,
                "status": status
            })

        context["campagnes_by_hopital"] = grouped
        
        campagnes = Campagne.objects.select_related("hopital").prefetch_related("creneaux__inscriptions")

        grouped = {}

        today = date.today()

        for c in campagnes:

            total_places = 0
            total_taken = 0

            for cr in c.creneaux.all():
                total_places += cr.capacite
                total_taken += cr.inscriptions.count()

            if c.date > today:
                status_time = "A_venir"
            elif c.date == today:
                status_time = "En_cours"
            else:
                status_time = "Terminee"

            if total_places and total_taken >= total_places:
                status_fill = "Succès"
            elif total_taken > 0:
                status_fill = "Partiel"
            else:
                status_fill = "Faible"

            hopital = c.hopital.nom

            if hopital not in grouped:
                grouped[hopital] = []

            grouped[hopital].append({
                "campagne": c,
                "places": total_places,
                "taken": total_taken,
                "status_fill": status_fill,
                "status_time": status_time
            })

            context["campagnes_by_hopital"] = grouped

        return context
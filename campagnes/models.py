from django.db import models

# Create your models here.
from django.db import models
from accounts.models import Hopital
from accounts.models import Donneur

class Campagne(models.Model):
    nom = models.CharField(max_length=100)
    date = models.DateField()
    lieu = models.CharField(max_length=100)
    groupes_cibles = models.CharField(
        max_length=50,
        help_text="Ex: A+, O-, B+"
    )
    capacite_totale = models.PositiveIntegerField()
    hopital = models.ForeignKey(Hopital, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nom} ({self.date})"
    
class Creneau(models.Model):
    campagne = models.ForeignKey("Campagne", on_delete=models.CASCADE, related_name="creneaux")
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    capacite = models.PositiveIntegerField()
    def places_restantes(self):
        return self.capacite - self.inscriptions.count()

    def est_complet(self):
        return self.places_restantes() <= 0
    
    def __str__(self):
        return f"{self.campagne.nom} | {self.heure_debut} - {self.heure_fin}"
    

class InscriptionCampagne(models.Model):
    donneur = models.ForeignKey("accounts.Donneur", on_delete=models.CASCADE)
    creneau = models.ForeignKey("Creneau", on_delete=models.CASCADE,related_name="inscriptions")
    class Meta:
        unique_together = ('donneur', 'creneau')
    def __str__(self):
        return f"{self.donneur.user.username} -> {self.creneau}"
from django.db import models

# Create your models here.
from django.db import models
from accounts.models import Hopital

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
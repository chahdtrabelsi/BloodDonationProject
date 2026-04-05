from django.db import models
from accounts.models import Hopital

class DemandeUrgente(models.Model):
    STATUT_CHOICES = (
        ('Ouvert', 'Ouvert'),
        ('Clôturé', 'Clôturé'),
    )
    groupe_sanguin = models.CharField(max_length=3)
    quantite = models.PositiveIntegerField()
    delai = models.DateField()
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='Ouvert')
    description = models.TextField()
    hopital = models.ForeignKey(Hopital, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.groupe_sanguin} - {self.quantite} poches - {self.hopital.nom}"
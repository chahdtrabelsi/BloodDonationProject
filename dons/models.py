from django.db import models
from accounts.models import Donneur, Hopital

class Don(models.Model):
    donneur = models.ForeignKey(Donneur, on_delete=models.CASCADE) 
    hopital = models.ForeignKey(Hopital, on_delete=models.CASCADE)   
    date_don = models.DateField()                                     
    notes = models.TextField(blank=True, null=True)                   
    valide = models.BooleanField(default=False)                       

    def __str__(self):
        return f"Don de {self.donneur.user.username} à {self.hopital.nom} le {self.date_don}"
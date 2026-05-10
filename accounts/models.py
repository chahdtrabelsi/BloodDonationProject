
from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from datetime import date
class Donneur(models.Model):
    SEXE_CHOICES = [('M', 'Homme'), ('F', 'Femme')]
    GROUPE_SANGUIN_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    groupe_sanguin = models.CharField(max_length=3, choices=GROUPE_SANGUIN_CHOICES)
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES)
    date_naissance = models.DateField()
    ville = models.CharField(max_length=100)
    actif = models.BooleanField(default=True)  
    @property
    def medical(self):
        return getattr(self, 'medicalprofile', None)

    def __str__(self):
        return f"{self.user.username} ({self.groupe_sanguin})"

    from datetime import timedelta

    def prochaine_date_don(self):
        dernier_don = self.dons.order_by('-date_don').first()

        if not dernier_don:
            return None

        if self.sexe == 'M':
            return dernier_don.date_don + timedelta(days=56)

        return dernier_don.date_don + timedelta(days=84)

    def est_eligible(self):
        mp = self.medical

        if mp.a_tension:
            return False, "Tension"
        if mp.diabete:
            return False, "Diabète"
        if mp.anemie:
            return False, "Anémie"
        if mp.maladie_sanguine:
            return False, "Maladie sanguine"
        if not mp.poids:
            return False, "Poids manquant"

        prochaine = self.prochaine_date_don()
        if prochaine and date.today() < prochaine:
            return False, "Période d'attente"

        return True, "OK"
class Hopital(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=200)
    adresse = models.CharField(max_length=200)
    ville = models.CharField(max_length=100)
    agrement = models.CharField(max_length=50)
    valide = models.BooleanField(default=False)  

    def __str__(self):
        return self.nom
    

class MedicalProfile(models.Model):
    donneur = models.OneToOneField(Donneur, on_delete=models.CASCADE)

    poids = models.FloatField(null=True, blank=True)
    taille = models.FloatField(null=True, blank=True)
    a_tension = models.BooleanField(default=False)
    diabete = models.BooleanField(default=False)
    anemie = models.BooleanField(default=False)
    maladie_sanguine = models.BooleanField(default=False)
    dernier_don_medical_ok = models.BooleanField(default=True)

from django.db import models
from accounts.models import Donneur

class Notification(models.Model):

    TYPE_CHOICES = [
        ('info', 'Info'),
        ('creneau', 'Créneau'),
        ('campagne', 'Campagne'),
        ('systeme', 'Système'),
    ]

    donneur = models.ForeignKey(
        Donneur,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    message = models.TextField()

    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='info'
    )

    lu = models.BooleanField(default=False) 

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donneur.user.username} - {self.type}"
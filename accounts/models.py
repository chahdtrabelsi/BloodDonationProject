
from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta

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
    actif = models.BooleanField(default=True)  # désactivation temporaire

    def __str__(self):
        return f"{self.user.username} ({self.groupe_sanguin})"

    def prochaine_date_don(self, dernier_don_date):
        if self.sexe == 'M':
            return dernier_don_date + timedelta(days=56)
        return dernier_don_date + timedelta(days=84)


class Hopital(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=200)
    adresse = models.CharField(max_length=200)
    ville = models.CharField(max_length=100)
    agrement = models.CharField(max_length=50)
    valide = models.BooleanField(default=False)  # validation par admin

    def __str__(self):
        return self.nom

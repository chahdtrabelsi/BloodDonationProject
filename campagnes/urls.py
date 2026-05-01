from django.urls import path
from . import views

app_name = 'campagnes'

urlpatterns = [
    path('', views.index, name='index'),

    # 🏥 Hôpital
    path('creer/', views.creer_campagne, name='creer_campagne'),
    path('mes-campagnes/', views.mes_campagnes, name='mes_campagnes'),
    path('creneau/ajouter/<int:campagne_id>/', views.ajouter_creneau, name='ajouter_creneau'),

    # 🩸 Donneur (INSCRIPTION CRÉNEAU)
    path('inscription/<int:creneau_id>/', views.inscrire_creneau, name='inscription_creneau'),
    path(
    'annuler/<int:inscription_id>/',
    views.annuler_participation,
    name='annuler_participation'
),
]

from django.urls import path
from . import views

app_name = 'demandes'
urlpatterns = [
    path('creer/', views.creer_demande, name='creer_demande'),
    path('liste/', views.liste_demandes, name='liste_demandes'),
    path('repondre/<int:id>/', views.repondre, name='repondre'),
    path('modifier/<int:id>/', views.modifier_demande, name='modifier'),
    path('cloturer/<int:id>/', views.cloturer_demande, name='cloturer'),
    path('donneurs/<int:id>/', views.donneurs_repondus, name='donneurs_repondus'),
    path('reouvrir/<int:id>/', views.reouvrir_demande, name='reouvrir')
]

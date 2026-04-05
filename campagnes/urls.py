from django.urls import path
from . import views

app_name = 'campagnes'  

urlpatterns = [
    path('', views.index, name='index'),
    path('creer/', views.creer_campagne, name='creer_campagne'),
    path('mes-campagnes/', views.mes_campagnes, name='mes_campagnes'),
]


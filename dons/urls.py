from django.urls import path
from . import views

app_name = "dons"

urlpatterns = [
    path('ajouter/', views.ajouter_don, name='ajouter_don'),
]
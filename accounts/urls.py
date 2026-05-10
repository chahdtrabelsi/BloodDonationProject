from django.urls import path
from . import views
from accounts.admin_views import (
    AdminDashboardView,
    ValidateHopitalView,
    ExportDonneursCSV,
    AdminMapView,
    AdminHopitalListView,
     AdminDonneurListView,
     AdminDemandesActivesView,
     AdminCampagnesView,
)
urlpatterns = [
    path('', views.index, name='index'),

    path('register/donneur/', views.register_donneur, name='register_donneur'),

    path('register/medicale/<int:donneur_id>/', views.register_medicale, name='register_medicale'),

    path('register/hopital/', views.register_hopital, name='register_hopital'),

    path('donneur/', views.dashboard_donneur, name='dashboard_donneur'),
    path('hopital/', views.dashboard_hopital, name='dashboard_hopital'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
     path('notre-histoire/', views.notre_histoire, name='notre_histoire'),
    path('fiche-eligibilite/', views.fiche_eligibilite, name='fiche_eligibilite'),
    path('eligibility/', views.eligibilite, name='eligibiliteGlobale'),
    path('processus-don/', views.processus_don, name='processus-don'),
    path('donneur/edit/', views.edit_donneur, name='edit_donneur'),
    path('donneur/editMedical/', views.edit_medical, name='edit_medical'),
    
    path("admin/dashboard/", AdminDashboardView.as_view(), name="admin_dashboard"),
    path("admin/hopital/validate/<int:pk>/", ValidateHopitalView.as_view(), name="validate_hopital"),
    path("admin/export/donneurs/", ExportDonneursCSV.as_view(), name="export_donneurs"),
    path("admin/map/", AdminMapView.as_view(), name="admin_map"),
    path("admin/hopitaux/", AdminHopitalListView.as_view(), name="admin_hopitaux"),
    path("admin/donneurs/", AdminDonneurListView.as_view(), name="admin_donneurs"),
    path(
    "admin/demandes-actives/",
    AdminDemandesActivesView.as_view(),
    name="admin_demandes_actives"
),
    path("admin/campagnes/", AdminCampagnesView.as_view(), name="admin_campagnes"),
]
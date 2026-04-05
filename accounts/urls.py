from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),  
    path('register/donneur/', views.register_donneur, name='register_donneur'),
    path('register/hopital/', views.register_hopital, name='register_hopital'),
    path('donneur/', views.dashboard_donneur, name='dashboard_donneur'),
    path('hopital/', views.dashboard_hopital, name='dashboard_hopital')
]
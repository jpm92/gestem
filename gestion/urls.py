from django.urls import path
from . import views


urlpatterns = [
    path('tablon/', views.Tablon.as_view(), name='tablon'),
    path('secretaria/', views.Secretario.as_view(), name='secretaria'),
    path('anotar/', views.NuevaNota, name='anotar'),
    path('autogestion/', views.AutoGestion, name='autogestion'),
]

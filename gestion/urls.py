from django.urls import path, include
from . import views
from django.views.generic import RedirectView


urlpatterns = [
    path('', RedirectView.as_view(url='/tablon/', permanent=True)),
    path('tablon/', views.Tablon.as_view(), name='tablon'),
    path('secretaria/', views.Secretario.as_view(), name='secretaria'),
    path('anotar/', views.NuevaNota, name='anotar'),
    path('autogestion/', views.AutoGestion, name='autogestion'),
    path('producto/', views.CrearProducto.as_view(), name='producto'),
    path('cuentas/', include('django.contrib.auth.urls')),
]

from django.urls import path, include
from . import views
from django.views.generic import RedirectView


urlpatterns = [
    path('', RedirectView.as_view(url='/tablon/', permanent=True)),
    path('tablon/', views.Tablon.as_view(), name='tablon'),
    path('secretaria/', views.Secretario.as_view(), name='secretaria'),
    path('anotar/', views.NuevaNota, name='anotar'),
    path('autogestion/', views.AutoGestion, name='autogestion'),
    path('producto/crear', views.CrearProducto.as_view(), name='nproducto'),
    path('cuentas/', include('django.contrib.auth.urls')),
    path('articulo/<int:pk>/recepcionar/', views.Recepcion, name='recepcion'),
    path('articulo/<int:pk>/reclamar', views.Reclamar, name='reclamar')
]

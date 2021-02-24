from django.urls import path, include
from . import views
from django.views.generic import RedirectView


urlpatterns = [
    path('', RedirectView.as_view(url='/tablon/', permanent=True)),
    path('tablon/', views.Tablon.as_view(), name='tablon'),
    path('secretaria/', views.Secretario.as_view(), name='secretaria'),
    path('anotar/', views.NuevaNota, name='anotar'),
    path('autogestion/', views.AutoGestion, name='autogestion'),
    path('productos', views.ListaProductos.as_view(), name='productos'),
    path(
        'producto/<int:pk>', views.DetalleProducto.as_view(), name='producto'
    ),
    path('producto/crear', views.CrearProducto.as_view(), name='nproducto'),
    path('cuentas/', include('django.contrib.auth.urls')),
    path('cuentas/password', views.cambio_password, name='cambiopassword'),
    path(
        'articulo/<int:pk>', views.ArticuloDetalle.as_view(), name='articulo'
    ),
    path('articulo/<int:pk>/recepcionar/', views.Recepcion, name='recepcion'),
    path('articulo/<int:pk>/reclamar', views.Reclamar, name='reclamar'),
    path('articulo/<int:pk>/cancelar', views.Cancelar, name='cancelar'),
    path('pedidos/', views.HistorialPedidos.as_view(), name='pedidos'),
    path('pedido/<int:pk>', views.PedidoDetalle.as_view(), name='pedido'),
    path('pedido/<int:pk>/cpm', views.CPM, name='cpm'),
    path('pedido/<int:pk>/confirmar', views.Confirmar, name='confirmar'),
    path('historial', views.HistorialNotas.as_view(), name='historial'),
    path(
        'historial/nota/<int:pk>',
        views.DetalleNota.as_view(),
        name='nota'
    ),
    path('b_articulo/', views.BusquedaArticulo, name='barticulo'),
    path('b_pedido/', views.BusquedaPedido, name='bpedido'),
    path('b_producto/', views.BusquedaProducto, name='bproducto'),
    path('salir/', views.salir, name='salir'),
]

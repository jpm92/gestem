from django.contrib import admin
from gestion.models import (
    Producto,
    Articulo,
    Pedido,
    CentroGasto,
    Entrega,
    Almacen,
    Fabricante,
    Distribuidor,
    Nota
)

# Register your models here.
# TODO: Registrar modelos en el panel de administración.

admin.site.register(Producto)
admin.site.register(Articulo)
admin.site.register(Pedido)
admin.site.register(CentroGasto)
admin.site.register(Entrega)
admin.site.register(Almacen)
admin.site.register(Fabricante)
admin.site.register(Distribuidor)
admin.site.register(Nota)

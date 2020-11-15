from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from gestem.aux import keygen
from gestion.models import (
    Producto,
    Articulo,
    Pedido,
    CentroGasto,
    Entrega,
    Almacen,
    Fabricante,
    Distribuidor,
    Nota,
    PerfilExtendido
)

# Register your models here.
# TODO: Registrar modelos en el panel de administración.


class ProductoAdmin(ImportExportModelAdmin):
    pass


class ArticuloAdmin(ImportExportModelAdmin):

    list_display = ('producto', 'unidades', 'nota', 'estado', 'pedido',)
    list_filter = ('estado',)
    list_display_links = ('producto',)
    actions = ['asignar_pedido']

    def asignar_pedido(self, request, queryset):
        f = queryset.first()
        p = Pedido.objects.create(
            codigo=keygen(),
            entrega=f.nota.entrega,
            distribuidor=f.producto.distribuidor
        )
        for a in queryset:
            a.pedido = p
            a.estado = 'i'
            a.save()

    asignar_pedido.short_description = _("Crear pedido")


class ArticuloInline(admin.TabularInline):
    model = Articulo


class PedidoAdmin(ImportExportModelAdmin):
    list_display = ('fecha_creacion', 'codigo', 'cpm', 'estado',
                    'distribuidor', 'entrega', 'centro_gasto')
    list_filter = ('estado',)
    list_display_links = ('codigo',)
    readonly_fields = ('fecha_creacion', 'fecha_cpm', 'fecha_confirmacion',
                       'fecha_cierre')
    fieldsets = (
        (_('Información del pedido'), {
            'fields': ('codigo', 'cpm', 'estado', 'distribuidor', 'entrega',
                       'centro_gasto')
        }),
        (_('Cronología'), {
            'classes': ('collapse',),
            'fields': ('fecha_creacion', 'fecha_cpm', 'fecha_confirmacion',
                       'fecha_cierre'),
        }),
    )
    inlines = (ArticuloInline,)


class ExtendidoInLine(admin.TabularInline):
    model = PerfilExtendido
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = (ExtendidoInLine,)


admin.site.register(Producto)
admin.site.register(Articulo, ArticuloAdmin)
admin.site.register(Pedido, PedidoAdmin)
admin.site.register(CentroGasto)
admin.site.register(Entrega)
admin.site.register(Almacen)
admin.site.register(Fabricante)
admin.site.register(Distribuidor)
admin.site.register(Nota)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

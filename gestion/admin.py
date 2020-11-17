from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.urls import path
from django.shortcuts import redirect
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

    list_display = ('nombre_fabricante', 'fabricante', 'referencia', 'formato',
                    'distribuidor', 'categoria')
    list_filter = ('categoria',)
    search_fields = ('nombre_fabricante', 'referencia', 'nombre_amistoso')


class ArticuloAdmin(ImportExportModelAdmin):

    list_display = ('fecha', 'usuario', 'producto', 'unidades', 'nota',
                    'estado', 'pedido',)
    list_filter = ('estado',)
    list_display_links = ('producto',)
    autocomplete_fields = ('producto',)
    list_select_related = ('pedido',)
    actions = ['crear_pedido']
    readonly_fields = ('fecha_recepcion',)
    change_list_template = "gestion/articulos_admin.html"

    def crear_pedido(self, request, queryset):
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

        self.message_user(request, _(f'¡Pedido {p.codigo} creado con éxito!'))
        return redirect('admin:gestion_pedido_changelist')

    crear_pedido.short_description = _("Crear pedido")

    def fecha(self, obj):
        return obj.nota.fecha

    def usuario(self, obj):
        return obj.nota.usuario

    def magia(self, request):
        """ Este método se ejecuta al pulsar el boton en admin. Itera sobre
        todos los artículos pendientes y los autoincluye en pedidos nuevos. """

        articulos = Articulo.objects.filter(estado='p')
        if articulos.count() == 0:
            self.message_user(
                request,
                _('¡No hay articulos pendientes de procesar!')
                )
            return redirect('admin:gestion_articulo_changelist')
        else:
            distribuidor = {}
            cuenta = 0

            for articulo in articulos:
                dist = articulo.producto.distribuidor
                if dist not in distribuidor.keys():
                    distribuidor[dist] = [articulo]
                else:
                    distribuidor[dist].append(articulo)
            for d in distribuidor:
                entregas = {}
                for a in distribuidor[d]:
                    entrega = a.nota.entrega
                    if entrega not in entregas.keys():
                        entregas[entrega] = [a]
                    else:
                        entregas[entrega].append(a)
                for e in entregas:
                    a = entregas[e][0]
                    p = Pedido.objects.create(
                        codigo=keygen(),
                        entrega=a.nota.entrega,
                        distribuidor=a.producto.distribuidor
                    )
                    cuenta += 1
                    for articulo in entregas[e]:
                        articulo.pedido = p
                        articulo.estado = 'i'
                        articulo.save()
            self.message_user(
                request,
                _(f'¡{cuenta} pedidos creados con éxito!')
                )
            return redirect('admin:gestion_pedido_changelist')

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('clasificar/', self.magia),
        ]
        return my_urls + urls


class ArticuloInline(admin.TabularInline):
    model = Articulo
    extra = 0
    autocomplete_fields = ('producto',)


class PedidoAdmin(ImportExportModelAdmin):
    list_display = ('fecha_creacion', 'codigo', 'cpm', 'estado',
                    'narticulos', 'distribuidor', 'entrega', 'centro_gasto')
    list_filter = ('estado',)
    list_display_links = ('codigo',)
    readonly_fields = ('fecha_creacion', 'fecha_cpm', 'fecha_confirmacion',
                       'fecha_cierre', 'codigo')
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

    def narticulos(self, obj):
        return obj.articulo_set.count()

    narticulos.short_description = _("nº articulos")


class ExtendidoInLine(admin.TabularInline):
    model = PerfilExtendido
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = (ExtendidoInLine,)


admin.site.register(Producto, ProductoAdmin)
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

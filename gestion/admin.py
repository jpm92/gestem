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
    PerfilExtendido,
    Borrador
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
        try:
            return obj.nota.fecha
        except AttributeError:
            return f'Objeto {obj.pk}'

    def usuario(self, obj):
        try:
            return obj.nota.usuario
        except AttributeError:
            return f'Objeto {obj.pk}'

    def magia(self, request):
        """ Este método se ejecuta al pulsar el boton en admin. Itera sobre
        todos los artículos pendientes y los autoincluye en pedidos nuevos. """

        # Obtenemos todos los articulos pendientes de clasificar.
        articulos = Articulo.objects.filter(estado='p')

        # Si no hay ningún pedido pendiente notificamos al usuario.
        if articulos.count() == 0:
            self.message_user(
                request,
                _('¡No hay articulos pendientes de procesar!')
                )
            return redirect('admin:gestion_articulo_changelist')
        # De lo contrario procedemos a la clasificación.
        else:
            distribuidor = {}
            cuenta = 0
            # En este bucle rellenamos el diccionario distribuidor de la
            # siguiente forma:
            # distribuidor[distribuidor1] = [lista de articulos distribuidos
            #                                por distribuidor 1]
            # distribuidor[distribuidor2] = [lista de articulos distribuidos
            #                                por distribuidor 2]
            # etc
            for articulo in articulos:
                dist = articulo.producto.distribuidor
                if dist not in distribuidor.keys():
                    distribuidor[dist] = [articulo]
                else:
                    distribuidor[dist].append(articulo)

            # Ahora iteramos cada distribuidor presente en el diccionario
            for d in distribuidor:
                # Diccionario en el que almacenaremos sitios de entrega y sus
                # articulos asociados (en forma de lista)
                entregas = {}
                # Iteramos cada articulo presente en la lista de articulos
                # correspondientes al distribuidor de la iteración.
                for a in distribuidor[d]:
                    entrega = a.nota.entrega
                    # Añadimos la entrega al diccionario entrega. Si ya existia
                    # la clave, el articulo se adjunta a la lista asociada a
                    # dicha clave, si no, se crea la clave y la lista
                    if entrega not in entregas.keys():
                        entregas[entrega] = [a]
                    else:
                        entregas[entrega].append(a)
                # Iteramos cada uno de los elementos del diccionario entregas.
                for e in entregas:
                    # Accedemos al primer articulo de la lista asociada a la
                    # clave de esta iteración.
                    a = entregas[e][0]
                    # Creamos un pedido con los datos del articulo (ya que
                    # todos los articulos de la lista comparten los datos).
                    p = Pedido.objects.create(
                        codigo=keygen(),
                        entrega=a.nota.entrega,
                        distribuidor=a.producto.distribuidor
                    )
                    cuenta += 1
                    # Asociamos cada uno de los articulos de la lista con el
                    # pedido recien creado.
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
    readonly_fields = ('fecha_recepcion', 'usuario_recepcion',)
    exclude = ('borrador',)


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

    def solicitar(self, queryset, request):
        """ Acción para solicitar por e-mail presupuesto para los artículos del
        pedido al proveedor asignado. """

        usuario = request.user.get_short_name()
        pedidos = []
        for pedido in queryset:
            pedidos.append(pedido)
            pedido.email(usuario)
            pedido.estado = 's'
            pedido.save()
        if len(pedidos) > 1:
            self.message_user(
                        request,
                        _('Emails enviados correctamente.'),
                        level='success'
            )
        else:
            self.message_user(
                        request,
                        _('Email enviado correctamente.'),
                        level='success'
            )
    solicitar.short_description = _("Enviar correo")


# Creamos un inline para poder modificar los campos añadidos al perfil User.
class ExtendidoInLine(admin.TabularInline):
    model = PerfilExtendido
    can_delete = False


# Añadimos el inline al modelo User de Admin
class UserAdmin(BaseUserAdmin):
    inlines = (ExtendidoInLine,)


class ArticuloBInline(admin.TabularInline):
    model = Borrador.productos.through
    extra = 0
    fields = ('producto', 'unidades')
    autocomplete_fields = ('producto',)


class BorradorAdmin(ImportExportModelAdmin):
    inlines = (ArticuloBInline,)


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
admin.site.register(Borrador, BorradorAdmin)

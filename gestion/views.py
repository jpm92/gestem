from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
from gestion.models import (
    Articulo,
    Pedido,
    Producto,
    Nota,
    Almacen
)
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin
)
from gestion.forms import (
    ArticuloForm,
    NotaForm,
    ProductoForm,
    PedidoForm,
    RecepcionForm,
    CPMForm,
)
from gestem.aux import keygen
from django.views.generic.edit import CreateView
from django.forms import formset_factory
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.views import generic
from django.contrib.auth.decorators import (
    login_required,
    permission_required
)
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash, logout
from django.core.paginator import Paginator
from django.db.models import Q


# REVIEW: Comprobar que funciona Tablon ListView
class Tablon(LoginRequiredMixin, generic.ListView):
    model = Articulo
    paginate_by = 15
    template_name = 'gestion/tablon.html'

    def get_queryset(self):
        """ Modificamos el método para obtener el queryset, de manera que
        los articulos esten filtrados por usuario. Ademas los ordenamos segun
        la fecha de la nota a la que pertenecen. """
        usuario = self.request.user
        articulos = Articulo.objects.filter(
            nota__usuario=usuario
            ).order_by(  # QUESTION: No se si se podría hacer con "ordering"
                '-nota__fecha',
                'producto__nombre_amistoso'
            ).exclude(
                borrador__isnull=False
            )
        return articulos

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet
        usuario = self.request.user
        total = Articulo.objects.filter(nota__usuario=usuario)
        estads = {
            'total': total.count(),
            'recibidos': total.filter(estado='r').count(),
            'pendientes': total.exclude(estado='r').count()
        }
        context['estads'] = estads
        return context


# REVIEW: Añadir vista para tablón Secretario
class Secretario(PermissionRequiredMixin, generic.ListView):
    permission_required = (
        'gestion.secretaria',
    )
    model = Pedido
    ordering = ['-fecha_creacion']
    paginate_by = 15
    template_name = 'gestion/secretario.html'
    # Excluimos los pedidos de centros de gasto ajenos a la UGR, ya que no
    # les interesa a la secretaría.
    queryset = Pedido.objects.exclude(centro_gasto__pertenencia_ugr=False)


# REVIEW: Añadir vista para Añadir CPM (Secretario)
@permission_required('gestion.secretaria')
def CPM(request, pk):
    """ Modifica el CPM de un pedido y actualiza su estado a
    "Para Validar". """

    instancia = get_object_or_404(Pedido, id=pk)

    if request.method == "POST":
        form = CPMForm(request.POST, instance=instancia)
        if form.is_valid():
            model_instance = form.save(commit=False)
            model_instance.estado = 'v'
            model_instance.fecha_cpm = datetime.now()
            model_instance.save(update_fields=['estado', 'fecha_cpm', 'cpm'])
            return redirect('secretaria')
    else:
        pre_data = {'cpm': instancia.cpm}
        form = CPMForm(pre_data)
        return render(
            request,
            "gestion/cpm.html",
            {'form': form, 'pedido': instancia}
        )


# REVIEW: Añadir vista para Marcar pedido como Lanzado (Secretario)
@permission_required('gestion.secretaria')
def Confirmar(request, pk):
    pedido = get_object_or_404(Pedido, id=pk)
    pedido.estado = 'p'
    pedido.fecha_confirmacion = datetime.now()
    pedido.save()
    return redirect('secretaria')


def Reclamar(request, pk):
    """ Esta vista se encarga de enviar un e-mail reclamando un articulo
    que aun no ha sido recibido. """
    # TODO: Implementar vista reclamacion

    articulo = get_object_or_404(Articulo, id=pk)
    if articulo.estado == 'p':
        pass  # Enviar e-mail a Staff

    elif articulo.estado == 'i':
        estado = articulo.pedido.estado
        if estado == 's':  # Proforma solicitada
            pass  # Enviar email a proveedor (reenviar solicitud?)
        elif estado == 'c':  # CPM Solicitado
            pass  # Enviar e-mail a Isa
        elif estado == 'v':  # Para validar
            pass  # Enviar e-mail a Juan/Isa
        elif estado == 'p':  # Confirmado
            pass  # Enviar e-mail a distribuidor con Isa en CC
    else:
        pass


def Cancelar(request, pk):
    """ Esta vista de encarga de cancelar una anotación que aún no ha sido
    tramitada. """
    anotacion = get_object_or_404(Articulo, id=pk)
    anotacion.delete()
    return redirect('tablon')


class CrearProducto(LoginRequiredMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'gestion/crear_producto.html'
    success_url = "/"


# REVIEW: Rematar lista de productos, con su búsqueda Select 2 incluida.
class ListaProductos(LoginRequiredMixin, generic.ListView):
    """ Esta vista se encarga de mostrar la lista de productos disponibles
    en la base de datos. """
    model = Producto
    ordering = ['nombre_amistoso']
    paginate_by = 15
    template_name = 'gestion/productos.html'


# REVIEW: Añadir vista para registro total de articulos
class HistorialNotas(LoginRequiredMixin, generic.ListView):
    model = Articulo
    paginate_by = 15
    template_name = 'gestion/notas.html'
    # FIXME: Corregir orden listado
    def get_queryset(self):
        return Articulo.objects.order_by(
            'nota__fecha'
            ).exclude(
            borrador__isnull=False
            )


# REVIEW: Rematar ListaPedidos
class HistorialPedidos(LoginRequiredMixin, generic.ListView):
    model = Pedido
    ordering = ['-fecha_creacion']
    paginate_by = 15
    template_name = 'gestion/pedidos.html'


# REVIEW: Implementar vista en detalle para productos.
class DetalleProducto(generic.DetailView):

    model = Producto
    template_name = "gestion/detalle_producto.html"


# REVIEW: Implementar vista en detalle para Nota.
class DetalleNota(generic.DetailView):

    model = Nota
    template_name = "gestion/detalle_nota.html"


# REVIEW: Implementar vista en detalle para Artículo.
class ArticuloDetalle(generic.DetailView):

    model = Articulo
    template_name = "gestion/detalle_articulo.html"


# REVIEW: Implementar vista en detalle de Pedido.
class PedidoDetalle(generic.DetailView):

    model = Pedido
    template_name = "gestion/detalle_pedido.html"


def BusquedaArticulo(request):
    """ Esta vista se encarga de buscar los articulos introducidos en
    la barra de búsqueda. """

    b = request.GET.get('q')

    queryset = Articulo.objects.exclude(
        estado='r'
    ).filter(
        Q(producto__nombre_amistoso__icontains=b) |
        Q(producto__nombre_fabricante__icontains=b) |
        Q(producto__referencia__icontains=b)
    ).distinct(
    ).order_by(
        '-nota__fecha'
    ).exclude(
        borrador__isnull=False
    )

    paginacion = Paginator(queryset, 15)
    pagina = request.GET.get('page')
    resultado = paginacion.get_page(pagina)
    # REVIEW: Crear plantilla para resultados_articulos
    return render(
        request,
        "gestion/r_articulos.html",
        {'resultados': resultado}
    )


def BusquedaPedido(request):
    """ Esta vista se encarga de buscar los pedidos introducidos en
    la barra de búsqueda. """

    b = request.GET.get('q')

    queryset = Pedido.objects.filter(
        Q(codigo__icontains=b) |
        Q(cpm__icontains=b) |
        Q(distribuidor__nombre__icontains=b)
    ).order_by('-fecha_creacion')

    paginacion = Paginator(queryset, 15)
    pagina = request.GET.get('page')
    resultado = paginacion.get_page(pagina)
    # Crear plantilla para resultados_pedidos
    return render(
        request,
        "gestion/pedidos.html",
        {'pedido_list': resultado}
    )


def BusquedaProducto(request):
    """ Esta vista se encarga de buscar los productos introducidos en
    la barra de búsqueda. """

    b = request.GET.get('q')

    queryset = Producto.objects.filter(
        Q(nombre_amistoso__icontains=b) |
        Q(nombre_amistoso__icontains=b) |
        Q(referencia__icontains=b)
    ).order_by('nombre_amistoso')

    paginacion = Paginator(queryset, 15)
    pagina = request.GET.get('page')
    resultado = paginacion.get_page(pagina)
    # REVIEW: Crear plantilla para resultados_productos
    return render(
        request,
        "gestion/productos.html",
        {'producto_list': resultado}
    )


# NOTE: Desactivada hasta nuevo aviso, mejor ir a lo seguro
# def Busqueda(request):
#     """ Esta vista se encarga de buscar los parámetros introducidos en
#     la barra de búsqueda. """
#
#     path = request.META['HTTP_REFERER']
#
#     b = request.GET.get('q')
#
#     if 'articulo' in path or 'tablon' in path or 'historial' in path:
#         # Búsqueda de artículos
#         queryset = Articulo.objects.exclude(
#             estado='r'
#         ).filter(
#             Q(producto__nombre_amistoso__icontains=b) |
#             Q(producto__nombre_fabricante__icontains=b) |
#             Q(producto__referencia__icontains=b)
#         ).distinct(
#         ).order_by('-nota__fecha')
#
#         paginacion = Paginator(queryset, 15)
#         pagina = request.GET.get('page')
#         resultado = paginacion.get_page(pagina)
#         # REVIEW: Crear plantilla para resultados_articulos
#         return render(
#             request,
#             "gestion/r_articulos.html",
#             {'resultados': resultado}
#         )
#
#     if 'producto' in path:
#         # Búsqueda de productos
#         queryset = Producto.objects.filter(
#             Q(nombre_amistoso__icontains=b) |
#             Q(nombre_amistoso__icontains=b) |
#             Q(referencia__icontains=b)
#         ).order_by('nombre_amistoso')
#
#         paginacion = Paginator(queryset, 15)
#         pagina = request.GET.get('page')
#         resultado = paginacion.get_page(pagina)
#         # REVIEW: Crear plantilla para resultados_productos
#         return render(
#             request,
#             "gestion/productos.html",
#             {'producto_list': resultado}
#         )
#
#     if 'pedido' in path:
#         # Búsqueda de Pedidos
#         queryset = Pedido.objects.filter(
#             Q(codigo__icontains=b) |
#             Q(cpm__icontains=b) |
#             Q(distribuidor__nombre__icontains=b)
#         ).order_by('-fecha_creacion')
#
#         paginacion = Paginator(queryset, 15)
#         pagina = request.GET.get('page')
#         resultado = paginacion.get_page(pagina)
#         # Crear plantilla para resultados_pedidos
#         return render(
#             request,
#             "gestion/pedidos.html",
#             {'pedido_list': resultado}
#         )


# REVIEW: Comprobar que funciona la vista para formulario de Notas
@login_required
def NuevaNota(request):
    # Creamos un formset a partir del formulario de Articulo.
    ArticuloFormset = formset_factory(ArticuloForm)
    if request.method == "POST":
        # Instanciamos un objeto de la clase ArticuloFormset y lo populamos con
        # los datos del post request
        articulos_formset = ArticuloFormset(request.POST)
        # Instanciamos un objeto de la clase EntregaForm y lo populamos con
        # los datos del post request
        nota_form = NotaForm(request.POST)
        # Si los formularios han sido rellenados correctamente:
        if articulos_formset.is_valid() and nota_form.is_valid():
            # Guardamos el objeto formulario sin anotarlo en la base de datos.
            nota = nota_form.save(commit=False)
            # Añadimos el usuario al objeto formulario.
            nota.usuario = request.user
            # Escribimos los datos del objeto formulario en la base de datos.
            nota.save()
            # Ahora iteramos cada uno de los articulos presentes en el
            # formset y los registramos en la base de datos, asignandole a cada
            # uno la nota anterior (que posee informacion común a todos los
            # articulos).
            for articulo_form in articulos_formset:
                if articulo_form.cleaned_data != {}:
                    articulo = articulo_form.save(commit=False)
                    articulo.nota = nota
                    articulo.save()
                # messages.success(
                #     request,
                #     _(f'Nota nº{nota.pk} añadida con éxito.'),
                #     extra_tags='alert alert-success'
                # )
            return redirect('/')

    else:
        articulos = ArticuloFormset()
        nota = NotaForm()
        context = {
            'articulos': articulos,
            'nota': nota
        }
        return render(request, "gestion/anotar.html", context)


# REVIEW: Añadir formulario para registro de Notas en modo autogestión
def AutoGestion(request):
    # Creamos un formset a partir del formulario de Articulo.
    ArticuloFormset = formset_factory(ArticuloForm)
    if request.method == "POST":
        # Instanciamos un objeto de la clase ArticuloFormset y lo populamos con
        # los datos del post request
        articulos_formset = ArticuloFormset(request.POST)
        # Instanciamos un objeto de la clase PedidoForm y lo populamos con
        # los datos del post request
        pedido_form = PedidoForm(request.POST)
        # Si los formularios han sido rellenados correctamente:
        if articulos_formset.is_valid() and pedido_form.is_valid():
            # Guardamos el objeto formulario sin anotarlo en la base de datos.
            pedido = pedido_form.save(commit=False)
            # Añadimos el usuario al objeto formulario.
            pedido.usuario = request.user
            pedido.codigo = keygen()
            pedido.estado = 'g'
            # Escribimos los datos del objeto formulario en la base de datos.
            pedido.save()
            # Creamos un objeto Nota para relacionarla con los articulos.
            nota = Nota.objects.create(
                usuario=request.user,
                entrega=pedido.entrega
            )
            # Ahora iteramos cada uno de los articulos presentes en el
            # formset y los registramos en la base de datos, asignandole a cada
            # uno el pedido anterior (que posee informacion común a todos los
            # articulos), así como la nota anterior.
            for articulo_form in articulos_formset:
                if articulo_form.cleaned_data != {}:
                    articulo = articulo_form.save(commit=False)
                    articulo.pedido = pedido
                    articulo.nota = nota
                    articulo.estado = 'i'
                    articulo.save()
                messages.success(
                    request,
                    _(f'Pedido nº{pedido.codigo} añadido con éxito.'),
                    extra_tags='alert alert-success'
                )
            return redirect('/')

    else:
        articulos = ArticuloFormset()
        pedido = PedidoForm()
        context = {
            'articulos': articulos,
            'pedido': pedido,
        }
        return render(request, "gestion/autogestion.html", context)


def Recepcion(request, pk):

    instance = get_object_or_404(Articulo, id=pk)
    if request.method == "POST":
        form = RecepcionForm(request.POST, instance=instance)
        if form.is_valid():
            model_instance = form.save(commit=False)
            model_instance.usuario_recepcion = request.user
            model_instance.estado = 'r'
            model_instance.fecha_recepcion = datetime.now()
            model_instance.save(
                update_fields=[
                    'usuario_recepcion',
                    'almacen',
                    'fecha_recepcion',
                    'estado',
                ]
            )
            model_instance.pedido.concluir()
            return redirect('/')
    else:
        form = RecepcionForm()
        form.fields["almacen"].queryset = Almacen.objects.filter(
            lugar=instance.pedido.entrega
        )
        return render(
            request,
            "gestion/recepcion.html",
            {'form': form}
        )


def cambio_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(
                request,
                _('Su contraseña ha sido actualizada correctamente.'),
                extra_tags='alert alert-success'
            )
            return redirect('index')
        else:
            messages.error(
                request,
                _('Por favor corrija el error indicado debajo.'),
                extra_tags='alert alert-warning'
            )
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/cambiar_password.html', {
        'form': form
    })


def salir(request):
    """ Desconecta al usuario y reenvia a página de despedida. """
    logout(request)
    return render(request, 'gestion/logout.html')

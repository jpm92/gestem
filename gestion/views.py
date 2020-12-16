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
    #  PermissionRequiredMixin
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
    #  permission_required
)
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

# Create your views here.


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
class Secretario(LoginRequiredMixin, generic.ListView):
    model = Pedido
    ordering = ['-fecha_creacion']
    paginate_by = 15
    template_name = 'gestion/secretario.html'
    # Excluimos los pedidos de centros de gasto ajenos a la UGR, ya que no
    # les interesa a la secretaría.
    queryset = Pedido.objects.exclude(centro_gasto__pertenencia_ugr=False)


# REVIEW: Añadir vista para Añadir CPM (Secretario)
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
def Confirmar(request, pk):
    pedido = get_object_or_404(Pedido, id=pk)
    pedido.estado = 'p'
    pedido.fecha_confirmacion = datetime.now()
    pedido.save()
    return redirect('secretaria')


def Reclamar(request):
    """ Esta vista se encarga de enviar un e-mail reclamando un articulo
    que aun no ha sido recibido. """
    # TODO: Implementar vista reclamacion
    pass


class CrearProducto(LoginRequiredMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'gestion/producto.html'
    success_url = "/"


# TODO: Rematar lista de productos, con su búsqueda Select 2 incluida.
class ListaProductos(LoginRequiredMixin, generic.ListView):
    """ Esta vista se encarga de mostrar la lista de productos disponibles
    en la base de datos. """
    model = Producto
    ordering = ['-nombre_amistoso']
    paginate_by = 15
    template_name = 'gestion/productos.html'


# TODO: Añadir vista para registro total de articulos
class HistorialNotas(LoginRequiredMixin, generic.ListView):
    model = Articulo
    ordering = ['-fecha_creacion']
    paginate_by = 15
    template_name = 'gestion/notas.html'


# TODO: Rematar ListaPedidos
class HistorialPedidos(LoginRequiredMixin, generic.ListView):
    model = Pedido
    ordering = ['-fecha_creacion']
    paginate_by = 15
    template_name = 'gestion/pedidos.html'


# TODO: Implementar vista en detalle para productos.
class DetalleProducto(generic.DetailView):
    pass


# TODO: Implementar vista en detalle para Nota.
class DetalleNota(generic.DetailView):
    pass


# TODO: Implementar vista en detalle para Artículo.
class ArticuloDetalle(generic.DetailView):
    pass


# TODO: Implementar vista en detalle de Pedido.
class PedidoDetalle(generic.DetailView):
    pass


def Busqueda(request):
    """ Esta vista se encarga de buscar los parámetros introducidos en
    la barra de búsqueda. """
    # TODO: Implementar búsqueda según el path donde se ejecute:
    # if request.path == /pedido/ or /articulo/ etc.
    pass


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

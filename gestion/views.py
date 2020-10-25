from django.shortcuts import render, redirect
from gestion.models import (
    Articulo,
    Pedido,
    Nota
)
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin
)
from gestion.forms import (
    ArticuloForm,
    EntregaForm
)
from django.forms import formset_factory
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.views import generic
from django.contrib.auth.decorators import login_required, permission_required

# Create your views here.


# REVIEW: Comprobar que funciona Tablon ListView
class Tablon(LoginRequiredMixin, generic.ListView):
    model = Articulo
    ordering = ['-fecha']
    paginate_by = 15
    template_name = 'gestion/tablon.html'

    def get_queryset(self):
        usuario = self.request.user
        articulos = Articulo.objects.filter(nota__usuario=usuario)
        return articulos


# TODO: Añadir vista para tablón Secretario
class Secretario(LoginRequiredMixin, generic.ListView):
    model = Pedido
    ordering = ['-fecha']
    paginate_by = 15
    template_name = 'gestion/secretario.html'


# TODO: Añadir vista para Añadir CPM (Secretario)
# TODO: Añadir vista para Marcar pedido como Lanzado (Secretario)
# TODO: Añadir vista para recepcionar pedido
# TODO: Añadir vista para formulario de Productos
# TODO: Añadir vista para registro total
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
        entrega_form = EntregaForm(request.POST)
        # Si los formularios han sido rellenados correctamente:
        if articulos_formset.is_valid() and entrega_form.is_valid():
            # Recopilamos los datos de entrega a partir de los datos limpios
            # del formulario.
            entrega = entrega_form.cleaned_data['direccion']
            # Creamos una nota con los datos que recopilados de entrega, y el
            # usuario (recopilado a partir del request). La fecha se añade sola
            # gracias al "auto_now_add" del campo del modelo Nota.
            nota = Nota(
                entrega=entrega,
                usuario=request.user
            )
            nota.save()
            # TODO: Ahora iteramos cada uno de los articulos presentes en el
            # formset y los registramos en la base de datos, asignandole a cada
            # uno la nota anterior (que posee informacion común a todos los
            # articulos).
            for articulo_form in articulos_formset:
                articulo_data = articulo_form.cleaned_data
                producto = articulo_data['producto']
                unidades = articulo_data['unidades']
                articulo = Articulo(
                    producto=producto,
                    unidades=unidades,
                    nota=nota
                )
                articulo.save()
            messages.success(
                request,
                _(f'Nota nº{nota.pk} añadida con éxito.'),
                extra_tags='alert alert-success'
            )
            return redirect('/')

    else:
        articulos = ArticuloFormset()
        entrega = EntregaForm()
        context = {
            'articulos': articulos,
            'entrega': entrega
        }
        return render(request, "gestion/nuevanota.html", context)
# TODO: Añadir formulario para registro de Notas en modo autogestión

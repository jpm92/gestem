from django.shortcuts import render, redirect
from gestion.models import (
    Articulo,
    Pedido,
)
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    #  PermissionRequiredMixin
)
from gestion.forms import (
    ArticuloForm,
    NotaForm,
)
from django.forms import formset_factory
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.views import generic
from django.contrib.auth.decorators import login_required, permission_required

# Create your views here.


# REVIEW: Comprobar que funciona Tablon ListView
class Tablon(generic.ListView):
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
                articulo = articulo_form.save(commit=False)
                articulo.nota = nota
                articulo.save()
            messages.success(
                request,
                _(f'Nota nº{nota.pk} añadida con éxito.'),
                extra_tags='alert alert-success'
            )
            return redirect('/')

    else:
        articulos = ArticuloFormset()
        nota = NotaForm()
        context = {
            'articulos': articulos,
            'nota': nota
        }
        return render(request, "gestion/nuevanota.html", context)
# TODO: Añadir formulario para registro de Notas en modo autogestión

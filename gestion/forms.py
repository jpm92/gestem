""" Este modulo contiene los formularios necesarios en la app gestion. """
from django import forms
from .models import Articulo, Nota
from django_select2 import forms as s2forms


class ProductoWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "nombre_amistoso__icontains",
        "nombre_fabricante__icontains",
        "referencia__icontains"
    ]


class ArticuloForm(forms.ModelForm):
    """ Este formulario se utiliza para agregar articulos a la pizarra. """

    class Meta:
        model = Articulo
        fields = ['producto', 'unidades']
        widgets = {
            "producto": ProductoWidget,
        }


class NotaForm(forms.ModelForm):
    """ Este formulario se utiliza para crear una nota a la que enlazar
    articulos al rellenar el formulario de anotación de articulos. """

    class Meta:
        model = Nota
        fields = ['entrega']
    # direccion = forms.ForeignKey blablabla -> modelo Entrega
# TODO: Formulario para nuevo Producto
# TODO: Formulario para articulos (Pedido) en modo autogestion
# TODO: Formulario para asignar CPM
# TODO: Formulario para Marcar Pedido Realizado

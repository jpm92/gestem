""" Este modulo contiene los formularios necesarios en la app gestion. """
from django import forms
from .models import Articulo, Nota, Producto, Pedido
from django_select2 import forms as s2forms
from django.utils.translation import ugettext_lazy as _


class ProductoWidget(s2forms.ModelSelect2Widget):
    """ Widget especial creado con libreria django-select2.
    Busca según los campos especificados en serach_fields. """

    search_fields = [
        "nombre_amistoso__icontains",
        "nombre_fabricante__icontains",
        "referencia__icontains",
    ]


class ArticuloForm(forms.ModelForm):
    """ Este formulario se utiliza para agregar articulos a la pizarra. """

    class Meta:
        model = Articulo
        fields = ['producto', 'unidades']
        widgets = {
            "producto": ProductoWidget(
                {'data-language': 'es',
                 'data-placeholder': 'Busque productos',
                 'data-width': '100%',
                 }
            ),
        }


class NotaForm(forms.ModelForm):
    """ Este formulario se utiliza para crear una nota a la que enlazar
    articulos al rellenar el formulario de anotación de articulos. """

    class Meta:
        model = Nota
        fields = ['entrega']
    # direccion = forms.ForeignKey blablabla -> modelo Entrega


class PedidoForm(forms.ModelForm):
    """ Este formulario se utiliza para crear un pedido directamente con
    los articulos introducidos por el usuario. """

    class Meta:
        model = Pedido
        fields = ['entrega', 'distribuidor']


# TODO: Formulario para nuevo Producto
class ProductoForm(forms.ModelForm):
    """ Formulario para añadir productos a la base de datos. """
    def __init__(self, *args, **kwargs):
        super(ProductoForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs = {
                'class': 'form-control'
            }

    class Meta:
        model = Producto
        fields = "__all__"


class RecepcionForm(forms.ModelForm):
    """ Este formulario se utiliza para recepcionar articulos recibidos. """

    class Meta:
        model = Articulo
        fields = ['almacen']


# TODO: Formulario para asignar CPM
class CPMForm(forms.ModelForm):

    cpm = forms.CharField(
        required=True, max_length=20,
        help_text=_('Introduzca el código del CPM asignado a este pedido.'),
        label=_('Código CPM')
        )

    class Meta:
        model = Pedido
        fields = ['cpm']

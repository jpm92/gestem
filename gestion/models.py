from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class Producto(models.Model):
    """ Este modelo representa a cada uno de los productos disponibles
    para hacer un pedido en la aplicación. """

    nombre_amistoso = models.CharField(
        max_length=40,
        help_text=_('Nombre amigable del producto.')
    )
    nombre_fabricante = models.CharField(
        max_length=60,
        help_text=_(
            'Nombre real del producto, tal como lo conoce el fabricante.'
        )
    )
    fabricante = models.ForeignKey(
        'Fabricante',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    referencia = models.CharField(
        max_length=25,
        help_text=_('Referencia del fabricante.')
    )
    distribuidor = models.ForeignKey(
        'Distribuidor',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    distribuidores = None  # QUESTION: ¿Es necesario un m2m o ignoro?
    CATEGORIAS = {
        'a': _('Cultivo celular'),
        'b': _('Kits viabilidad'),
        'c': _('Esferas'),
        'd': _('Western Blot'),
        'e': _('PCR'),
        'f': _('Tinciones.'),
        'g': _('Impresión 3D.'),
        'h': _('Fungible.')
    }
    categoria = models.CharField(
        max_length=1,
        choices=CATEGORIAS,
        help_text=_('Categoría del producto.')
    )


class Fabricante(models.Model):
    """ Este modelo representa al fabricante de cada uno de los productos del
    modelo Producto. """

    nombre = models.CharField(
        max_length=40,
        help_text=_('Nombre del fabricante.')
    )
    web = models.CharField(
        max_length=25,
        help_text=_('Página web del fabricante.'),
        blank=True
    )


class Distribuidor(models.Model):
    """ Cada producto puede ser adquirido a través de uno o más distribuidores.
    Este modelo representa a dichos distribuidores. """

    nombre = models.CharField(
        max_length=40,
        help_text=_('Nombre del distribuidor.')
    )
    comercial = models.CharField(
        max_length=25,
        help_text=_('Nombre del comercial de confianza.'),
        blank=True
    )
    contacto = models.EmailField(
        max_length=40,
        help_text=_('e-mail de contacto.')
    )


class Almacen(models.Model):
    """ Este modelo representa cada una de las localizaciones posibles donde
    recepcionar un producto. Están asociados a la dirección de entrega
    (class Entrega). Así, cada dirección de entrega poseerá distintas
    localizaciones (Frigorífico 1, Mueble 3, etc.) donde guardar el producto
    una vez recepcionado. """

    nombre = models.CharField(
        max_length=30,
        help_text=_('Nombre del lugar de almacenaje.')
    )
    descripcion = models.TextField(
        help_text=_('Descripción del almacén.')
    )
    lugar = models.ForeignKey(
        'Entrega',
        on_delete=models.SET_NULL,
        null=True
    )


class Entrega(models.Model):
    """ Este modelo representa las posibles direcciones a las que puede ser
    enviado un pedido (p. ej. distintos laboratorios). El campo "direccion"
    será el que se muestre a los distribuidores a la hora de realizar el
    pedido. """

    nombre = models.CharField(
        max_length=30,
        help_text=_('Nombre indentificativo de la dirección de entrega.')
    )
    direccion = models.TextField(
        help_text=_('Dirección completa con instrucciones de entrega.')
    )


class Articulo(models.Model):
    """ Este modelo representa la instancia de un producto anotado por un
    usuario y que se encuentra pendiente de ser incluido en un pedido, junto al
    numero de unidades, fecha y usuario. """

    producto = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        null=True
    )
    unidades = models.IntegerField(
        default=1
    )
    ESTADOS = {
        'p': _('Pendiente.'),
        'i': _('En proceso.'),
        'r': _('Recibido.')
    }
    estado = models.CharField(
        max_length=1,
        choices=ESTADOS,
        default='p',
        help_text=_('Estado de este articulo.')
    )
    fecha_recepcion = models.DateTimeField(
        auto_now_add=True,
        help_text=_('Fecha de recepción de este articulo.')
    )
    nota = models.ForeignKey(
        'Nota',
        on_delete=models.SET_NULL,
        null=True
    )


class Pedido(models.Model):
    """ Este modelo representa un pedido en firme a un distribuidor. Los
    articulos (class Articulo) tienen una relacion ManyToOne con este modelo de
    forma que se pueda acceder a los articulos de cada pedido mediante
    'Pedido.articulo_set.all()'. """

    codigo = models.CharField(
        max_length=15,
        help_text=_('Código único identificativo del pedido.')
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        help_text=_('Fecha de creación del pedido.')
    )
    fecha_cpm = models.DateTimeField(
        help_text=_('Fecha de asignación de CPM.')
    )
    ESTADOS = {
        's': _('Proforma solicitada.'),
        'c': _('CPM solicitado.'),
        'v': _('Para validar.'),
        'p': _('Pedido realizado.'),  # TODO: Comentar a Isabel.
        'r': _('Recibido.')
    }
    estado = models.CharField(
        max_length=1,
        choices=ESTADOS
    )
    distribuidor = models.ForeignKey(
        Distribuidor,
        on_delete=models.SET_NULL,
        null=True
    )
    entrega = models.ForeignKey(
        Entrega,
        on_delete=models.SET_NULL,
        null=True
    )


class Nota(models.Model):
    """ Este modelo representa un conjunto de artículos anotados
    simultáneamente en la pizarra. Recopila todos los datos compartidos entre
    todos los artículos que han sido añadidos simultáneamente:
        - fecha de anotación
        - usuario que lo ha anotado
        - dirección a la que entregar estos articulos.
    """

    fecha = models.DateTimeField(
        auto_now_add=True,
        help_text=_('Fecha de creación de la nota.')
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    entrega = models.ForeignKey(
        Entrega,
        on_delete=models.SET_NULL,
        null=True
    )

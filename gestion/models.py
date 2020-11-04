from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class Producto(models.Model):
    """ Este modelo representa a cada uno de los productos disponibles
    para hacer un pedido en la aplicación. """

    nombre_amistoso = models.CharField(
        max_length=40,
        help_text=_('Nombre corto para identificarlo facilmente.'),
        verbose_name=_('Pseudónimo')
    )
    nombre_fabricante = models.CharField(
        max_length=60,
        help_text=_(
            'Nombre que le da al producto el fabricante.'
        ),
        verbose_name=_('Nombre real')
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
        null=True,
        help_text=_('Empresa que suministra este producto.')
    )
    distribuidores = None  # QUESTION: ¿Es necesario un m2m o ignoro?
    CATEGORIAS = [
        ('a', _('Cultivo celular')),
        ('b', _('Kits viabilidad')),
        ('c', _('Esferas')),
        ('d', _('Western Blot')),
        ('e', _('PCR')),
        ('f', _('Tinciones.')),
        ('g', _('Impresión 3D.')),
        ('h', _('Fungible.'))
    ]
    categoria = models.CharField(
        max_length=1,
        choices=CATEGORIAS,
        help_text=_('Categoría del producto.'),
        blank=True
    )

    # Metadata
    class Meta:
        verbose_name = _("Producto")
        verbose_name_plural = _("Productos")

    def __str__(self):
        return f'{self.nombre_amistoso} ({self.referencia})'


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

    class Meta:
        verbose_name = _("Fabricante")
        verbose_name_plural = _("Fabricantes")

    def __str__(self):
        return f'{self.nombre}'


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

    class Meta:
        verbose_name = _("Distribuidor")
        verbose_name_plural = _("Distribuidores")

    def __str__(self):
        return f'{self.nombre}'


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
        help_text=_('Descripción del almacén.'),
        blank=True
    )
    lugar = models.ForeignKey(
        'Entrega',
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        verbose_name = _("Almacén")
        verbose_name_plural = _("Almacenes")

    def __str__(self):
        return f'{self.nombre}'


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

    class Meta:
        verbose_name = _("Dirección de entrega")
        verbose_name_plural = _("Direcciones de entrega")

    def __str__(self):
        return f'{self.nombre}'


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
    ESTADOS = [
        ('p', _('Pendiente.')),
        ('i', _('En proceso.')),
        ('r', _('Recibido.'))
    ]
    estado = models.CharField(
        max_length=1,
        choices=ESTADOS,
        default='p',
        help_text=_('Estado de este articulo.')
    )
    fecha_recepcion = models.DateTimeField(
        help_text=_('Fecha de recepción de este articulo.'),
        blank=True,
        null=True
    )
    nota = models.ForeignKey(
        'Nota',
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        verbose_name = _("Artículo")
        verbose_name_plural = _("Artículos")

    def __str__(self):
        producto = self.producto.nombre_amistoso
        unidades = self.unidades
        if unidades > 1:
            return f'{producto} ({unidades}uds)'
        else:
            return f'{producto} ({unidades}ud)'


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
    cpm = models.CharField(
        max_length=13,
        default=_('Pendiente.'),
        blank=True
    )
    fecha_cpm = models.DateTimeField(
        help_text=_('Fecha de asignación de CPM.'),
        blank=True
    )
    ESTADOS = [
        ('s', _('Proforma solicitada.')),
        ('c', _('CPM solicitado.')),
        ('v', _('Para validar.')),
        ('p', _('Pedido realizado.')),  # TODO: Comentar a Isabel.
        ('r', _('Recibido.'))
    ]
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
    centro_gasto = models.ForeignKey(
        'CentroGasto',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _("Pedido")
        verbose_name_plural = _("Pedidos")

    def __str__(self):
        return f'{self.codigo}'


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

    class Meta:
        verbose_name = _("Nota")
        verbose_name_plural = _("Notas")

    def __str__(self):
        return f'Nota nº{self.pk}'


class CentroGasto(models.Model):
    """ Este modelo representa a un centro de gasto al cual cargar el
    importe de un pedido. Los administradores lo asignan al crear el pedido."""

    nombre = models.CharField(
        max_length=25,
        help_text=_('Nombre del centro de gasto.')
    )
    codigo = models.CharField(
        max_length=50,
        help_text=_('Codigo del centro de gasto dentro de la UGR.')
    )
    pertenencia_ugr = models.BooleanField(
        blank=True,
        help_text=_('¿Centro de gasto de la UGR? (Si/No)')
    )

    class Meta:
        verbose_name = _("Centro de gasto")
        verbose_name_plural = _("Centros de gasto")

    def __str__(self):
        return f'{self.nombre}'

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from datetime import datetime, time
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from gestion.tasks import solicitud_email
from gestem.aux import keygen
from django.utils import timezone


def get_name(self):
    """
    Esta función modifica el __str__ del modelo de Usuario de django,
    permitiendo representar a los usuarios de manera personalizada
    """
    if self.first_name:
        nombre = f'{self.first_name}'
        nombre = nombre.replace(" ", "")
        if self.last_name:
            nombre = f'{nombre} '
            for x in self.last_name.split():
                nombre = f'{nombre}{x[0]}'
        return f'{nombre}'
    else:
        return self.username


User.add_to_class("__str__", get_name)


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
            'Nombre largo que le da el fabricante al producto.'
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
    formato = models.CharField(
        max_length=25,
        help_text=_('Formato del producto (ej. c/50, b/100, etc.)'),
        blank=True
    )
    distribuidor = models.ForeignKey(
        'Distribuidor',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_('Empresa que suministra este producto.')
    )
    # distribuidores = None  IDEA: ¿Es necesario? Ignorar por ahora.
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
        return f'{self.nombre_amistoso} ({self.fabricante}: {self.referencia})'

    def en_curso(self):
        """ Este método comprueba si hay algun artículo relacionado con la
        instancia del producto cuya solicitud esta en curso. """

        articulos = self.articulo_set.all().exclude(estado='r')

        return articulos

    def sumario(self):
        """ Este método devuelve la información más basica del producto en
        forma de cadena. """

        cadena = f'{self.nombre_amistoso}, {self.fabricante}\
         ({self.referencia})'

        return cadena


class Fabricante(models.Model):
    """ Este modelo representa al fabricante de cada uno de los productos del
    modelo Producto. """

    nombre = models.CharField(
        max_length=40,
        help_text=_('Nombre del fabricante.')
    )
    web = models.CharField(
        max_length=60,
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
        return f'{self.nombre} ({self.lugar})'


class Entrega(models.Model):
    """ Este modelo representa las posibles direcciones a las que puede ser
    enviado un pedido (p. ej. distintos laboratorios). El campo "direccion"
    será el que se muestre a los distribuidores a la hora de realizar el
    pedido. """

    nombre = models.CharField(
        max_length=30,
        help_text=_(
            'Nombre interno indentificativo de la dirección de entrega.'
        )
    )
    centro = models.CharField(
        max_length=50,
        help_text=_('Nombre del centro de investigación.'),
        null=True
    )
    laboratorio = models.CharField(
        max_length=40,
        help_text=_('Laboratorio, departamento, secretaría, etc.'),
        null=True
    )
    aa = models.CharField(
        max_length=40,
        help_text=_('A la atencion de.'),
        null=True
    )
    direccion = models.TextField(
        help_text=_('Dirección completa.'),
        null=True
    )
    cp = models.CharField(
        max_length=5,
        help_text=_('Código postal.'),
        null=True
    )
    poblacion = models.CharField(
        max_length=40,
        help_text=_('Población del código postal.'),
        null=True
    )
    instrucciones = models.TextField(
        help_text=_('Instrucciones de entrega.'),
        blank=True,
        null=True
    )
    contacto = models.CharField(
        max_length=40,
        blank=True,
        help_text=_('Datos de contacto.')
    )
    horario = models.CharField(
        max_length=40,
        blank=True,
        help_text=_('Horario para entregar paquetes (mañanas, tardes, etc).')
    )

    class Meta:
        verbose_name = _("Dirección de entrega")
        verbose_name_plural = _("Direcciones de entrega")

    def __str__(self):
        return f'{self.nombre}'

    def resumen(self):
        """ Este método devuelve una cadena con toda la información del
        sitio de entrega resumida. """

        dir = f'{self.centro}; {self.laboratorio}, Aa {self.aa};\
                {self.direccion}; {self.cp} {self.poblacion}; ESPAÑA'
        if self.instrucciones:
            dir += f'; {self.instrucciones}'
        if self.contacto:
            dir += f';Contacto: {self.contacto}'
        if self.horario:
            dir += f';Horario: {self.horario}'
        return dir

    def html(self):
        """ Este método devuelve una cadena en formato html con toda la
        información del lugar de entrega lista para incluirla en una plantilla.
        """

        html = f'<b>{self.centro}</b><br>{self.laboratorio}<br>{self.aa}<br>\
                {self.direccion}<br>{self.cp} {self.poblacion}<br>ESPAÑA'
        if self.instrucciones:
            html += f'<br>{self.instrucciones}'
        if self.contacto:
            html += f'<br><b>Contacto:</b> {self.contacto}'
        if self.horario:
            html += f'<br><b>Horario:</b> {self.horario}'
        return html

    def resumen_secretaria(self):
        """ Este método devuelve una cadena con toda la información del
        sitio de entrega resumida preparada para ser copiada con
        un click por la secretaria. """

        dir = f'{self.centro};\n{self.laboratorio}, Aa {self.aa}\n'
        dir += f'{self.direccion}\n{self.cp} {self.poblacion}\nESPAÑA'
        if self.instrucciones:
            dir += f'\n{self.instrucciones}'
        if self.contacto:
            dir += f'\nContacto: {self.contacto}'
        if self.horario:
            dir += f'\nHorario: {self.horario}'
        return dir


class Articulo(models.Model):
    """ Este modelo representa la instancia de un producto anotado por un
    usuario y que se encuentra pendiente de ser incluido en un pedido, junto al
    numero de unidades, fecha y usuario. """

    producto = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        null=True
    )
    borrador = models.ForeignKey(
        'Borrador',
        on_delete=models.SET_NULL,
        related_name='articulos',
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
    pedido = models.ForeignKey(
        'Pedido',
        on_delete=models.SET_NULL,
        related_name='productos',
        null=True,
        blank=True
    )
    nota = models.ForeignKey(
        'Nota',
        related_name='articulos',
        on_delete=models.SET_NULL,
        null=True
    )
    fecha_recepcion = models.DateTimeField(
        help_text=_('Fecha de recepción de este articulo.'),
        blank=True,
        null=True
    )
    usuario_recepcion = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    almacen = models.ForeignKey(
        Almacen,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _("Artículo")
        verbose_name_plural = _("Artículos")

    def __str__(self):
        try:
            producto = self.producto.nombre_amistoso
            unidades = self.unidades
            if unidades > 1:
                return f'{producto} ({unidades}uds)'
            else:
                return f'{producto} ({unidades}ud)'
        except AttributeError:
            return str(self.pk)

    def atrasado(self):  # REVIEW: Revisar que funciona (no se da el caso)
        """ Método para marcar un articulo como "con retraso" para
        asi notificar al usuario en su tablón que o bien lo recepcione o bien
        lo reclame. """

        if self.estado != 'r':
            tiempo = timezone.now() - self.nota.fecha
            if tiempo.days >= 30:
                return True
            else:
                return False
        else:
            pass

    def sumario(self):
        """ Método que devuelve una cadena de texto con la información mas
        relevante del objeto (útil para usar en plantilla detalle_pedido). """

        fecha_bruta = timezone.localtime(self.nota.fecha)
        fecha = fecha_bruta.strftime('%d/%m/%Y %H:%M:%S')

        cadena = f'{self.producto} [{self.unidades} uds.] \
        (por {self.nota.usuario} el {fecha}).'

        return cadena


class Pedido(models.Model):
    """ Este modelo representa un pedido en firme a un distribuidor. Los
    articulos (class Articulo) tienen una relacion ManyToOne con este modelo de
    forma que se pueda acceder a los articulos de cada pedido mediante
    'Pedido.productos.all()'. """

    codigo = models.CharField(
        max_length=15,
        help_text=_('Código único identificativo del pedido.')
    )
    cpm = models.CharField(
        max_length=13,
        default=_('Pendiente.'),
        blank=True,
        verbose_name=_('CPM')
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        help_text=_('Fecha de creación del pedido.'),
        null=True
    )
    fecha_cpm = models.DateTimeField(
        help_text=_('Fecha de asignación de CPM.'),
        blank=True,
        null=True,
        verbose_name=_('Fecha CPM')
    )
    fecha_confirmacion = models.DateTimeField(
        help_text=_('Fecha de lanzamiento de pedido.'),
        blank=True,
        null=True
    )
    fecha_cierre = models.DateTimeField(
        help_text=_('Fecha de finalización del pedido.'),
        blank=True,
        null=True
    )
    ESTADOS = [
        ('a', _('Pendiente.')),
        ('s', _('Proforma solicitada.')),
        ('c', _('CPM solicitado.')),
        ('v', _('Para validar.')),
        ('p', _('Pedido realizado.')),
        ('r', _('Recibido.')),
        ('g', _('Autogestión.'))
    ]
    estado = models.CharField(
        max_length=1,
        choices=ESTADOS,
        default='a'
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
        blank=True,
        verbose_name=_('Centro de gasto')
    )

    class Meta:
        verbose_name = _("Pedido")
        verbose_name_plural = _("Pedidos")
        permissions = [
            ('secretaria', _('Privilegios de secretaria (editar pedidos)')),
        ]

    def __str__(self):
        return f'{self.codigo}'

    def email(self, usuario=None):
        """ Este método envia por email una solicitud de presupuesto para
        los articulos incluidos en el pedido. """

        hora = datetime.now().time()
        if time(0) <= hora < time(12):
            saludo = 'Buenos días'
        elif time(12) <= hora < time(20):
            saludo = 'Buenas tardes'
        elif time(20) <= hora <= time(23, 49):
            saludo = 'Buenas noches'
        subject = f'[{self.entrega}] SOLICITUD PROFORMA CODIGO {self.codigo}'
        context = {'pedido': self, 'saludo': saludo}
        if usuario:
            context['usuario'] = usuario

        html_message = render_to_string(
            'gestion/solicitud_email.html',
            context
        )
        plain_message = strip_tags(html_message)
        from_email = 'pedidosterstem@ugr.es'
        to = [self.distribuidor.contacto]
        solicitud_email(
            subject,
            plain_message,
            from_email,
            to,
            html_message
        )

    def concluir(self):
        """ Este método comprueba si todos los articulos relacionados se
        encuentran en estado "recibido" para así concluir el pedido marcandolo
        como "completo". """

        boton = True

        for articulo in self.productos.all():
            if articulo.estado != 'r':
                boton = False

        if boton:
            self.estado = 'r'
            self.save()


class Nota(models.Model):
    """ Este modelo representa un conjunto de artículos anotados
    simultáneamente en la pizarra. Recopila todos los datos compartidos entre
    todos los artículos que han sido añadidos simultáneamente:
        - fecha de anotación
        - usuario que lo ha anotado
        - dirección a la que entregar estos articulos.
    Se puede acceder a los articulos asociado a cada Nota mediante
    Nota.articulos.all()
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
        max_length=150,
        help_text=_('Codigo del centro de gasto dentro de la UGR.')
    )
    pertenencia_ugr = models.BooleanField(
        default=True,
        blank=True,
        help_text=_('¿Centro de gasto de la UGR? (Si/No)'),
        verbose_name=_('Pertenencia a UGR')
    )

    class Meta:
        verbose_name = _("Centro de gasto")
        verbose_name_plural = _("Centros de gasto")

    def __str__(self):
        return f'{self.nombre}'


class PerfilExtendido(models.Model):
    """ En este modelo se almacenará información de los usuarios no
    relacionada con temas de autenticación. """

    usuario = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    telegram_id = models.CharField(
        max_length=9,
        blank=True
    )
    correo = models.BooleanField(
        default=False
    )


class Borrador(models.Model):  # FIXME: Necesario corregir logica de articulos.
    # Hay que distinguir entre articulo.borrador None y True para evitar que sean tramitados
    # como articulos convencionales. Corregir en meth:clasificar y en vistas de articulos.
    """ Este modelo representa un borrador de pedido. Se utiliza para
    guardar pedidos que se realicen muy a menudo, de manera que no haya que
    crearlos manualmente cada vez. Simplemente se acude al borrador
    y se lanza el pedido. """

    nombre = models.CharField(
        max_length=40,
        help_text=_('Nombre para identificar al borrador.')
    )
    productos = models.ManyToManyField(
        Producto,
        through=Articulo,
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
    OPCIONES = [
        ('s', _('Semanal')),
        ('m', _('Mensual')),
        ('a', _('Anual')),
        ('q', _('Quincenal')),
        ('n', _('Ninguna')),
    ]
    periodico = models.CharField(
        max_length=1,
        choices=OPCIONES,
        default='n',
        verbose_name=_('Periodicidad')
    )
    # centro_gasto = models.ForeignKey(
    #     'CentroGasto',
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     verbose_name=_('Centro de gasto')
    # )

    class Meta:
        verbose_name = _("Borrador")
        verbose_name_plural = _("Borradores")

    def __str__(self):
        return f'{self.nombre}'

    def tramitar(self, usuario, solicitar=False):
        """ Crea un pedido a partir del borrador. Indicar solicitar=True para
        solicitar un presupuesto para el pedido recien creado. """

        pedido = Pedido.objects.create(
            codigo=keygen(),
            distribuidor=self.distribuidor,
            entrega=self.entrega
        )
        nota = Nota.objects.create(
            usuario=usuario,
            entrega=self.entrega,
        )

        for articulo in self.articulos.all():
            articulo.pk = None
            articulo.pedido = pedido
            articulo.nota = nota
            articulo.borrador = None
            articulo.save()
        if solicitar:
            pedido.email(usuario=usuario)

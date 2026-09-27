from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField

class SecuenciaCuentaComercial(models.Model):
    siguiente = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "secuencia_cuenta_comercial"

    def __str__(self):
        return f"Siguiente: {self.siguiente}"

# Modelo comercial
class CuentaComercial(models.Model):

    class TipoPersona(models.TextChoices):
        NATURAL = "natural", "Natural"
        JURIDICA = "juridica", "Jurídica"
    class Estado(models.TextChoices):
        PROSPECTO = "prospecto", "Prospecto"
        CLIENTE = "cliente", "Cliente"
        INACTIVO = "inactivo", "Inactivo" #Inactivo creo que no va

    class TipoRelacion(models.TextChoices):
            CLIENTE = "cliente", "Cliente"
            PROVEEDOR = "proveedor", "Proveedor"
            AMBOS   = "ambos", "Ambos"
    class DocumentoIdentidad(models.TextChoices):
        CI = "ci", "CI"
        NIT = "nit", "NIT"
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="cuentas_comerciales", null=True, blank=True)
    nombres = models.CharField(max_length=150, blank=True)
    apellido_paterno = models.CharField(max_length=100, blank=True)
    apellido_materno = models.CharField(max_length=100, blank=True)
    tipo_persona = models.CharField(max_length=20,choices=TipoPersona.choices)
    razon_social = models.CharField(max_length=200, blank=True)
    identificacion = models.PositiveIntegerField(unique=True)
    documento_identidad = models.CharField(max_length=10, choices=DocumentoIdentidad.choices, null=True, blank=True)
    numero_documento = models.CharField(max_length=10, blank=True,)
    telefono = models.CharField(max_length=30,blank=True,)
    correo = models.EmailField(max_length=254,blank=True,)
    direccion = models.CharField(max_length=300,blank=True,)
    estado = models.CharField(max_length=20,choices=Estado.choices,default=Estado.PROSPECTO,)
    tipo_relacion = models.CharField(max_length=20, choices=TipoRelacion.choices, null=True, blank=True)
    ejecutivo_asignado = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="cuentas_comerciales_asignadas", null=True, blank=True,)
    fecha_alta = models.DateTimeField() #Fecha efectiva en que la cuenta comercial fue registrada/dada de alta comercialmente.
    created_at = models.DateTimeField(auto_now_add=True,) #Fecha y hora en que se creó físicamente el registro en la base de datos.
    updated_at = models.DateTimeField(auto_now=True,) #Fecha y hora de la última modificación del registro.

    class Meta:
        db_table = "cuenta_comercial"
        verbose_name = "Cuenta comercial"
        verbose_name_plural = "Cuentas comerciales"
    
    def __str__(self):
        return f"{self.razon_social} - {self.identificacion}"

#Actividad Comercial representa que hizo la ejecutiva
class ActividadComercial(models.Model):
    class Tipo(models.TextChoices):
        LLAMADA = "llamada", "Llamada"
        REUNION = "reunion", "Reunión"
        COTIZACION = "cotizacion", "Cotización"
        SEGUIMIENTO = "seguimiento", "Seguimiento"
        CONFIRMACION = "confirmacion", "Confirmación"

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        EN_PROCESO = "en_proceso", "En proceso"
        COMPLETADA = "completada", "Completada"
        CANCELADA = "cancelada", "Cancelada"

    cuenta_comercial = models.ForeignKey("comercial.CuentaComercial",on_delete=models.PROTECT, related_name="actividades")
    solicitud_comercial = models.ForeignKey("comercial.SolicitudComercial", on_delete=models.PROTECT, related_name="actividades", null=True, blank=True,)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="actividades_comerciales",)
    tipo = models.CharField(max_length=30,choices=Tipo.choices,)
    descripcion = models.TextField()
    fecha_programada = models.DateTimeField()
    fecha_completada = models.DateTimeField(null=True,blank=True,)
    estado = models.CharField( max_length=20,choices=Estado.choices,)
    resultado = models.TextField(null=True,blank=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)

    class Meta:
        db_table = "actividad_comercial"
        verbose_name = "Actividad comercial"
        verbose_name_plural = "Actividades comerciales"
        indexes = [
            models.Index(
                fields=[
                    "usuario",
                    "fecha_programada",
                    "estado",
                ],
                name="ix_act_com_resp_fecha_estado",
            ),
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.cuenta_comercial}"


class SolicitudComercial(models.Model):

    class Prioridad(models.TextChoices):
        BAJA = "baja", "Baja"
        NORMAL = "normal", "Normal"
        ALTA = "alta", "Alta"
        URGENTE = "urgente", "Urgente"

    class Estado(models.TextChoices):
        RECIBIDA = "recibida", "Recibida"
        EN_NEGOCIACION = "en_negociacion", "En negociación"
        EN_VIABILIDAD = "en_viabilidad", "En viabilidad"
        APROBADA = "aprobada", "Aprobada"
        RECHAZADA = "rechazada", "Rechazada"
        CONVERTIDA = "convertida", "Convertida"
        CANCELADA = "cancelada", "Cancelada"

    cuenta_comercial = models.ForeignKey("comercial.CuentaComercial",on_delete=models.PROTECT,related_name="solicitudes",)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="solicitudes_comerciales",)
    fecha = models.DateTimeField()
    descripcion = models.TextField()
    cantidad_unidades = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    cantidad_kg = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True,)
    fecha_entrega = models.DateField(null=True, blank=True,)
    observaciones = models.TextField(blank=True)
    prioridad = models.CharField(max_length=20,choices=Prioridad.choices,)
    estado = models.CharField(max_length=30,choices=Estado.choices,)
    lugar_entrega = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)


    class Meta:
        db_table = "solicitud_comercial"
        verbose_name = "Solicitud comercial"
        verbose_name_plural = "Solicitudes comerciales"

        indexes = [
            models.Index(
                fields=[
                    "cuenta_comercial",
                    "fecha",
                ],
                name="ix_sol_com_cuenta_fecha",
            ),
        ]

    def __str__(self):
        return f"Solicitud #{self.id} - {self.cuenta_comercial}"

class EspecificacionProductoSolicitado(models.Model):

    class TipoCapa(models.TextChoices):
        MONOCAPA = "monocapa", "Monocapa"
        BICAPA = "bicapa", "Bicapa"
        TRICAPA = "tricapa", "Tricapa"
    class Material(models.TextChoices):
        PEAD = "PEAD", "PEAD"
        PEBD = "PEBD", "PEBD"
        PP = "PP", "PP"
        BOPP = "BOPP", "BOPP"
        OTRO = "OTRO", "Otro"

    class Opacidad(models.TextChoices):
        ALTA = "alta", "Alta"
        MEDIA = "media", "Media"
        BAJA = "baja", "Baja"
    class TipoImpresion(models.TextChoices):
        CORRIDA = "corrida", "Corrida"
        DIMENSIONADA = "dimensionada", "Dimensionada"
    
    class PosicionImpresion(models.TextChoices):
        CENTRADA = "centrada", "Centrada"
        PERSONALIZDA = "personalizada", "Personalizada"

    class CaraImpresion(models.TextChoices):
        ANVERSO = "anverso", "Anverso"
        REVERSO = "reverso", "Reverso"
        AMBAS = "ambas", "Anverso y Reverso"

    class TipoTratamientoImpresion(models.TextChoices):
        SOLIDO = "solido", "Color sólido"
        DEGRADADO = "degradado", "Degradado"
        TRAMEADO = "trameado", "Trameado"
    
    class TratamientosAcabadosEspeciales(models.TextChoices):
        FILM_AROMATIZADO = "film_aromatizado", "Film Aromatizado"
        OXOBIODEGRADABLE = "oxobiodegradable", "Oxobiodegradable"
        PERFORADA = "perforada", "Perforada"
        PRECORTE = "precorte", "Precorte"

    solicitud_comercial = models.ForeignKey("comercial.SolicitudComercial",on_delete=models.PROTECT,related_name="especificaciones_producto",)
    diseno = models.ForeignKey("recursos.Diseno",on_delete=models.PROTECT, null=True, blank=True, related_name="especificaciones_solicitadas")
    capas = models.CharField(max_length=20, choices=TipoCapa.choices, default=TipoCapa.MONOCAPA)
    cara_impresion = models.CharField(max_length=20, choices=CaraImpresion.choices, blank=True,)
    categoria_producto = models.ForeignKey("productos.ProductoCategoria",on_delete=models.PROTECT,related_name="especificaciones_solicitadas",)
    material = models.CharField(max_length=20, choices=Material.choices)
    apto_alimento = models.BooleanField(default=False,)
    micraje = models.DecimalField(max_digits=8,decimal_places=2,null=True,blank=True,)
    color_bolsa = models.CharField(max_length=100,blank=True,)
    impresion = models.BooleanField(default=False,)
    color_impresion = ArrayField(base_field=models.CharField(max_length=50),default=list,blank=True,)
    tipo_impresion = models.CharField(max_length=20,blank=True,choices=TipoImpresion.choices)
    posicion_impresion = models.CharField(max_length=20,choices=PosicionImpresion.choices,null=True,blank=True,)
    distancia_impresion_superior = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    distancia_impresion_inferior = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    distancia_impresion_izquierda = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    distancia_impresion_derecha = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    tratamiento_impresion = models.CharField(max_length=20, choices=TipoTratamientoImpresion.choices, default=TipoTratamientoImpresion.SOLIDO,)
    otras_caracteristicas = models.TextField(blank=True,)
    opacidad = models.CharField(max_length=20, choices=Opacidad.choices, blank=True,)
    tratamientos_acabados_especiales = ArrayField(base_field=models.CharField(max_length=30, choices=TratamientosAcabadosEspeciales.choices),default=list,blank=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        db_table = "especificacion_producto_solicitado"
        verbose_name = "Especificación de producto solicitado"
        verbose_name_plural = "Especificaciones de productos solicitados"

    def __str__(self):
        return f"{self.solicitud_comercial} - {self.categoria_producto}"

class EspecificacionBolsaSolicitada(models.Model):

    class TipoTroquel(models.TextChoices):
        CAMISETA = "camiseta", "Camiseta"
        NORMAL = "normal", "Normal"
        RINONERA = "rinonera", "Riñonera"
        CON_ASA = "con_asa", "Con asa"
        REFUERZO = "refuerzo", "Refuerzo"
        SOLAPA = "solapa", "Solapa"
        ADHESIVA = "adhesiva", "Adhesiva"
        CIERRE_FACIL = "cierre_facil", "Cierre fácil"

    class TipoSello(models.TextChoices):
        LATERAL = "lateral", "Lateral"
        FONDO = "fondo", "Fondo"
        NINGUNO = "ninguno", "Ninguno"

    class TipoPestana(models.TextChoices):
        SIN_PESTANA = "sin_pestana", "Sin pestaña"
        SUPERIOR = "superior", "Superior"
        INFERIOR = "inferior", "Inferior"
        AMBAS = "ambas", "Superior e inferior"

        
    especificacion_producto_solicitado = models.OneToOneField("comercial.EspecificacionProductoSolicitado", on_delete=models.PROTECT, related_name="especificacion_bolsa",)
    ancho_doblado = models.DecimalField(max_digits=10,decimal_places=2,)
    ancho_desdoblado = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    largo_doblado = models.DecimalField(max_digits=10,decimal_places=2,)
    largo_desdoblado = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    fuelle = models.BooleanField(default=False,)
    fuelle_izquierdo = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    fuelle_derecho = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    fuelle_inferior = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    fuelle_superior = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    tipo_troquel = models.CharField(max_length=100,blank=True, choices=TipoTroquel.choices)
    tipo_sello = models.CharField(max_length=100,blank=False, choices=TipoSello.choices)
    pestana = models.CharField(max_length=20, choices=TipoPestana.choices, default=TipoPestana.SIN_PESTANA,)
    otras_caracteristicas = models.TextField(blank=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)

    class Meta:
        db_table = "especificacion_bolsa_solicitada"
        verbose_name = "Especificación de bolsa solicitada"
        verbose_name_plural = "Especificaciones de bolsa solicitada"

    def __str__(self):
        return f"Especificación - {self.especificacion_producto_solicitado}"

class EspecificacionBobinaSolicitada(models.Model):
    especificacion_producto_solicitado = models.OneToOneField("comercial.EspecificacionProductoSolicitado", on_delete=models.PROTECT, related_name="especificacion_bobina",)
    ancho = models.DecimalField(max_digits=10,decimal_places=2,)
    diametro = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    diametro_nucleo = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    tipo_nucleo = models.CharField(max_length=100,blank=True,)
    peso = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    longitud = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,)
    otras_caracteristicas = models.TextField(blank=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        db_table = "especificacion_bobina_solicitada"
        verbose_name = "Especificación de bobina solicitada"
        verbose_name_plural = "Especificaciones de bobinas solicitadas"

    def __str__(self):
        return f"Especificación - {self.especificacion_producto_solicitado}"

class VarianteColorSolicitada(models.Model):
    especificacion_producto_solicitado = models.ForeignKey(
        "comercial.EspecificacionProductoSolicitado",
        on_delete=models.PROTECT,
        related_name="variantes_color",
    )
    color = models.CharField(max_length=100,)
    cantidad = models.DecimalField(max_digits=10,decimal_places=2,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        db_table = "variante_color_solicitada"
        verbose_name = "Variante de color solicitada"
        verbose_name_plural = "Variantes de color solicitadas"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "especificacion_producto_solicitado",
                    "color",
                ],
                name="unique_color_por_especificacion",
            )
        ]
    def __str__(self):
        return f"{self.color} - {self.cantidad}"



class Comunicacion(models.Model):

    class Tipo(models.TextChoices):
        LLAMADA = "llamada", "Llamada"
        CORREO = "correo", "Correo"
        MENSAJE = "mensaje", "Mensaje"
        REUNION = "reunion", "Reunión"
        VISITA = "visita", "Visita"
        OTRO = "otro", "Otro"
    
    class Medio(models.TextChoices):
        TELEFONO = "telefono", "Teléfono"
        EMAIL = "email", "Correo electrónico"
        WHATSAPP = "whatsapp", "WhatsApp"
        PRESENCIAL = "presencial", "Presencial"
        VIDEOLLAMADA = "videollamada", "Videollamada"
        OTRO = "otro", "Otro"
    
    class Direccion(models.TextChoices):
        SALIENTE = "saliente", "Ejecutivo -> Cliente"
        ENTRANTE = "entrante", "Cliente -> Ejecutivo"


    solicitud_comercial = models.ForeignKey("comercial.SolicitudComercial",on_delete=models.PROTECT,related_name="comunicaciones",)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="comunicaciones_comerciales",)
    tipo = models.CharField(max_length=30, choices=Tipo.choices,)
    medio = models.CharField(max_length=30, choices=Medio.choices,)
    direccion = models.CharField(max_length=20, choices=Direccion.choices, null=True, blank=True,)
    asunto = models.CharField(max_length=200,null=True,blank=True,)
    contenido = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        db_table = "comunicacion"
        verbose_name = "Comunicación"
        verbose_name_plural = "Comunicaciones"

        indexes = [
            models.Index(
                fields=[
                    "solicitud_comercial",
                    "created_at",
                ],
                name="ix_com_sol_created_at",
            ),
        ]

    def __str__(self):
        return f"{self.tipo} - {self.solicitud_comercial_id}"

#La cotización representa la propuesta comercial 
# generada para una solicitud y tiene una relación 1:N con SolicitudComercial.
class Cotizacion(models.Model):

    class Estado(models.TextChoices):
        BORRADOR = "borrador", "Borrador",
        ACTIVA = "activa", "Activa",
        CERRADA = "cerrada", "Cerrada"
        ANULADA = "anulada", "Anulada"
    #Usamos PROTECT porque no queremos eliminar una solicitud que tenga cotizaciones históricas asociadas.
    solicitud_comercial = models.ForeignKey("comercial.SolicitudComercial",on_delete=models.PROTECT,related_name="cotizaciones",)
    numero = models.CharField(max_length=50,unique=True,)
    fecha_emision = models.DateTimeField()
    fecha_vencimiento = models.DateField(null=True,blank=True,)
    estado = models.CharField(max_length=20, choices=Estado.choices)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)

    class Meta:
        db_table = "cotizacion"
        verbose_name = "Cotización"
        verbose_name_plural = "Cotizaciones"

    def __str__(self):
        return self.numero

class CotizacionVersion(models.Model):
    class Moneda(models.TextChoices):
            BOB = "BOB", "Boliviano"
            USD = "USD", "Dólares"
    class Estado(models.TextChoices):
            BORRADOR = "borrador", "Borrador"
            ENVIADA = "enviada", "Enviada"
            ACEPTADA = "aceptada", "Aceptada"
            RECHAZADA = "rechazada", "Rechazada"
            ANULADA = "anulada", "Anulada"
    cotizacion = models.ForeignKey("comercial.Cotizacion",on_delete=models.CASCADE,related_name="versiones",)
    version  = models.PositiveIntegerField()
    moneda = models.CharField(max_length=3,choices=Moneda.choices, default=Moneda.BOB)
    precio_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.BORRADOR)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cotizacion_version"
        verbose_name = "Versión de cotización"
        verbose_name_plural = "Versiones de cotización"

        constraints = [
            models.UniqueConstraint(
                fields=["cotizacion", "version"],
                name="unique_cotizacion_version"
            )
        ]

        ordering = ["cotizacion", "-version"]

    def __str__(self):
        return f"{self.cotizacion} - Versión {self.version}"

class CotizacionDetalle(models.Model):
    cotizacion_version = models.ForeignKey("comercial.CotizacionVersion", on_delete=models.PROTECT,related_name="detalles")
    producto_version = models.ForeignKey("productos.ProductoVersion", on_delete=models.PROTECT, related_name="detalles_cotizacion",)
    cantidad = models.DecimalField(max_digits=12, decimal_places=2,)
    precio_unitario = models.DecimalField(max_digits=12,decimal_places=2,)
    precio_total = models.DecimalField(max_digits=12, decimal_places=2,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cotizacion_detalle"
        verbose_name = "Detalle de cotización"
        verbose_name_plural = "Detalles de cotización"

    def __str__(self):
        return f"{self.cotizacion_version} - {self.producto_version}"

class Pedido(models.Model):
    class Estado(models.TextChoices):
        FINALIZADO = "finalizado", "Finalizado",
        EN_PROCESO = "en_proceso", "En proceso",

    cotizacion_version = models.ForeignKey("comercial.CotizacionVersion", on_delete=models.PROTECT,related_name="pedidos",)
    cuenta_comercial = models.ForeignKey("comercial.CuentaComercial", on_delete=models.PROTECT, related_name="pedidos")
    numero = models.CharField(max_length=50, unique=True,)
    fecha_pedido = models.DateTimeField()
    estado = models.CharField(max_length=30, choices=Estado.choices,)
    fecha_entrega_comprometida = models.DateTimeField()
    observaciones = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "pedido"
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return self.numero
    
class PedidoDetalle(models.Model):
    pedido = models.ForeignKey("comercial.Pedido", on_delete=models.PROTECT,related_name="detalles",)
    producto_version = models.ForeignKey("productos.ProductoVersion", on_delete=models.PROTECT, related_name="detalles_pedido",)
    cantidad = models.DecimalField(max_digits=12, decimal_places=2,)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2,)
    precio_total = models.DecimalField(max_digits=12, decimal_places=2,)
    fecha_entrega_comprometida = models.DateTimeField()
    observaciones = models.TextField(blank=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pedido_detalle"
        verbose_name = "Detalle de pedido"
        verbose_name_plural = "Detalles de pedido"

    def __str__(self):
        return f"{self.pedido} - {self.producto_version}"



    


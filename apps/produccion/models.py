from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from django.conf import settings

class OrdenProduccion(models.Model):

    class Estado(models.TextChoices):
        PLANIFICADA = "planificada", "Planificada"
        EN_PROCESO = "en_proceso", "En proceso"
        COMPLETADA = "completada", "Completada"
        CANCELADA = "cancelada", "Cancelada"

    class Prioridad(models.TextChoices):
        BAJA = "baja", "Baja"
        NORMAL = "normal", "Normal"
        ALTA = "alta", "Alta"
        URGENTE = "urgente", "Urgente"

    pedido_detalle = models.ForeignKey("comercial.PedidoDetalle", on_delete=models.PROTECT, null=True, blank=True, related_name="ordenes_produccion")
    evaluacion_viabilidad = models.ForeignKey("viabilidad.EvaluacionViabilidad",on_delete=models.PROTECT,related_name="ordenes_produccion", null=True, blank=True)
    numero = models.CharField(max_length=50,unique=True,)
    cantidad_planificada = models.DecimalField(max_digits=12,decimal_places=2,)
    fecha_inicio_planificada = models.DateTimeField()
    fecha_fin_planificada = models.DateTimeField()
    estado = models.CharField(max_length=30,choices=Estado.choices,default=Estado.PLANIFICADA,)
    prioridad = models.CharField(max_length=20,choices=Prioridad.choices,default=Prioridad.NORMAL,)
    observaciones = models.TextField(blank=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        db_table = "orden_produccion"
        verbose_name = "Orden de producción"
        verbose_name_plural = "Órdenes de producción"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.numero}"

class OrdenProduccionDetalle(models.Model):

    class Estado(models.TextChoices):
        PROGRAMADA = "programada", "Programada"
        EN_PROCESO = "en_proceso", "En proceso"
        COMPLETADA = "completada", "Completada"
        CANCELADA = "cancelada", "Cancelada"

    orden_produccion = models.ForeignKey("produccion.OrdenProduccion",on_delete=models.PROTECT,related_name="detalles",)
    pedido_detalle = models.ForeignKey("comercial.PedidoDetalle",on_delete=models.PROTECT,related_name="detalles_produccion",)
    cantidad_programada = models.DecimalField(max_digits=12,decimal_places=2,)
    cantidad_atendida = models.DecimalField(max_digits=12,decimal_places=2,default=0,)
    estado = models.CharField(max_length=30,choices=Estado.choices,default=Estado.PROGRAMADA,)
    observaciones = models.TextField(blank=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        db_table = "orden_produccion_detalle"
        verbose_name = "Detalle de orden de producción"
        verbose_name_plural = "Detalles de órdenes de producción"

    def __str__(self):
        return f"{self.orden_produccion} - Pedido detalle #{self.pedido_detalle_id}"

class PlanProduccion(models.Model):

    class Estado(models.TextChoices):
        BORRADOR = "borrador", "Borrador"
        PLANIFICADO = "planificado", "Planificado"
        EN_PROCESO = "en_proceso", "En proceso"
        COMPLETADO = "completado", "Completado"
        CANCELADO = "cancelado", "Cancelado"

    fecha_plan = models.DateField()
    estado = models.CharField(max_length=30,choices=Estado.choices,default=Estado.BORRADOR,)
    observaciones = models.TextField(blank=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "plan_produccion"
        verbose_name = "Plan de producción"
        verbose_name_plural = "Planes de producción"
        ordering = ["-fecha_plan"]

    def __str__(self):
        return f"Plan #{self.id} - {self.fecha_plan}"

class PlanDetalle(models.Model):

    class Estado(models.TextChoices):
        PROGRAMADO = "programado", "Programado"
        EN_PROCESO = "en_proceso", "En proceso"
        COMPLETADO = "completado", "Completado"
        CANCELADO = "cancelado", "Cancelado"

    plan_produccion = models.ForeignKey("produccion.PlanProduccion",on_delete=models.PROTECT,related_name="detalles",)
    orden_produccion = models.ForeignKey("produccion.OrdenProduccion",on_delete=models.PROTECT,related_name="planes",)
    fecha_programada = models.DateField()
    cantidad_programada = models.DecimalField(max_digits=12,decimal_places=2,)
    estado = models.CharField(max_length=30,choices=Estado.choices,default=Estado.PROGRAMADO,)
    observaciones = models.TextField(blank=True,)

    class Meta:
        db_table = "plan_detalle"
        verbose_name = "Detalle de plan de producción"
        verbose_name_plural = "Detalles de planes de producción"

    def __str__(self):
        return f"{self.plan_produccion} - {self.orden_produccion}"

class ColaOperacion(models.Model):

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        EN_PROCESO = "en_proceso", "En proceso"
        COMPLETADA = "completada", "Completada"
        CANCELADA = "cancelada", "Cancelada"

    produccion_operacion = models.OneToOneField("produccion.ProduccionOperacion",on_delete=models.PROTECT,related_name="cola",)
    posicion = models.PositiveIntegerField()
    estado = models.CharField(max_length=30,choices=Estado.choices,default=Estado.PENDIENTE,)
    fecha_entrada = models.DateTimeField()
    fecha_salida = models.DateTimeField(null=True,blank=True,)
    class Meta:
        db_table = "cola_operacion"
        verbose_name = "Cola de operación"
        verbose_name_plural = "Colas de operaciones"
        ordering = ["posicion"]

    def __str__(self):
        return f"Cola #{self.posicion} - {self.produccion_operacion}"

class RutaProduccion(models.Model):

    class Estado(models.TextChoices):
        ACTIVA = "activa", "Activa"
        INACTIVA = "inactiva", "Inactiva"

    codigo = models.CharField(max_length=50,unique=True,)
    nombre = models.CharField(max_length=200,)
    descripcion = models.TextField(blank=True,)
    estado = models.CharField(max_length=20,choices=Estado.choices,default=Estado.ACTIVA,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ruta_produccion"
        verbose_name = "Ruta de producción"
        verbose_name_plural = "Rutas de producción"

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class PasoRuta(models.Model):

    class Estado(models.TextChoices):
        ACTIVO = "activo", "Activo"
        INACTIVO = "inactivo", "Inactivo"

    ruta_produccion = models.ForeignKey("produccion.RutaProduccion",on_delete=models.PROTECT,related_name="pasos",)
    numero = models.PositiveIntegerField()
    nombre = models.CharField(max_length=200,)
    descripcion = models.TextField(blank=True,)
    orden_ejecucion = models.PositiveIntegerField()
    estado = models.CharField(max_length=20,choices=Estado.choices,default=Estado.ACTIVO,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "paso_ruta"
        verbose_name = "Paso de ruta"
        verbose_name_plural = "Pasos de ruta"
        ordering = ["orden_ejecucion"]

    def __str__(self):
        return f"{self.ruta_produccion} - Paso {self.numero}"

class RutaOperacion(models.Model):

    class Estado(models.TextChoices):
        ACTIVA = "activa", "Activa"
        INACTIVA = "inactiva", "Inactiva"

    ruta_paso = models.ForeignKey("produccion.PasoRuta",on_delete=models.PROTECT,related_name="operaciones",)
    tiempo_estandar_min = models.DecimalField(max_digits=10,decimal_places=2,)
    descripcion = models.TextField(blank=True,)
    orden_ejecucion = models.PositiveIntegerField()
    estado = models.CharField(max_length=20,choices=Estado.choices,default=Estado.ACTIVA,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        db_table = "ruta_operacion"
        verbose_name = "Operación de ruta"
        verbose_name_plural = "Operaciones de ruta"
        ordering = ["orden_ejecucion"]

    def __str__(self):
        return f"{self.ruta_paso} - Operación {self.orden_ejecucion}"

class OrdenRuta(models.Model):

    class Estado(models.TextChoices):
        ACTIVA = "activa", "Activa"
        COMPLETADA = "completada", "Completada"
        CANCELADA = "cancelada", "Cancelada"

    orden_produccion = models.ForeignKey("produccion.OrdenProduccion",on_delete=models.PROTECT,related_name="rutas",)
    ruta_produccion = models.ForeignKey("produccion.RutaProduccion",on_delete=models.PROTECT,related_name="ordenes",)
    version = models.PositiveIntegerField()
    estado = models.CharField(max_length=20,choices=Estado.choices,default=Estado.ACTIVA,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orden_ruta"
        verbose_name = "Ruta de orden de producción"
        verbose_name_plural = "Rutas de órdenes de producción"

    def __str__(self):
        return f"{self.orden_produccion} - {self.ruta_produccion} V{self.version}"

class ProduccionOperacion(models.Model):

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        EN_PROCESO = "en_proceso", "En proceso"
        COMPLETADA = "completada", "Completada"
        CANCELADA = "cancelada", "Cancelada"

    orden_ruta = models.ForeignKey("produccion.OrdenRuta",on_delete=models.PROTECT,related_name="operaciones",)
    ruta_operacion = models.ForeignKey("produccion.RutaOperacion",on_delete=models.PROTECT,related_name="producciones",)
    resultado_viabilidad = models.ForeignKey("viabilidad.ResultadoViabilidad",on_delete=models.PROTECT,related_name="producciones_operacion",)
    equipo = models.ForeignKey("recursos.Equipo",on_delete=models.PROTECT,related_name="producciones_operacion",)
    numero_operacion = models.PositiveIntegerField()
    fecha_inicio_planificada = models.DateTimeField()
    fecha_inicio_real = models.DateTimeField(null=True,blank=True,)
    fecha_fin_planificada = models.DateTimeField()
    fecha_fin_real = models.DateTimeField(null=True,blank=True,)
    estado = models.CharField(max_length=30,choices=Estado.choices,default=Estado.PENDIENTE,)
    cantidad_producida = models.DecimalField(max_digits=12,decimal_places=2,default=0,)
    observaciones = models.TextField(blank=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "produccion_operacion"
        verbose_name = "Operación de producción"
        verbose_name_plural = "Operaciones de producción"
        ordering = ["numero_operacion"]

    def __str__(self):
        return f"Operación {self.numero_operacion} - {self.orden_ruta}"

class Dosificacion(models.Model):

    producto_version = models.ForeignKey("productos.ProductoVersion",on_delete=models.PROTECT,related_name="dosificaciones",)
    materia_prima = models.ForeignKey("inventario.MateriaPrima",on_delete=models.PROTECT,related_name="dosificaciones",)
    cantidad = models.DecimalField(max_digits=12,decimal_places=2,)
    unidad_medida = models.CharField(max_length=30,)
    porcentaje = models.DecimalField(max_digits=5,decimal_places=2,)
    activo = models.BooleanField(default=True,)
    observaciones = models.TextField(blank=True,)
    class Meta:
        db_table = "dosificacion"
        verbose_name = "Dosificación"
        verbose_name_plural = "Dosificaciones"

    def __str__(self):
        return f"{self.producto_version} - {self.materia_prima}"

class ConsumoProduccion(models.Model):

    produccion_operacion = models.ForeignKey("produccion.ProduccionOperacion",on_delete=models.PROTECT,related_name="consumos",)
    materia_prima = models.ForeignKey("inventario.MateriaPrima",on_delete=models.PROTECT,related_name="consumos_produccion",)
    cantidad_entregada = models.DecimalField(max_digits=12,decimal_places=2,)
    cantidad_utilizada = models.DecimalField(max_digits=12,decimal_places=2,)
    cantidad_scrap = models.DecimalField(max_digits=12,decimal_places=2,default=0,)
    unidad_medida = models.CharField(max_length=30,)
    observaciones = models.TextField(blank=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        db_table = "consumo_produccion"
        verbose_name = "Consumo de producción"
        verbose_name_plural = "Consumos de producción"

    def __str__(self):
        return (
            f"{self.produccion_operacion} - "
            f"{self.materia_prima}"
        )

class LoteProduccion(models.Model):

    produccion_operacion = models.ForeignKey("produccion.ProduccionOperacion",on_delete=models.PROTECT,related_name="lotes_produccion",)
    producto_version = models.ForeignKey("productos.ProductoVersion", on_delete=models.PROTECT, related_name="lotes_produccion", null=True, blank=True,)
    codigo = models.CharField(max_length=50,unique=True,)
    cantidad_total = models.DecimalField(max_digits=12,decimal_places=2,default=0,)
    unidad_medida = models.CharField(max_length=30,)
    observaciones = models.TextField(blank=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        db_table = "lote_produccion"
        verbose_name = "Lote de producción"
        verbose_name_plural = "Lotes de producción"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.codigo} - {self.produccion_operacion}"   
         
class ResultadoProduccion(models.Model):

    produccion_operacion = models.ForeignKey("produccion.ProduccionOperacion",on_delete=models.PROTECT,related_name="resultados_produccion")
    lote = models.ForeignKey("produccion.LoteProduccion",on_delete=models.PROTECT, related_name="resultados", null=True, blank=True)
    codigo = models.CharField(max_length=50, unique=True,)
    cantidad = models.DecimalField(max_digits=12,decimal_places=2,)
    unidad_medida = models.CharField(max_length=30,)

    # ===== EXTRUSIÓN =====

    ancho_obtenido = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    micraje_obtenido = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    material_obtenido = models.CharField(max_length=100,blank=True,)
    color_obtenido = models.CharField(max_length=100,blank=True,)
    olor = models.CharField(max_length=100,blank=True,)
    peso_obtenido = models.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True,)

    # ===== FLEXOGRAFÍA =====

    impresion = models.BooleanField(default=False,)
    colores_obtenidos = ArrayField(models.CharField(max_length=50),default=list,blank=True,)
    calidad_color = models.CharField(max_length=100,blank=True,)
    tonalidad = models.CharField(max_length=100,blank=True,)
    diseno = models.CharField(max_length=200,blank=True,)
    posicion_impresion = models.CharField(max_length=50,blank=True,)
    distancia_arriba = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    distancia_abajo = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    distancia_izquierda = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    distancia_derecha = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)

    # ===== CONFECCIÓN =====
    largo_obtenido = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    tipo_sello = models.CharField(max_length=100,blank=True,)
    tipo_troquel = models.CharField(max_length=100,blank=True,)
    observaciones = models.TextField(blank=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        db_table = "resultado_produccion"
        verbose_name = "Resultado de producción"
        verbose_name_plural = "Resultados de producción"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.codigo} - {self.produccion_operacion}"

class BobinaProduccion(models.Model):
    """
    Las bobinas son unidades de producción generadas durante una operación. Según la ruta de producción, 
    pueden constituir un producto terminado o ser utilizadas como insumo de una operación posterior.
    """
    
    class Estado(models.TextChoices):
        EN_PRODUCCION = "en_produccion", "En producción"
        TERMINADA = "terminada", "Terminada"
        TRANSFERIDA = "transferida", "Transferida"
        RECHAZADA = "rechazada", "Rechazada"
        EN_ALMACEN = "en_almacen", "En almacén"
    
    class Calidad(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        APROBADA = "aprobada", "Aprobada"
        REPROCESAR = "reprocesar", "Reprocesar"
        RECHAZADA = "rechazada", "Rechazada"
    
    produccion_operacion = models.ForeignKey("produccion.ProduccionOperacion",on_delete=models.PROTECT,related_name="bobinas",)
    lote = models.ForeignKey("produccion.LoteProduccion",on_delete=models.PROTECT,related_name="bobinas",null=True, blank=True,)
    codigo = models.CharField(max_length=50,unique=True,help_text="Código único de identificación de la bobina")
    # Características físicas
    peso = models.DecimalField(max_digits=12,decimal_places=2,help_text="Peso de la bobina en kg")
    ancho = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,help_text="Ancho de la bobina en mm")
    diametro = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,help_text="Diámetro de la bobina en mm")
    diametro_nucleo = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,help_text="Diámetro del núcleo en mm")
    longitud = models.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True,help_text="Longitud de la bobina en metros")
    # Estado y calidad
    estado = models.CharField(max_length=30,choices=Estado.choices,default=Estado.EN_PRODUCCION)
    calidad = models.CharField(max_length=30,choices=Calidad.choices,default=Calidad.PENDIENTE)
    # Referencias a control de calidad
    control_calidad = models.ForeignKey("calidad.ControlCalidad",on_delete=models.PROTECT,null=True,blank=True,related_name="bobinas")
    # Información de transferencia
    operacion_destino = models.ForeignKey("produccion.ProduccionOperacion",on_delete=models.PROTECT,null=True,blank=True,related_name="bobinas_recibidas",help_text="Operación a la que fue transferida esta bobina")
    fecha_transferencia = models.DateTimeField(null=True,blank=True,help_text="Fecha en que se transfirió la bobina")
    # Observaciones
    observaciones = models.TextField(blank=True)
    # Fechas
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_terminacion = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "bobina_produccion"
        verbose_name = "Bobina de producción"
        verbose_name_plural = "Bobinas de producción"
        ordering = ["-fecha_creacion"]
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['estado']),
            models.Index(fields=['calidad']),
            models.Index(fields=['produccion_operacion']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.peso}kg - {self.get_estado_display()}"
    
    def marcar_terminada(self):
        """Marca la bobina como terminada."""
        from django.utils import timezone
        self.estado = self.Estado.TERMINADA
        self.fecha_terminacion = timezone.now()
        self.save()
    
    def transferir_a(self, operacion_destino):
        """Transfiere la bobina a otra operación."""
        from django.utils import timezone
        self.operacion_destino = operacion_destino
        self.estado = self.Estado.TRANSFERIDA
        self.fecha_transferencia = timezone.now()
        self.save()


class MermaProduccion(models.Model):
    """
    Modelo para registrar mermas (pérdidas) por operación de producción.
    
    Las mermas representan material perdido durante el proceso productivo
    por diferentes razones: arranque, proceso, calidad, etc.
    """
    
    class TipoMerma(models.TextChoices):
        ARRANQUE = "arranque", "Arranque"
        PROCESO = "proceso", "Proceso"
        CALIDAD = "calidad", "Calidad"
        MANTENIMIENTO = "mantenimiento", "Mantenimiento"
        OTRO = "otro", "Otro"
    
    class Causa(models.TextChoices):
        CONFIGURACION = "configuracion", "Configuración"
        MATERIAL = "material", "Material defectuoso"
        EQUIPO = "equipo", "Falla de equipo"
        OPERADOR = "operador", "Error operacional"
        ESPECIFICACION = "especificacion", "Cambio especificación"
        DESCONOCIDA = "desconocida", "Causa desconocida"
        OTRO = "otro", "Otra causa"
    
    produccion_operacion = models.ForeignKey("produccion.ProduccionOperacion",on_delete=models.PROTECT,related_name="mermas",)
    tipo_merma = models.CharField(max_length=30,choices=TipoMerma.choices,help_text="Tipo de merma registrada")
    causa = models.CharField(max_length=30,choices=Causa.choices,help_text="Causa de la merma")
    cantidad = models.DecimalField(max_digits=12,decimal_places=2,help_text="Cantidad de material perdido (en kg o unidad según proceso)")
    unidad_medida = models.CharField(max_length=30,default="kg",help_text="Unidad de medida de la merma")
    # Referencia opcional a bobina específica si aplica
    bobina = models.ForeignKey("produccion.BobinaProduccion",on_delete=models.PROTECT,null=True,blank=True,related_name="mermas",help_text="Bobina asociada si la merma es específica")
    # Referencia a control de calidad si es merma por calidad
    control_calidad = models.ForeignKey("calidad.ControlCalidad",on_delete=models.PROTECT,null=True,blank=True,related_name="mermas",help_text="Control de calidad que generó la merma")
    # Usuario que registró la merma
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="mermas_registradas")
    # Observaciones y justificación
    observaciones = models.TextField(blank=True,help_text="Descripción detallada de la merma")
    # Fechas
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_merma = models.DateTimeField(help_text="Fecha y hora en que ocurrió la merma")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "merma_produccion"
        verbose_name = "Merma de producción"
        verbose_name_plural = "Mermas de producción"
        ordering = ["-fecha_registro"]
        indexes = [
            models.Index(fields=['tipo_merma']),
            models.Index(fields=['causa']),
            models.Index(fields=['produccion_operacion']),
            models.Index(fields=['fecha_merma']),
        ]
    
    def __str__(self):
        return f"Merma {self.tipo_merma} - {self.cantidad} {self.unidad_medida} - {self.produccion_operacion}"

class TransferenciaProduccion(models.Model):

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        APROBADA = "aprobada", "Aprobada"
        RECHAZADA = "rechazada", "Rechazada"
        COMPLETADA = "completada", "Completada"

    operacion_origen = models.ForeignKey("produccion.ProduccionOperacion",on_delete=models.PROTECT,related_name="transferencias_origen",)
    operacion_destino = models.ForeignKey("produccion.ProduccionOperacion",on_delete=models.PROTECT,related_name="transferencias_destino",)
    cantidad_total = models.DecimalField(max_digits=12,decimal_places=2,default=0,)
    unidad_medida = models.CharField(max_length=30,default="kg",)
    estado = models.CharField(max_length=30,choices=Estado.choices,default=Estado.PENDIENTE,)
    control_calidad = models.ForeignKey("calidad.ControlCalidad",on_delete=models.PROTECT,null=True,blank=True,related_name="transferencias_produccion",)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="transferencias_produccion",)
    observaciones = models.TextField(blank=True,)
    fecha_transferencia = models.DateTimeField(null=True,blank=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)

    class Meta:
        db_table = "transferencia_produccion"
        verbose_name = "Transferencia de producción"
        verbose_name_plural = "Transferencias de producción"
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Transferencia {self.id} - "
            f"{self.operacion_origen} → {self.operacion_destino}"
        )

class DetalleTransferenciaProduccion(models.Model):

    transferencia = models.ForeignKey("produccion.TransferenciaProduccion",on_delete=models.PROTECT,related_name="detalles",)
    bobina = models.ForeignKey("produccion.BobinaProduccion",on_delete=models.PROTECT,related_name="detalles_transferencia",)
    cantidad = models.DecimalField(max_digits=12,decimal_places=2,)
    unidad_medida = models.CharField(max_length=30,default="kg",)
    observaciones = models.TextField(blank=True,)

    class Meta:
        db_table = "detalle_transferencia_produccion"
        verbose_name = "Detalle de transferencia"
        verbose_name_plural = "Detalles de transferencia"
        constraints = [
            models.UniqueConstraint(
                fields=["transferencia", "bobina"],
                name="unique_bobina_transferencia",
            )
        ]

    def __str__(self):
        return (
            f"{self.transferencia} - "
            f"{self.bobina.codigo}"
        )
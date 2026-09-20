from django.db import models
from django.conf import settings


class EvaluacionComercial(models.Model):
    especificacion_producto_solicitado = models.ForeignKey("comercial.EspecificacionProductoSolicitado",on_delete=models.PROTECT,related_name="evaluaciones_comerciales",)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="evaluaciones_comerciales",)
    resultado = models.CharField(max_length=100,)
    fecha = models.DateTimeField()
    observaciones = models.TextField(blank=True,)
    updated_at = models.DateTimeField(auto_now=True,)

    class Meta:
        db_table = "evaluacion_comercial"
        verbose_name = "Evaluación comercial"
        verbose_name_plural = "Evaluaciones comerciales"

    def __str__(self):
        return f"Evaluación comercial #{self.id}"

#Representa la evaluacion de si técnicamente es viable fabricar los solicitado
class EvaluacionViabilidad(models.Model):
    
    class EstadoAprobacion(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        APROBADA = "aprobada", "Aprobada"
        RECHAZADA = "rechazada", "Rechazada"
    
    evaluacion_comercial = models.ForeignKey("viabilidad.EvaluacionComercial",on_delete=models.PROTECT,null=True,blank=True,related_name="evaluaciones_viabilidad",)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="evaluaciones_viabilidad",)
    resultado = models.CharField(max_length=100,)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(null=True,blank=True,)
    estado_aprobacion = models.CharField(max_length=30, choices=EstadoAprobacion.choices, default=EstadoAprobacion.PENDIENTE)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    aprobado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="aprobaciones_viabilidad")
    observaciones = models.TextField(blank=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)

    class Meta:
        db_table = "evaluacion_viabilidad"
        verbose_name = "Evaluación de viabilidad"
        verbose_name_plural = "Evaluaciones de viabilidad"

    def __str__(self):
        return f"Viabilidad #{self.id} - {self.resultado}"

class EvaluacionProceso(models.Model):

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        EN_PROCESO = "en_proceso", "En proceso"
        COMPLETADA = "completada", "Completada"
        CANCELADA = "cancelada", "Cancelada"

    evaluacion_viabilidad = models.ForeignKey("viabilidad.EvaluacionViabilidad",on_delete=models.PROTECT,related_name="evaluaciones_proceso",)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="evaluaciones_proceso",)
    proceso = models.CharField(max_length=50, null=True, blank=True, help_text="Tipo de proceso: extrusion, flexografia, confeccion")
    maquina_seleccionada = models.ForeignKey("recursos.Equipo", on_delete=models.PROTECT, null=True, blank=True, related_name="selecciones_proceso")
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(null=True,blank=True,)
    estado = models.CharField(max_length=30, choices=Estado.choices,default=Estado.PENDIENTE)
    observaciones = models.TextField(blank=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        db_table = "evaluacion_proceso"
        verbose_name = "Evaluación de proceso"
        verbose_name_plural = "Evaluaciones de proceso"

    def __str__(self):
        return f"Proceso #{self.id} - {self.estado}"

class ResultadoViabilidad(models.Model):
    class Prioridad(models.TextChoices):
        BAJA = "baja", "Baja"
        MEDIA = "media", "Media"
        ALTA = "alta", "Alta"

    
    evaluacion_proceso = models.ForeignKey("viabilidad.EvaluacionProceso",on_delete=models.PROTECT,related_name="resultados_viabilidad",)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="resultados_viabilidad",)
    equipo = models.ForeignKey("recursos.Equipo",on_delete=models.PROTECT,related_name="resultados_viabilidad",)
    anilla = models.ForeignKey("recursos.Anilla",on_delete=models.PROTECT,null=True,blank=True,related_name="resultados_viabilidad",)
    rodillo = models.ForeignKey("recursos.Rodillo",on_delete=models.PROTECT,null=True,blank=True,related_name="resultados_viabilidad",)
    cliche = models.ForeignKey("recursos.Cliche",on_delete=models.PROTECT,null=True,blank=True,related_name="resultados_viabilidad",)
    resultado = models.CharField(max_length=100,)
    puntaje_viabilidad = models.DecimalField(max_digits=5,decimal_places=2,)
    criterios_evaluados = models.JSONField(default=dict, blank=True,)
    prioridad = models.CharField(max_length=30, choices=Prioridad.choices, default=Prioridad.MEDIA)
    es_recomendada = models.BooleanField(default=False,)
    requiere_adaptacion = models.BooleanField(default=False,)
    adaptacion_propuesta = models.TextField(blank=True,)
    observacion = models.TextField(blank=True,)
    fecha_evaluacion = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        db_table = "resultado_viabilidad"
        verbose_name = "Resultado de viabilidad"
        verbose_name_plural = "Resultados de viabilidad"

    def __str__(self):
        return f"Resultado #{self.id} - {self.resultado}"

class RutaViabilidad(models.Model):
    evaluacion_viabilidad = models.ForeignKey("viabilidad.EvaluacionViabilidad",on_delete=models.PROTECT,related_name="rutas",)
    maquinaria = models.ForeignKey("recursos.Maquinaria",on_delete=models.PROTECT,null=True,blank=True,related_name="rutas_viabilidad",)
    orden = models.PositiveIntegerField()
    proceso = models.CharField(max_length=50)
    observaciones = models.TextField(blank=True)

    class Meta:
        db_table = "ruta_viabilidad"
        ordering = ["orden"]
        constraints = [
            models.UniqueConstraint(
                fields=["evaluacion_viabilidad", "orden"],
                name="unique_orden_ruta_viabilidad",
            )
        ]


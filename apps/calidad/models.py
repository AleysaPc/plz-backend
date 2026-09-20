from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField
class ControlCalidad(models.Model):
    class MomentoControl(models.TextChoices):
        INICIO = "inicio", "Inicio"
        PROCESO = "proceso", "Proceso"
        FINAL = "final", "Final"
    class Resultado(models.TextChoices):
        APROBADO = "aprobado", "Aprobado"
        RECHAZADO = "rechazado", "Rechazado"
        OBSERVADO = "observado", "Observado"
        PENDIENTE = "pendiente", "Pendiente"
    produccion_operacion = models.ForeignKey("produccion.ProduccionOperacion",on_delete=models.PROTECT,related_name="controles_calidad",)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="controles_calidad",)
    tiempo_control = models.DecimalField(max_digits=10,decimal_places=2, null=True, blank=True,)
    momento_control = models.CharField(max_length=20, choices=MomentoControl.choices,)
    resultado = models.CharField(max_length=20, choices=Resultado.choices)
    observaciones = models.TextField(blank=True,)
    fecha_control = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        db_table = "control_calidad"
        verbose_name = "Control de calidad"
        verbose_name_plural = "Controles de calidad"
        ordering = ["-fecha_control"]

    def __str__(self):
        return f"Control #{self.id} - {self.resultado}"

class ControlExtrusion(models.Model):
    control_calidad = models.OneToOneField("calidad.ControlCalidad",on_delete=models.PROTECT,related_name="control_extrusion",)
    micraje_medido = models.DecimalField(max_digits=10,decimal_places=2,)
    ancho_medido = models.DecimalField(max_digits=10,decimal_places=2,)
    peso_muestra = models.DecimalField(max_digits=10,decimal_places=2,)
    apariencia = models.PositiveBigIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ]

    )
    uniformidad = models.PositiveBigIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ]
    )
    resistencia = models.PositiveBigIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ]
    )
    observaciones = models.TextField(blank=True)

    class Meta:
        db_table = "control_extrusion"
        verbose_name = "Control de extrusión"
        verbose_name_plural = "Controles de extrusión"

    def __str__(self):
        return f"Control de extrusión #{self.id}"

class ControlFlexografia(models.Model):
    class Evaluacion(models.TextChoices):
        RECHAZADO = "rechazado", "Rechazado"
        ACEPTABLE = "aceptable", "Aceptable"
        BUENO = "bueno", "Bueno"
        MUY_BUENO = "muy_bueno", "Muy bueno"

    control_calidad = models.OneToOneField("calidad.ControlCalidad",on_delete=models.PROTECT,related_name="control_flexo",)
    color = ArrayField(models.CharField(max_length=50),default=list,blank=True)
    registro_impresion = models.CharField(max_length=100)
    calidad_impresion = models.CharField(max_length=20, choices=Evaluacion.choices)
    adhesion_tinta = models.CharField(max_length=20, choices=Evaluacion.choices)
    definicion = models.CharField(max_length=100)
    diseno = models.CharField(max_length=100)
    observaciones = models.TextField(blank=True)

    class Meta:
        db_table = "control_flexo"
        verbose_name = "Control de flexografía"
        verbose_name_plural = "Controles de flexografía"

    def __str__(self):
        return f"Control de flexografía #{self.id}"


class ControlConfeccion(models.Model):
    class TipoSello(models.TextChoices):
        LATERAL = "lateral", "Lateral"
        FONDO = "fondo", "Fondo"
        FONDO_CON_PESTANA = "fondo_con_pestana", "Fondo con pestaña"

    class TipoTroquel(models.TextChoices):
        BOUTIQUE = "boutique", "Boutique"
        BOUTIQUE_REFORZADO = "boutique_reforzado", "Boutique reforzado"
        CAMISETA = "camiseta" , "Camiseta"
        BOLSA = "bolsa","Bolsa"
        ZIPER = "ziper", "Ziper"
    control_calidad = models.OneToOneField("calidad.ControlCalidad",on_delete=models.PROTECT,related_name="control_confeccion",)
    ancho_medido = models.DecimalField(max_digits=10,decimal_places=2,)
    largo_medido = models.DecimalField(max_digits=10,decimal_places=2,)
    fuelle_medido = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    tipo_sello = models.CharField(max_length=20, choices=TipoSello.choices)
    calidad_sello = models.PositiveBigIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
            ]
        )
    tipo_troquel = models.CharField(max_length=20, choices=TipoTroquel.choices)
    calidad_troquel = models.PositiveBigIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
            ]
        )
    pestana = models.BooleanField(default=True)
    apariencia = models.PositiveBigIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
            ]
        )
    observaciones = models.TextField(blank=True)

    class Meta:
        db_table = "control_confeccion"
        verbose_name = "Control de confección"
        verbose_name_plural = "Controles de confección"

    def __str__(self):
        return f"Control de confección #{self.id}"


class ControlRefilado(models.Model):

    control_calidad = models.OneToOneField("calidad.ControlCalidad",on_delete=models.PROTECT,related_name="control_refilado",)
    ancho_medido = models.DecimalField(max_digits=10,decimal_places=2,)
    diametro_medido = models.DecimalField(max_digits=10,decimal_places=2,)
    peso = models.DecimalField(max_digits=10,decimal_places=2,)
    calidad_bobinado = models.PositiveBigIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
            ]
        )
    alineacion = models.PositiveBigIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
            ]
        )
    tension = models.PositiveBigIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
            ]
        )
    observaciones = models.TextField(blank=True)

    class Meta:
        db_table = "control_refilado"
        verbose_name = "Control de refilado"
        verbose_name_plural = "Controles de refilado"

    def __str__(self):
        return f"Control de refilado #{self.id}"
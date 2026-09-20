from django.db import models
from django.conf import settings
# Create your models here.
class Notificacion(models.Model):

    class Prioridad(models.TextChoices):
        BAJA = "baja", "Baja"
        MEDIA = "media", "Media"
        ALTA = "alta", "Alta"

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="notificaciones",)
    tipo = models.CharField(max_length=50)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    prioridad = models.CharField(max_length=20,choices=Prioridad.choices,default=Prioridad.MEDIA,)
    entidad_tipo = models.CharField(max_length=100,blank=True,)
    entidad_id = models.PositiveIntegerField(null=True,blank=True,)
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True,)
    fecha_lectura = models.DateTimeField(null=True,blank=True,)
    class Meta:
        db_table = "notificacion"
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"{self.titulo} - {self.usuario}"
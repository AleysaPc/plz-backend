from django.db import models
from django.conf import settings


# Create your models here.
class Despacho(models.Model):

    class Estado(models.TextChoices):
        PROGRAMADO = "programado", "Programado"
        EN_RUTA = "en_ruta", "En ruta"
        ENTREGADO = "entregado", "Entregado"
        CANCELADO = "cancelado", "Cancelado"

    pedido = models.ForeignKey("comercial.Pedido", on_delete=models.PROTECT, related_name="despachos",)
    vehiculo = models.ForeignKey("recursos.Vehiculo",on_delete=models.PROTECT,related_name="despachos",)
    responsable = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="despachos_responsables",)
    numero = models.CharField(max_length=50,unique=True,)
    fecha_salida_programada = models.DateTimeField()
    fecha_salida_real = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=30,choices=Estado.choices,default=Estado.PROGRAMADO,)
    observaciones = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "despacho"
        verbose_name = "Despacho"
        verbose_name_plural = "Despachos"

    def __str__(self):
        return self.numero

class DespachoDetalle(models.Model):

    despacho = models.ForeignKey("despacho.Despacho",on_delete=models.PROTECT,related_name="detalles",)
    pedido_detalle = models.ForeignKey("comercial.PedidoDetalle",on_delete=models.PROTECT,related_name="despachos",)
    cantidad = models.DecimalField(max_digits=12,decimal_places=2,)
    unidad_medida = models.CharField(max_length=30,)
    observaciones = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "despacho_detalle"
        verbose_name = "Detalle de despacho"
        verbose_name_plural = "Detalles de despacho"

    def __str__(self):
        return f"{self.despacho} - Pedido #{self.pedido_detalle_id}"

class Entrega(models.Model):

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        ENTREGADA = "entregada", "Entregada"
        RECHAZADA = "rechazada", "Rechazada"

    despacho = models.ForeignKey("despacho.Despacho",on_delete=models.PROTECT,related_name="entregas",)
    cuenta_comercial = models.ForeignKey("comercial.CuentaComercial",on_delete=models.PROTECT,related_name="entregas",)
    fecha_entrega_programada = models.DateTimeField()
    fecha_entrega_real = models.DateTimeField(null=True, blank=True)
    hora_entrega = models.TimeField(null=True, blank=True)
    estado = models.CharField(max_length=30,choices=Estado.choices,default=Estado.PENDIENTE,)
    persona_recibe = models.CharField(max_length=150)
    observaciones = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "entrega"
        verbose_name = "Entrega"
        verbose_name_plural = "Entregas"

    def __str__(self):
        return f"Entrega #{self.id} - {self.cuenta_comercial}"
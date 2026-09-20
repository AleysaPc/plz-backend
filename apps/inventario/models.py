from django.db import models
from django.conf import settings
# Create your models here.
class Almacen(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=150)
    ubicacion = models.CharField(max_length=200, blank=True)
    descripcion = models.TextField(blank=True)
    estado = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "almacen"
        verbose_name = "Almacén"
        verbose_name_plural = "Almacenes"

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class MateriaPrima(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=150)
    unidad_medida = models.CharField(max_length=30)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "materia_prima"
        verbose_name = "Materia prima"
        verbose_name_plural = "Materias primas"

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class Pintura(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=150)
    color = models.CharField(max_length=100)
    tipo = models.CharField(max_length=100)
    unidad_medida = models.CharField(max_length=30)
    proveedor = models.CharField(max_length=150, blank=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pintura"
        verbose_name = "Pintura"
        verbose_name_plural = "Pinturas"

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class Inventario(models.Model):
    class Estado(models.TextChoices):
        DISPONIBLE = "disponible", "Disponible"
        AGOTADO = "agotado", "Agotado"
        BLOQUEADO = "bloqueado", "Bloqueado"
    almacen = models.ForeignKey("inventario.Almacen",on_delete=models.PROTECT,related_name="inventarios",)
    producto = models.ForeignKey("productos.Producto",on_delete=models.PROTECT,null=True,blank=True,related_name="inventarios",)
    materia_prima = models.ForeignKey("inventario.MateriaPrima",on_delete=models.PROTECT,null=True,blank=True,related_name="inventarios",)
    pintura = models.ForeignKey("inventario.Pintura",on_delete=models.PROTECT,null=True,blank=True,related_name="inventarios",)
    cantidad = models.DecimalField(max_digits=12,decimal_places=2,default=0,)
    unidad_medida = models.CharField(max_length=30)
    stock_minimo = models.DecimalField(max_digits=12,decimal_places=2,default=0,)
    stock_maximo = models.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True,)
    estado = models.CharField(max_length=30, choices=Estado.choices, default=Estado.DISPONIBLE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inventario"
        verbose_name = "Inventario"
        verbose_name_plural = "Inventarios"

class MovimientoInventario(models.Model):
    inventario = models.ForeignKey("inventario.Inventario",on_delete=models.PROTECT,related_name="movimientos",)
    lote_produccion = models.ForeignKey("produccion.LoteProduccion", on_delete=models.PROTECT, null=True, blank=True, related_name="movimientos_inventario")
    produccion_operacion = models.ForeignKey("produccion.ProduccionOperacion",on_delete=models.PROTECT,null=True,blank=True,related_name="movimientos_inventario",)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="movimientos_inventario",)
    despacho_detalle = models.ForeignKey("despacho.DespachoDetalle",on_delete=models.PROTECT,null=True,blank=True,related_name="movimientos_inventario",)
    tipo_movimiento = models.CharField(max_length=30)
    cantidad = models.DecimalField(max_digits=12,decimal_places=2,)
    fecha = models.DateTimeField()
    motivo = models.CharField(max_length=200)
    observaciones = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "movimiento_inventario"
        verbose_name = "Movimiento de inventario"
        verbose_name_plural = "Movimientos de inventario"
        ordering = ["-fecha"]

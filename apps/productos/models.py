from django.db import models
from django.contrib.postgres.fields import ArrayField
#Es para determinar si es bobina o bolsa 
class ProductoCategoria(models.Model):
    nombre = models.CharField(max_length=100,unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "producto_categoria"
        verbose_name = "Categoría de producto"
        verbose_name_plural = "Categorías de productos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

class Producto(models.Model):

    class UnidadMedida(models.TextChoices):
        UNIDAD = "unidad", "Unidad"
        FAJO = "fajo", "Fajo"
        METRO = "metro", "Metro"

    categoria = models.ForeignKey("productos.ProductoCategoria",on_delete=models.PROTECT,related_name="productos",)
    codigo = models.CharField(max_length=50,unique=True,)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True,)
    unidad_medida = models.CharField(max_length=20, choices=UnidadMedida.choices,)
    pais_origen = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)

    class Meta:
        db_table = "producto"
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["codigo"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class ProductoVersion(models.Model):
    class Estado(models.TextChoices):
        ACTIVA = "activa", "Activa"
        INACTIVA = "inactiva", "Inactiva"

    producto = models.ForeignKey("productos.Producto", on_delete=models.PROTECT, related_name="versiones",)
    material = models.CharField(max_length=100)
    apto_alimento = models.BooleanField(default=False,)
    micraje = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    color_bolsa = models.CharField(max_length=100, blank=True)
    impresion = models.BooleanField(default=False,)
    color_impresion = ArrayField(base_field=models.CharField(max_length=50), default=list, blank=True,)
    tipo_impresion = models.CharField(max_length=100, blank=True)
    numero_version = models.PositiveIntegerField()
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.ACTIVA)
    observaciones = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "producto_version"
        verbose_name = "Versión de producto"
        verbose_name_plural= "Versiones de producto"

        constraints = [
            models.UniqueConstraint(
                fields=["producto", "numero_version"],
                name = "unique_producto_version",
            )
        ]
        ordering = ["producto", "-numero_version"]

    def __str__(self):
        return f"{self.producto} - Versión {self.numero_version}"

class EspecificacionBolsa(models.Model):
    #OneToOneField porque para una vesrsion concreta dle producto se requiere una sola especificacion de bolsa 
    producto_version = models.OneToOneField("productos.ProductoVersion",on_delete=models.PROTECT, related_name="especificacion_bolsa",)
    ancho_doblado = models.DecimalField(max_digits=10,decimal_places=2,)
    ancho_desdoblado = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    largo_doblado = models.DecimalField(max_digits=10,decimal_places=2,)
    largo_desdoblado = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    fuelle = models.BooleanField(default=False,)
    fuelle_izquierdo = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    fuelle_derecho = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    fuelle_inferior = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    fuelle_superior = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    tipo_troquel = models.CharField(max_length=100,blank=True,)
    tipo_sello = models.CharField(max_length=100,blank=True,)
    pestana = models.CharField(max_length=100,blank=True,)
    otras_caracteristicas = models.TextField(blank=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)

    class Meta:
        db_table = "especificacion_bolsa"
        verbose_name = "Especificación de bolsa"
        verbose_name_plural = "Especificaciones de bolsa"

    def __str__(self):
        return f"Especificación - {self.producto_version}"

class EspecificacionBobina(models.Model):
    producto_version = models.OneToOneField("productos.ProductoVersion", on_delete=models.PROTECT, related_name="especificacion_bobina",)
    ancho = models.DecimalField(max_digits=10,decimal_places=2,)
    diametro = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    diametro_nucleo = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    tipo_nucleo = models.CharField(max_length=100,blank=True,)
    peso = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    longitud = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True,)
    otras_caracteristicas = models.TextField(blank=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        db_table = "especificacion_bobina"
        verbose_name = "Especificación de bobina"
        verbose_name_plural = "Especificaciones de bobina"

    def __str__(self):
        return f"Especificación - {self.producto_version}"

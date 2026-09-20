from django.db import models
from django.contrib.postgres.fields import ArrayField

class Equipo(models.Model):

    class TipoEquipo(models.TextChoices):
        MAQUINARIA = "maquinaria", "Maquinaria"
        VEHICULO = "vehiculo", "Vehículo"
        INFRAESTRUCTURA = "infraestructura", "Infraestructura"

    class Estado(models.TextChoices):
        OPERATIVO = "operativo", "Operativo"
        MANTENIMIENTO = "mantenimiento", "Mantenimiento"
        FUERA_SERVICIO = "fuera_servicio", "Fuera de servicio"

    codigo = models.CharField(max_length=50,unique=True,)
    nombre = models.CharField(max_length=150,)
    tipo_equipo = models.CharField(max_length=30, choices=TipoEquipo.choices,)
    marca = models.CharField(max_length=100,blank=True,)
    modelo = models.CharField(max_length=100,blank=True,)
    estado = models.CharField(max_length=30,choices=Estado.choices,default=Estado.OPERATIVO,)
    ubicacion = models.CharField(max_length=150,blank=True,)
    class Meta:
        db_table = "equipo"
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"
        ordering = ["codigo"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class Maquinaria(models.Model):

    equipo = models.OneToOneField("recursos.Equipo",on_delete=models.PROTECT,related_name="maquinaria",)
    area_produccion = models.ForeignKey("recursos.AreaProduccion",on_delete=models.PROTECT,related_name="maquinarias",)
    descripcion = models.TextField(blank=True,)
    observacion = models.TextField(blank=True,)
    class Meta:
        db_table = "maquinaria"
        verbose_name = "Maquinaria"
        verbose_name_plural = "Maquinarias"

    def __str__(self):
        return f"Maquinaria - {self.equipo}"

class Vehiculo(models.Model):

    class TipoVehiculo(models.TextChoices):
        CAMION = "camion", "Camión"
        CAMIONETA = "camioneta", "Camioneta"
        FURGON = "furgon", "Furgón"
        OTRO = "otro", "Otro"

    class Estado(models.TextChoices):
        OPERATIVO = "operativo", "Operativo"
        MANTENIMIENTO = "mantenimiento", "Mantenimiento"
        FUERA_SERVICIO = "fuera_servicio", "Fuera de servicio"

    equipo = models.OneToOneField("recursos.Equipo",on_delete=models.PROTECT,related_name="vehiculo",)
    nombre = models.CharField(max_length=100,)
    placa = models.CharField(max_length=20,unique=True,)
    marca = models.CharField(max_length=100,blank=True,)
    modelo = models.CharField(max_length=100,blank=True,)
    capacidad_carga = models.DecimalField(max_digits=10,decimal_places=2,)
    tipo_vehiculo = models.CharField(max_length=30,choices=TipoVehiculo.choices,)
    estado = models.CharField(max_length=30,choices=Estado.choices,default=Estado.OPERATIVO,)
    observacion = models.TextField(blank=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        db_table = "vehiculo"
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"

    def __str__(self):
        return f"{self.placa} - {self.tipo_vehiculo}"

class AreaProduccion(models.Model):
    nombre = models.CharField(max_length=100,unique=True,)
    descripcion = models.TextField(blank=True,)

    class Meta:
        db_table = "area_produccion"
        verbose_name = "Área de producción"
        verbose_name_plural = "Áreas de producción"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

class CapacidadExtrusion(models.Model):
    class Material(models.TextChoices):
        PEAD = "PEAD", "PEAD"
        PEBD = "PEBD", "PEBD"
        PP = "PP", "PP"

    maquinaria = models.ForeignKey("recursos.Maquinaria",on_delete=models.PROTECT,related_name="capacidades_extrusion",)
    material = models.CharField(max_length=10,choices=Material.choices,)
    ancho_min = models.DecimalField(max_digits=10,decimal_places=2,)
    ancho_max = models.DecimalField(max_digits=10,decimal_places=2,)
    micronaje_min = models.DecimalField(max_digits=8,decimal_places=2,)
    micronaje_max = models.DecimalField(max_digits=8,decimal_places=2,)
    diametro_min = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    diametro_max = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    peso_min = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    peso_max = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    kg_h = models.DecimalField(max_digits=10,decimal_places=2,)
    capas = models.PositiveIntegerField()
    fuelle_minimo = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    fuelle_maximo = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    observaciones = models.TextField(blank=True,)
    class Meta:
        db_table = "capacidad_extrusion"
        verbose_name = "Capacidad de extrusión"
        verbose_name_plural = "Capacidades de extrusión"

    def __str__(self):
        return f"Capacidad de extrusión - {self.maquinaria}"

class CapacidadFlexografia(models.Model):

    maquinaria = models.OneToOneField("recursos.Maquinaria",on_delete=models.PROTECT,related_name="capacidades_flexografia",)
    ancho_min = models.DecimalField(max_digits=10,decimal_places=2,)
    ancho_max = models.DecimalField(max_digits=10,decimal_places=2,)
    colores_min = models.PositiveIntegerField()
    colores_max = models.PositiveIntegerField()
    puede_anverso = models.BooleanField(default=False,)
    puede_reverso = models.BooleanField(default=False,)
    puede_ambas_caras = models.BooleanField(default=False,)
    puede_degradado = models.BooleanField(default=False)
    puede_trameado = models.BooleanField(default=False)
    velocidad_m_min = models.DecimalField(max_digits=10,decimal_places=2,)
    observaciones = models.TextField(blank=True,)
    class Meta:
        db_table = "capacidad_flexografia"
        verbose_name = "Capacidad de flexografía"
        verbose_name_plural = "Capacidades de flexografía"

    def __str__(self):
        return f"Capacidad de flexografía - {self.maquinaria}"  
class CapacidadConfeccion(models.Model):
    class Material(models.TextChoices):
        PEAD = "PEAD", "PEAD"
        PEBD = "PEBD", "PEBD"
        PP = "PP", "PP"

    maquinaria = models.ForeignKey("recursos.Maquinaria",on_delete=models.PROTECT,related_name="capacidades_confeccion",)
    materiales = ArrayField(base_field=models.CharField(max_length=10,choices=Material.choices,),default=list,blank=True,)
    tipo_sello = models.CharField(max_length=100,)
    tipo_troquel = models.CharField(max_length=100,)
    acabado_especial = models.CharField(max_length=100,blank=True)
    #Capacidad de entrada:bobina
    bobina_ancho_min = models.DecimalField(max_digits=10, decimal_places=2,)
    bobina_ancho_max = models.DecimalField(max_digits=10, decimal_places=2,)
    #Capacidad de salida: Producto terminado
    producto_ancho_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    producto_ancho_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    largo_min = models.DecimalField(max_digits=10,decimal_places=2,)
    largo_max = models.DecimalField(max_digits=10,decimal_places=2,)
    fuelle_min = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    fuelle_max = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    velocidad_unidad_min = models.DecimalField(max_digits=10,decimal_places=2,)
    observaciones = models.TextField(blank=True,)
    class Meta:
        db_table = "capacidad_confeccion"
        verbose_name = "Capacidad de confección"
        verbose_name_plural = "Capacidades de confección"

    def __str__(self):
        return f"Capacidad de confección - {self.maquinaria}"

class CapacidadRefilado(models.Model):
    maquinaria = models.OneToOneField("recursos.Maquinaria", on_delete=models.PROTECT, related_name="capacidades_refilado",)
    ancho_entrada_min = models.DecimalField(max_digits=10,decimal_places=2,)
    ancho_entrada_max = models.DecimalField(max_digits=10,decimal_places=2,)
    ancho_salida_min = models.DecimalField(max_digits=10,decimal_places=2,)
    ancho_salida_max = models.DecimalField(max_digits=10,decimal_places=2,)
    velocidad_m_min = models.DecimalField(max_digits=10,decimal_places=2,)
    observaciones = models.TextField(blank=True,)
    class Meta:
        db_table = "capacidad_refilado"
        verbose_name = "Capacidad de refilado"
        verbose_name_plural = "Capacidades de refilado"

    def __str__(self):
        return f"Capacidad de refilado - {self.maquinaria}"

class Anilla(models.Model):

    capacidad_extrusion = models.ForeignKey("recursos.CapacidadExtrusion",on_delete=models.PROTECT,related_name="anillas",)
    codigo = models.CharField(max_length=50,unique=True,)
    nombre = models.CharField(max_length=100,)
    diametro = models.DecimalField(max_digits=10,decimal_places=2,)
    ancho_min = models.DecimalField(max_digits=10,decimal_places=2,)
    ancho_max = models.DecimalField(max_digits=10,decimal_places=2,)
    estado = models.CharField(max_length=30,)
    observaciones = models.TextField(blank=True,)
    descripcion = models.TextField(blank=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        db_table = "anilla"
        verbose_name = "Anilla"
        verbose_name_plural = "Anillas"

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class Rodillo(models.Model):

    capacidad_flexografia = models.ForeignKey("recursos.CapacidadFlexografia",on_delete=models.PROTECT,related_name="rodillos",)
    codigo = models.CharField(max_length=50,unique=True,)
    identificacion = models.CharField(max_length=100,)
    medida = models.DecimalField(max_digits=10,decimal_places=2,)
    unidad = models.CharField(max_length=20,)
    diametro = models.DecimalField(max_digits=10,decimal_places=2,)
    ancho = models.DecimalField(max_digits=10,decimal_places=2,)
    circunferencia = models.DecimalField(max_digits=10,decimal_places=2,)
    desarrollo = models.DecimalField(max_digits=10,decimal_places=2,)
    observaciones = models.TextField(blank=True,)
    estado = models.CharField(max_length=30,)
    class Meta:
        db_table = "rodillo"
        verbose_name = "Rodillo"
        verbose_name_plural = "Rodillos"

    def __str__(self):
        return f"{self.codigo} - {self.identificacion}"

class Cliche(models.Model):

    diseno = models.ForeignKey("recursos.Diseno",on_delete=models.PROTECT,related_name="cliches",)
    maquinaria = models.ForeignKey("recursos.Maquinaria",on_delete=models.PROTECT,related_name="cliches",)
    codigo = models.CharField(max_length=50,unique=True,)
    descripcion = models.TextField(blank=True,)
    grosor_min = models.DecimalField(max_digits=8,decimal_places=2,null=True,blank=True,)
    grosor_max = models.DecimalField(max_digits=8,decimal_places=2,null=True,blank=True,)
    ubicacion = models.CharField(max_length=150,blank=True,)
    estado = models.CharField(max_length=30,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        db_table = "cliche"
        verbose_name = "Cliché"
        verbose_name_plural = "Clichés"

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

class ClicheParte(models.Model):
    cliche = models.ForeignKey("recursos.Cliche", on_delete=models.PROTECT, related_name="partes",)
    numero_piezas = models.PositiveIntegerField()
    colores = ArrayField(base_field=models.CharField(max_length=50),default=list, blank=True)
    descripcion = models.TextField(blank=True,)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = "cliche_parte"
        verbose_name = "Parte de cliché"
        verbose_name_plural = "Partes de cliché"

    def __str__(self):
        return f"Parte {self.id} - {self.cliche}"

class Diseno(models.Model):

    especificacion_producto_solicitado = models.ForeignKey("comercial.EspecificacionProductoSolicitado", on_delete=models.PROTECT, related_name="disenos") 
    nombre = models.CharField(max_length=200,)
    descripcion = models.TextField(blank=True,)
    archivo = models.FileField(upload_to="disenos/", blank=True, null=True,)
    version = models.PositiveIntegerField()
    estado = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        db_table = "diseno"
        verbose_name = "Diseño"
        verbose_name_plural = "Diseños"
        ordering = ["nombre", "-version"]

    def __str__(self):
        return f"{self.nombre} - V{self.version}"

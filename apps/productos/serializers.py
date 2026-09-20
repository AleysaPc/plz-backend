from rest_framework import serializers
from apps.productos.models import ProductoCategoria, Producto, ProductoVersion, EspecificacionBobina, EspecificacionBolsa

class ProductoCategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoCategoria
        fields = [
            "id",
            "nombre",
            "descripcion",
            "activo",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at2",
        ]

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = [
            "id",
            "categoria",
            "codigo",
            "nombre",
            "descripcion",
            "unidad_medida",
            "pais_origen",
            "estado",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_att",
        ]

class ProductoVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoVersion
        fields = [
            "id",
            "producto",
            "material",
            "apto_alimento",
            "micraje",
            "color_bolsa",
            "impresion",
            "color_impresion",
            "tipo_impresion",
            "numero_version",
            "estado",
            "observaciones",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

class EspecificacionBolsaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EspecificacionBolsa
        fields = [
           "id",
            "producto_version",
            "ancho_doblado",
            "ancho_desdoblado",
            "largo_doblado",
            "largo_desdoblado",
            "fuelle",
            "fuelle_izquierdo",
            "fuelle_derecho",
            "fuelle_inferior",
            "fuelle_superior",
            "tipo_troquel",
            "tipo_sello",
            "pestana",
            "otras_caracteristicas",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

class EspecificacionBobinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EspecificacionBobina
        fields = [
            "id",
            "producto_version",
            "ancho",
            "diametro",
            "diametro_nucleo",
            "tipo_nucleo",
            "peso",
            "otras_caracteristicas",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]
        
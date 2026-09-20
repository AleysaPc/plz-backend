from rest_framework import serializers
from apps.recursos.models import (
    Equipo,
    Maquinaria,
    Vehiculo,
    AreaProduccion,
    CapacidadExtrusion,
    CapacidadFlexografia,
    CapacidadConfeccion,
    CapacidadRefilado,
    Anilla,
    Rodillo,
    Cliche,
    ClicheParte,
    Diseno,
)

class EquipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipo
        fields = [
            "id",
            "codigo",
            "nombre",
            "tipo_equipo",
            "marca",
            "modelo",
            "estado",
            "ubicacion",
        ]

class AreaProduccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaProduccion
        fields = [
            "id",
            "nombre",
            "descripcion",
        ]

class MaquinariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maquinaria
        fields = [
            "id",
            "equipo",
            "area_produccion",
            "descripcion",
            "observacion",
        ]
class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields =[
            "id",
            "equipo",
            "nombre",
            "placa",
            "marca",
            "modelo",
            "capacidad_carga",
            "tipo_vehiculo",
            "estado",
            "observacion",
            "created_at",
            "updated_at"
        ]


"""Serializadores que corresponden a la capacidad tecnica que el ER define
para extrusion, flexografia, confeccion y refilado
"""
class CapacidadExtrusionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapacidadExtrusion
        fields = [
            "id",
            "maquinaria",
            "material",
            "ancho_min",
            "ancho_max",
            "micronaje_min",
            "micronaje_max",
            "diametro_min",
            "diametro_max",
            "peso_min",
            "peso_max",
            "kg_h",
            "capas",
            "fuelle_minimo",
            "fuelle_maximo",
            "observaciones",
        ]

class CapacidadFlexografiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapacidadFlexografia
        fields = [
             "id",
            "maquinaria",
            "ancho_min",
            "ancho_max",
            "colores_min",
            "colores_max",
            "puede_anverso",
            "puede_reverso",
            "puede_ambas_caras",
            "velocidad_m_min",
            "observaciones"
        ]
class CapacidadConfeccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapacidadConfeccion
        fields = [
            "id",
            "maquinaria",
            "materiales",
            "tipo_sello",
            "tipo_troquel",
            "ancho_min",
            "ancho_max",
            "largo_min",
            "largo_max",
            "fuelle_min",
            "fuelle_max",
            "velocidad_unidad_min",
            "observaciones",
        ]

class CapacidadRefiladoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapacidadRefilado
        fields =  [
            "id",
            "maquinaria",
            "ancho_entrada_min",
            "ancho_entrada_max",
            "ancho_salida_min",
            "ancho_salida_max",
            "velocidad_m_min",
            "observaciones",
        ]

class AnillaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anilla
        fields = [
            "id",
            "capacidad_extrusion",
            "codigo",
            "nombre",
            "diametro",
            "ancho_min",
            "ancho_max",
            "estado",
            "observaciones",
            "descripcion",
            "created_at",
            "updated_at",
        ]
class RodilloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rodillo
        fields = [
            "id",
            "capacidad_flexografia",
            "codigo",
            "identificacion",
            "medida",
            "unidad",
            "diametro",
            "ancho",
            "circunferencia",
            "desarrollo",
            "observaciones",
            "estado",
        ]

class ClicheSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliche
        fields = [
             "id",
            "diseno",
            "maquinaria",
            "codigo",
            "descripcion",
            "grosor_min",
            "grosor_max",
            "ubicacion",
            "estado",
            "created_at",
            "updated_at",
        ]

class ClicheParteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClicheParte
        fields = [
            "id",
            "cliche",
            "numero_piezas",
            "colores",
            "descripcion",
            "estado",
        ]

class DisenoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diseno
        fields = [
            "id",
            "especificacion_producto_solicitado",
            "nombre",
            "descripcion",
            "archivo",
            "version",
            "estado",
            "created_at",
            "updated_at",
        ]
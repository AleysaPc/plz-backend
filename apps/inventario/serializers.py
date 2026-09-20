from rest_framework import serializers
from apps.inventario.models import (
    Almacen,
    MateriaPrima,
    Pintura,
    Inventario,
    MovimientoInventario
)
class AlmacenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Almacen
        fields = "__all__"
class MateriaPrimaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MateriaPrima
        fields = "__all__"
class PinturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pintura
        fields = "__all__"
class InventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventario
        fields = "__all__"

    # Antes de guardar, verificamos que el inventario
    # corresponda a un solo tipo de elemento.
    def validate(self, attrs):
        producto = attrs.get("producto")
        materia_prima = attrs.get("materia_prima")
        pintura = attrs.get("pintura")

        elementos = [
            producto,
            materia_prima,
            pintura,
        ]
        cantidad_asignada = sum (
            elemento is not None
            for elemento in elementos
        )
        if cantidad_asignada !=1:
            raise serializers.ValidationError(
                "El inventario debe estar asociado"
                "a un producto, una materia prima o una pintura"
            )
        return attrs
    
class MovimientoInventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimientoInventario
        fields = "__all__"
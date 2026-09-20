from rest_framework import serializers
from apps.produccion.models import(
    OrdenProduccion,
    OrdenProduccionDetalle,
    PlanProduccion,
    PlanDetalle,
    ColaOperacion,
    RutaProduccion,
    PasoRuta,
    RutaOperacion,
    OrdenRuta,
    ProduccionOperacion,
    Dosificacion,
    ConsumoProduccion,
    TransferenciaProduccion,
    ResultadoProduccion,
)
class OrdenProduccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrdenProduccion
        fields = "__all__"
        read_only_fields = ["id","created_at","updated_at"]
class OrdenProduccionDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrdenProduccionDetalle
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
class PlanProduccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanProduccion
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
class PlanDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanDetalle
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
class ColaOperacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColaOperacion
        fields = "__all__"
        read_only_fields = ["id"]
class RutaProduccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RutaProduccion
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
class PasoRutaSerializer(serializers.ModelSerializer):
    class Meta: 
        model = PasoRuta
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
class RutaOperacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RutaOperacion
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
class OrdenRutaSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrdenRuta
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
class ProduccionOperacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProduccionOperacion
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
class DosificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dosificacion
        fields = "__all__"
        read_only_fields = ["id"]
class ConsumoProduccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsumoProduccion
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

class TransferenciaProduccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferenciaProduccion
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

class ResultadoProduccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultadoProduccion
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]
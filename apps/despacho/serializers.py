from rest_framework import serializers
from apps.despacho.models import (
    Despacho,
    DespachoDetalle,
    Entrega,
)
class DespachoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Despacho
        fields = "__all__"
class DespachoDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DespachoDetalle
        fields = "__all__"
class EntregaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entrega
        fields = "__all__"

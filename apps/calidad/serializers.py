from rest_framework import serializers
from apps.calidad.models import (
    ControlCalidad,
    ControlExtrusion,
    ControlFlexografia,
    ControlConfeccion,
    ControlRefilado
) 
class ControlCalidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ControlCalidad
        fields = "__all__"
class ControlExtrusionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ControlExtrusion
        fields = "__all__"
class ControlFlexografiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ControlFlexografia
        fields = "__all__"
class ControlConfeccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ControlConfeccion
        fields = "__all__"
class ControlRefiladoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ControlRefilado
        fields = "__all__"
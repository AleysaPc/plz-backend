from rest_framework import serializers
from apps.viabilidad.models import(
 EvaluacionComercial,
 EvaluacionViabilidad,
 EvaluacionProceso,
 ResultadoViabilidad,   
)

class EvaluacionComercialSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluacionComercial
        fields = "__all__"

class EvaluacionViabildadSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluacionViabilidad
        fields = "__all__"

class EvaluacionProcesoSerialzer(serializers.ModelSerializer):
    class Meta:
        model = EvaluacionProceso
        fields = "__all__"
class ResultadoViabilidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultadoViabilidad
        fields = "__all__"
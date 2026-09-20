from django.shortcuts import render
from rest_framework import viewsets
from apps.calidad.models import (
    ControlCalidad,
    ControlExtrusion,
    ControlFlexografia,
    ControlConfeccion,
    ControlRefilado,
)
from apps.calidad.serializers import (
    ControlCalidadSerializer,
    ControlExtrusionSerializer,
    ControlConfeccionSerializer,
    ControlFlexografiaSerializer,
    ControlRefiladoSerializer
)
class ControlCalidadViewSet(viewsets.ModelViewSet):
    queryset = ControlCalidad.objects.all()
    serializer_class = ControlCalidadSerializer
class ControlExtrusionViewSet(viewsets.ModelViewSet):
    queryset = ControlExtrusion.objects.all()
    serializer_class = ControlExtrusionSerializer
class ControlFlexografiaViewSet(viewsets.ModelViewSet):
    queryset = ControlFlexografia.objects.all()
    serializer_class = ControlFlexografiaSerializer
class ControlConfeccionViewSet(viewsets.ModelViewSet):
    queryset = ControlConfeccion.objects.all()
    serializer_class = ControlConfeccionSerializer
class ControlRefiladoViewSet(viewsets.ModelViewSet):
    queryset = ControlRefilado.objects.all()
    serializer_class = ControlRefiladoSerializer
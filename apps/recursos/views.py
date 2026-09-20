from django.shortcuts import render
from rest_framework import viewsets

#Importamos los modelos 
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
    ClicheParte,
    Cliche,
    Diseno,
)
#Importamos los serializadores
from apps.recursos.serializers import (
    EquipoSerializer,
    VehiculoSerializer,
    MaquinariaSerializer,
    AreaProduccionSerializer,
    CapacidadExtrusionSerializer,
    CapacidadFlexografiaSerializer,
    CapacidadConfeccionSerializer,
    CapacidadRefiladoSerializer,
    AnillaSerializer,
    RodilloSerializer,
    ClicheSerializer,
    ClicheParteSerializer,
    DisenoSerializer,
)

class EquipoViewSet(viewsets.ModelViewSet):
    queryset = Equipo.objects.all()
    serializer_class = EquipoSerializer
class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer
class MaquinariaViewSet(viewsets.ModelViewSet):
    queryset = Maquinaria.objects.all()
    serializer_class = MaquinariaSerializer
class AreaProduccionViewSet(viewsets.ModelViewSet):
    queryset = AreaProduccion.objects.all()
    serializer_class = AreaProduccionSerializer
class CapacidadExtrusionViewSet(viewsets.ModelViewSet):
    queryset = CapacidadExtrusion.objects.all()
    serializer_class = CapacidadExtrusionSerializer
class CapacidadFlexografiaViewSet(viewsets.ModelViewSet):
    queryset = CapacidadFlexografia.objects.all()
    serializer_class = CapacidadFlexografiaSerializer
class CapacidadConfeccionViewSet(viewsets.ModelViewSet):
    queryset = CapacidadConfeccion.objects.all()
    serializer_class = CapacidadConfeccionSerializer
class CapacidadRefiladoViewSet(viewsets.ModelViewSet):
    queryset = CapacidadRefilado.objects.all()
    serializer_class = CapacidadRefiladoSerializer
class AnillaViewSet(viewsets.ModelViewSet):
    queryset = Anilla.objects.all()
    serializer_class = AnillaSerializer
class RodilloViewSet(viewsets.ModelViewSet):
    queryset = Rodillo.objects.all()
    serializer_class = RodilloSerializer
class ClicheViewSet(viewsets.ModelViewSet):
    queryset = Cliche.objects.all()
    serializer_class = ClicheSerializer
class ClicheParteViewSet(viewsets.ModelViewSet):
    queryset = ClicheParte.objects.all()
    serializer_class = ClicheParteSerializer
class DisenoViewSet(viewsets.ModelViewSet):
    queryset = Diseno.objects.all()
    serializer_class = DisenoSerializer




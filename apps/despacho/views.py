from django.shortcuts import render
from rest_framework import viewsets
from apps.despacho.models import (
    Entrega,
    Despacho,
    DespachoDetalle
)
from apps.despacho.serializers import (
    DespachoSerializer,
    DespachoDetalleSerializer,
    EntregaSerializer
)
class DespachoViewSet(viewsets.ModelViewSet):
    queryset = Despacho.objects.select_related(
        "pedido",
        "vehiculo",
        "responsable",
    ).all()
    serializer_class = DespachoSerializer
class DespachoDetalleViewSet(viewsets.ModelViewSet):
    queryset = DespachoDetalle.objects.all()
    serializer_class = DespachoDetalleSerializer
class EntregaViewSet(viewsets.ModelViewSet):
    queryset = Entrega.objects.all()
    serializer_class = EntregaSerializer
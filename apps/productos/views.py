from django.shortcuts import render
from rest_framework import viewsets
#Las Views son las encargadas de recibir las solicitudes de la API,
#procesar la petición usando los modelos y serializers, y devolver una 
#respuesta al cliente. 

from apps.productos.models import (
    ProductoCategoria,
    Producto,
    ProductoVersion,
    EspecificacionBobina,
    EspecificacionBolsa,
)
from apps.productos.serializers import (
    ProductoCategoriaSerializer,
    ProductoSerializer,
    ProductoVersionSerializer,
    EspecificacionBobinaSerializer,
    EspecificacionBolsaSerializer
)
#DRF automaticamente nos proporciona las operaciones CRUD

class ProductoCategoriaViewSet(viewsets.ModelViewSet):
    queryset = ProductoCategoria.objects.all()
    serializer_class = ProductoCategoriaSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

class ProductoVersionViewSet(viewsets.ModelViewSet):
    queryset = ProductoVersion.objects.all()
    serializer_class = ProductoVersionSerializer

class EspecificacionBolsaViewSet(viewsets.ModelViewSet):
    queryset = EspecificacionBolsa.objects.all()
    serializer_class = EspecificacionBolsaSerializer

class EspecificacionBobinaViewSet(viewsets.ModelViewSet):
    queryset = EspecificacionBobina.objects.all()
    serializer_class = EspecificacionBobinaSerializer

     





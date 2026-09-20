from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.inventario.services.inventario_service import (
    registrar_entrada_produccion,
)
from apps.inventario.models import (
        Almacen,
        MateriaPrima,
        Pintura,
        Inventario,
        MovimientoInventario
)
from apps.inventario.serializers import (
    AlmacenSerializer,
    MateriaPrimaSerializer,
    PinturaSerializer,
    InventarioSerializer,
    MovimientoInventarioSerializer,
)
class AlmacenViewSet(viewsets.ModelViewSet):
    queryset = Almacen.objects.all()
    serializer_class = AlmacenSerializer
    permission_classes = [IsAuthenticated]

class MateriaPrimaViewSet(viewsets.ModelViewSet):
    queryset = MateriaPrima.objects.all()
    serializer_class = MateriaPrimaSerializer
    permission_classes = [IsAuthenticated]
class PinturaViewSet(viewsets.ModelViewSet):
    queryset = Pintura.objects.all()
    serializer_class = PinturaSerializer
    permission_classes = [IsAuthenticated]

class InventarioViewSet(viewsets.ModelViewSet):
    queryset = Inventario.objects.select_related(
        "almacen",
        "producto",
        "materia_prima",
        "pintura",
    )
    serializer_class = InventarioSerializer
    @action(
    detail=False,
    methods=["post"],
    url_path="entrada-produccion",
    )
    def entrada_produccion(self, request):
        try:
            resultado = registrar_entrada_produccion(
                lote_produccion_id=request.data.get(
                    "lote_produccion_id"
                ),
                almacen_id=request.data.get(
                    "almacen_id"
                ),
                usuario=request.user,
                motivo=request.data.get(
                    "motivo",
                    "Ingreso de producción",
                ),
                observaciones=request.data.get(
                    "observaciones",
                    "",
                ),
            )

            if resultado["exito"]:
                return Response(
                    resultado,
                    status=status.HTTP_201_CREATED,
                )

            return Response(
                resultado,
                status=status.HTTP_400_BAD_REQUEST,
            )

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
class MovimientoInventarioViewSet(viewsets.ModelViewSet):
    queryset = MovimientoInventario.objects.select_related(
        "inventario",
        "produccion_operacion",
        "usuario",
        "despacho_detalle"
    ).all()
    serializer_class = MovimientoInventarioSerializer
    permission_classes = [IsAuthenticated]

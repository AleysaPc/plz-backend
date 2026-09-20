from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.produccion.models import (
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
from apps.calidad.models import (
    ControlCalidad,
)
from apps.produccion.serializers import (
    OrdenProduccionSerializer,
    OrdenProduccionDetalleSerializer,
    PlanProduccionSerializer,
    PlanDetalleSerializer,
    ColaOperacionSerializer,
    RutaProduccionSerializer,
    PasoRutaSerializer,
    RutaOperacionSerializer,
    OrdenRutaSerializer,
    ProduccionOperacionSerializer,
    DosificacionSerializer,
    ConsumoProduccionSerializer,
    TransferenciaProduccionSerializer,
    ResultadoProduccionSerializer,
)
from apps.calidad.serializers import (
    ControlCalidadSerializer,
)

from apps.produccion.services.ejecucion_produccion_service import (
    iniciar_operacion,
    registrar_produccion,
    registrar_scrap,
    finalizar_operacion,
)

from apps.produccion.services.control_produccion_service import (
    crear_control_calidad,
    completar_control_calidad,
    obtener_controles_operacion,
)
from apps.produccion.services.transferencia_produccion_service import (
    aprobar_transferencia,
    crear_transferencia,
    rechazar_transferencia,
    completar_transferencia,
)

from apps.viabilidad.services.produccion_service import (
    crear_orden_produccion_desde_viabilidad,
    crear_ruta_produccion,
    iniciar_produccion,
)

from apps.produccion.services.orden_produccion_service import (
    completar_orden_produccion,
)

# ============================================================
# CRUD
# ============================================================

class OrdenProduccionViewSet(viewsets.ModelViewSet):
    queryset = OrdenProduccion.objects.all()
    serializer_class = OrdenProduccionSerializer
    permission_classes = [IsAuthenticated]

    @action(
        detail=False,
        methods=["post"],
        url_path="crear-desde-pedido",
    )
    def crear_desde_pedido(self, request):
        try:
            resultado = crear_orden_produccion_desde_viabilidad(
                evaluacion_viabilidad_id=request.data.get(
                    "evaluacion_viabilidad_id"
                ),
                usuario=request.user,
                cantidad_planificada=request.data.get(
                    "cantidad_planificada"
                ),
                pedido_detalle_id=request.data.get(
                    "pedido_detalle_id"
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
    @action(
        detail=True, methods=["post"], url_path="crear-ruta")
    def crear_ruta(self, request, pk=None):
        try:
            resultado = crear_ruta_produccion(
                orden_produccion_id=pk,
                usuario=request.user,
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
    @action(
    detail=True,
    methods=["post"],            
    url_path="iniciar",
    )
    def iniciar(self, request, pk=None):
        try:
            resultado = iniciar_produccion(
                    orden_produccion_id=pk,
                    usuario=request.user,
                    observaciones=request.data.get(
                        "observaciones",
                        "",
                    ),
                )

            if resultado["exito"]:
                return Response(
                    resultado,
                    status=status.HTTP_200_OK,
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
    @action(
    detail=True,
    methods=["post"],
    url_path="completar",
    )
    def completar(self, request, pk=None):
        try:
            resultado = completar_orden_produccion(
                orden_produccion_id=pk,
                usuario=request.user,
            )

            if resultado["exito"]:
                return Response(
                    resultado,
                    status=status.HTTP_200_OK,
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
class OrdenProduccionDetalleViewSet(viewsets.ModelViewSet):
    queryset = OrdenProduccionDetalle.objects.all()
    serializer_class = OrdenProduccionDetalleSerializer
    permission_classes = [IsAuthenticated]


class PlanProduccionViewSet(viewsets.ModelViewSet):
    queryset = PlanProduccion.objects.all()
    serializer_class = PlanProduccionSerializer
    permission_classes = [IsAuthenticated]


class PlanDetalleViewSet(viewsets.ModelViewSet):
    queryset = PlanDetalle.objects.all()
    serializer_class = PlanDetalleSerializer
    permission_classes = [IsAuthenticated]


class ColaOperacionViewSet(viewsets.ModelViewSet):
    queryset = ColaOperacion.objects.all()
    serializer_class = ColaOperacionSerializer
    permission_classes = [IsAuthenticated]


class RutaProduccionViewSet(viewsets.ModelViewSet):
    queryset = RutaProduccion.objects.all()
    serializer_class = RutaProduccionSerializer
    permission_classes = [IsAuthenticated]


class PasoRutaViewSet(viewsets.ModelViewSet):
    queryset = PasoRuta.objects.all()
    serializer_class = PasoRutaSerializer
    permission_classes = [IsAuthenticated]


class RutaOperacionViewSet(viewsets.ModelViewSet):
    queryset = RutaOperacion.objects.all()
    serializer_class = RutaOperacionSerializer
    permission_classes = [IsAuthenticated]


class OrdenRutaViewSet(viewsets.ModelViewSet):
    queryset = OrdenRuta.objects.all()
    serializer_class = OrdenRutaSerializer
    permission_classes = [IsAuthenticated]

    @action(
        detail=False,
        methods=["post"],
        url_path="crear-desde-orden",
    )
    def crear_desde_orden(self, request):
        try:
            resultado = crear_ruta_produccion(
                orden_produccion_id=request.data.get(
                    "orden_produccion_id"
                ),
                usuario=request.user,
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


class ProduccionOperacionViewSet(viewsets.ModelViewSet):
    queryset = ProduccionOperacion.objects.all()
    serializer_class = ProduccionOperacionSerializer
    permission_classes = [IsAuthenticated]

    # ========================================================
    # EJECUCIÓN DE PRODUCCIÓN
    # ========================================================

    @action(detail=True, methods=["post"], url_path="iniciar")
    def iniciar(self, request, pk=None):
        operacion = self.get_object()

        try:
            resultado = iniciar_operacion(
                produccion_operacion_id=operacion.id,
                usuario=request.user,
            )
            if not resultado.get("exito"):
                return Response(
                    resultado,
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                resultado,
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["post"], url_path="registrar-produccion")
    def registrar_produccion_action(self, request, pk=None):
        operacion = self.get_object()

        try:
            resultado = registrar_produccion(
                produccion_operacion_id=operacion.id,
                usuario=request.user,
                cantidad=request.data.get("cantidad"),
                unidad_medida=request.data.get("unidad_medida"),
                codigo_lote=request.data.get("codigo_lote"),
                bobinas=request.data.get("bobinas"),
                producto_version=request.data.get("producto_version"),
                observaciones=request.data.get("observaciones", ""),
                datos_resultado=request.data.get("datos_resultado", {}),
            )

            return Response(
                resultado,
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["post"], url_path="registrar-merma")
    def registrar_merma(self, request, pk=None):
        operacion = self.get_object()

        try:
            resultado = registrar_scrap(
                produccion_operacion_id=operacion.id,
                usuario=request.user,
                cantidad_merma=request.data.get("cantidad_merma"),
                unidad=request.data.get("unidad"),
                observaciones=request.data.get("observaciones", ""),
            )

            return Response(
                resultado,
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["post"], url_path="finalizar")
    def finalizar(self, request, pk=None):
        operacion = self.get_object()

        try:
            resultado = finalizar_operacion(
                produccion_operacion_id=operacion.id,
                usuario=request.user,
            )

            return Response(
                resultado,
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class DosificacionViewSet(viewsets.ModelViewSet):
    queryset = Dosificacion.objects.all()
    serializer_class = DosificacionSerializer
    permission_classes = [IsAuthenticated]


class ConsumoProduccionViewSet(viewsets.ModelViewSet):
    queryset = ConsumoProduccion.objects.all()
    serializer_class = ConsumoProduccionSerializer
    permission_classes = [IsAuthenticated]


# ============================================================
# CONTROL DE CALIDAD
# ============================================================

class ControlCalidadViewSet(viewsets.ModelViewSet):
    queryset = ControlCalidad.objects.all()
    serializer_class = ControlCalidadSerializer
    permission_classes = [IsAuthenticated]

    @action(
        detail=False,
        methods=["post"],
        url_path="crear",
    )
    def crear(self, request):
        try:
            resultado = crear_control_calidad(
                produccion_operacion_id=request.data.get(
                    "produccion_operacion_id"
                ),
                usuario=request.user,
                momento_control=request.data.get(
                    "momento_control"
                ),
                observaciones=request.data.get(
                    "observaciones",
                    "",
                ),
            )

            return Response(
                resultado,
                status=status.HTTP_201_CREATED,
            )

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=True,
        methods=["post"],
        url_path="completar",
    )
    def completar(self, request, pk=None):
        try:
            resultado = completar_control_calidad(
                control_calidad_id=pk,
                usuario=request.user,
                resultado=request.data.get("resultado"),
                observaciones=request.data.get(
                    "observaciones",
                    "",
                ),
                tiempo_control=request.data.get(
                    "tiempo_control"
                ),
            )

            return Response(
                resultado,
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
    detail=False,
    methods=["get"],
    url_path="por-operacion/(?P<operacion_id>[^/.]+)",
    )
    def por_operacion(self, request, operacion_id=None):
        try:
            resultado = obtener_controles_operacion(
                produccion_operacion_id=operacion_id
            )

            return Response(
                resultado,
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


# ============================================================
# TRANSFERENCIAS
# ============================================================

class TransferenciaProduccionViewSet(viewsets.ModelViewSet):
    queryset = TransferenciaProduccion.objects.all()
    serializer_class = TransferenciaProduccionSerializer
    permission_classes = [IsAuthenticated]

    @action(
        detail=False,
        methods=["post"],
        url_path="crear",
    )
    def crear(self, request):
        print("DATOS RECIBIDOS:", request.data)
        print("BOBINAS", request.data.get("bobinas"))
        try:
            resultado = crear_transferencia(
                usuario=request.user,
                operacion_origen_id=request.data.get(
                    "operacion_origen_id"
                ),
                operacion_destino_id=request.data.get(
                    "operacion_destino_id"
                ),
                bobinas=request.data.get(
                    "bobinas"
                ),
                observaciones=request.data.get(
                    "observaciones",
                    "",
                ),
            )

            return Response(
                resultado,
                status=status.HTTP_201_CREATED,
            )

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=True,
        methods=["post"],
        url_path="aprobar",
    )
    def aprobar(self, request, pk=None):
        try:
            print("PK TRANSFERENCIA:", pk)
            print("DATOS RECIBIDOS:", request.data)
            print(
                "CONTROL CALIDAD:",
                request.data.get("control_calidad_id")
            )
            resultado = aprobar_transferencia(
                transferencia_id=pk,
                usuario=request.user,
                control_calidad_id=request.data.get(
                    "control_calidad_id"
                ),
            )

            return Response(
                resultado,
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=True,
        methods=["post"],
        url_path="rechazar",
    )
    def rechazar(self, request, pk=None):
        try:
            resultado = rechazar_transferencia(
                transferencia_id=pk,
                usuario=request.user,
                observaciones=request.data.get(
                    "observaciones",
                    "",
                ),
            )

            return Response(
                resultado,
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=True,
        methods=["post"],
        url_path="completar",
    )
    def completar(self, request, pk=None):
        try:
            resultado = completar_transferencia(
                transferencia_id=pk,
                usuario=request.user,
            )

            return Response(
                resultado,
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
class ResultadoProduccionViewSet(viewsets.ModelViewSet):
    queryset = ResultadoProduccion.objects.all()
    serializer_class = ResultadoProduccionSerializer
    permission_classes = [IsAuthenticated]
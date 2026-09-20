from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.viabilidad.models import (
    EvaluacionComercial,
    EvaluacionViabilidad,
    EvaluacionProceso,
    ResultadoViabilidad,
)

from apps.viabilidad.serializers import (
    EvaluacionComercialSerializer,
    EvaluacionViabildadSerializer,
    EvaluacionProcesoSerialzer,
    ResultadoViabilidadSerializer,
)

from apps.viabilidad.services.viabilidad_service import (
    evaluar_viabilidad_producto,
    obtener_resumen_evaluacion,
)

from apps.viabilidad.services.seleccion_service import (
    seleccionar_maquina_proceso,
    obtener_alternativas_seleccion,
    seleccionar_maquinas_evaluacion_completa,
)

from apps.viabilidad.services.produccion_service import (
    aprobar_evaluacion_viabilidad,
    rechazar_evaluacion_viabilidad,
)


class EvaluacionComercialViewSet(viewsets.ModelViewSet):
    queryset = EvaluacionComercial.objects.all()
    serializer_class = EvaluacionComercialSerializer
    permission_classes = [IsAuthenticated]


class EvaluacionViabilidadViewSet(viewsets.ModelViewSet):
    queryset = EvaluacionViabilidad.objects.all()
    serializer_class = EvaluacionViabildadSerializer
    permission_classes = [IsAuthenticated]

    @action(
        detail=False,
        methods=["post"],
        url_path="evaluar-producto",
    )
    def evaluar_producto(self, request):
        """
        Ejecuta la evaluación completa de viabilidad
        para una especificación de producto.
        """

        especificacion_producto_id = request.data.get(
            "especificacion_producto"
        )

        if not especificacion_producto_id:
            return Response(
                {
                    "exito": False,
                    "mensaje": (
                        "El campo "
                        "'especificacion_producto' es obligatorio."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        from apps.comercial.models import (
            EspecificacionProductoSolicitado,
        )

        try:
            especificacion_producto = (
                EspecificacionProductoSolicitado.objects.get(
                    id=especificacion_producto_id
                )
            )
        except EspecificacionProductoSolicitado.DoesNotExist:
            return Response(
                {
                    "exito": False,
                    "mensaje": (
                        "La especificación de producto "
                        "no existe."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        resultado = evaluar_viabilidad_producto(
            especificacion_producto=especificacion_producto,
            usuario=request.user,
        )

        if not resultado.get("exito", True):
            return Response(
                resultado,
                status=status.HTTP_400_BAD_REQUEST,
            )

        evaluacion = resultado["evaluacion_viabilidad"]

        return Response(
            {
                "exito": True,
                "evaluacion_viabilidad": evaluacion.id,
                "ruta": resultado["ruta"],
                "descripcion_ruta": resultado["descripcion_ruta"],
                "viable_global": resultado["viable_global"],
                "procesos_viables": resultado["procesos_viables"],
                "procesos_no_viables": resultado[
                    "procesos_no_viables"
                ],
                "resultados_por_proceso": resultado[
                    "resultados_por_proceso"
                ],
            },
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["get"],
        url_path="resumen",
    )
    def resumen(self, request, pk=None):
        """
        Obtiene el resumen de una evaluación de viabilidad.
        """

        resultado = obtener_resumen_evaluacion(
            evaluacion_viabilidad_id=pk
        )

        return Response(
            resultado,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="aprobar",
    )
    def aprobar(self, request, pk=None):
        """
        Aprueba una evaluación de viabilidad.
        """

        observaciones = request.data.get(
            "observaciones",
            "",
        )

        resultado = aprobar_evaluacion_viabilidad(
            evaluacion_viabilidad_id=pk,
            usuario=request.user,
            observaciones=observaciones,
        )

        if not resultado["exito"]:
            return Response(
                resultado,
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            resultado,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="rechazar",
    )
    def rechazar(self, request, pk=None):
        """
        Rechaza una evaluación de viabilidad.
        """

        observaciones = request.data.get(
            "observaciones",
            "",
        )

        resultado = rechazar_evaluacion_viabilidad(
            evaluacion_viabilidad_id=pk,
            usuario=request.user,
            observaciones=observaciones,
        )

        return Response(
            resultado,
            status=(
                status.HTTP_200_OK
                if resultado["exito"]
                else status.HTTP_400_BAD_REQUEST
            ),
        )


class EvaluacionProcesoViewSet(viewsets.ModelViewSet):
    queryset = EvaluacionProceso.objects.all()
    serializer_class = EvaluacionProcesoSerialzer
    permission_classes = [IsAuthenticated]

    @action(
        detail=True,
        methods=["get"],
        url_path="alternativas",
    )
    def alternativas(self, request, pk=None):
        """
        Obtiene las máquinas viables disponibles
        para un proceso.
        """

        resultado = obtener_alternativas_seleccion(
            evaluacion_proceso_id=pk
        )

        return Response(
            resultado,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="seleccionar-maquina",
    )
    def seleccionar_maquina(self, request, pk=None):
        """
        Selecciona una máquina para el proceso.
        """

        equipo_id = request.data.get("equipo_id")

        if not equipo_id:
            return Response(
                {
                    "exito": False,
                    "mensaje": "El campo 'equipo_id' es obligatorio.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        resultado = seleccionar_maquina_proceso(
            evaluacion_proceso_id=pk,
            equipo_id=equipo_id,
            usuario=request.user,
        )

        return Response(
            resultado,
            status=(
                status.HTTP_200_OK
                if resultado["exito"]
                else status.HTTP_400_BAD_REQUEST
            ),
        )


class ResultadoViabilidadViewSet(viewsets.ModelViewSet):
    queryset = ResultadoViabilidad.objects.all()
    serializer_class = ResultadoViabilidadSerializer
    permission_classes = [IsAuthenticated]
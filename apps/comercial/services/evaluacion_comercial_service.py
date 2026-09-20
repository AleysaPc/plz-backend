from django.db import transaction
from django.utils import timezone

from apps.comercial.models import (
    SolicitudComercial,
    EspecificacionProductoSolicitado,
)
from apps.viabilidad.models import EvaluacionComercial


@transaction.atomic
def crear_evaluacion_comercial(
    especificacion_producto_id,
    usuario,
    resultado,
    observaciones="",
):
    """
    Registra la evaluación comercial de una especificación
    y permite que posteriormente pase a viabilidad.
    """

    especificacion = EspecificacionProductoSolicitado.objects.select_related(
        "solicitud_comercial"
    ).get(id=especificacion_producto_id)

    solicitud = especificacion.solicitud_comercial

    evaluacion = EvaluacionComercial.objects.create(
        especificacion_producto_solicitado=especificacion,
        usuario=usuario,
        resultado=resultado,
        fecha=timezone.now(),
        observaciones=observaciones,
    )

    if resultado.lower() in ["aprobado", "aprobada", "viable"]:
        solicitud.estado = SolicitudComercial.Estado.EN_VIABILIDAD
    elif resultado.lower() in ["rechazado", "rechazada", "no_viable"]:
        solicitud.estado = SolicitudComercial.Estado.RECHAZADA

    solicitud.save(update_fields=["estado", "updated_at"])

    return {
        "exito": True,
        "mensaje": "Evaluación comercial registrada correctamente",
        "evaluacion_comercial": evaluacion.id,
        "solicitud_comercial": solicitud.id,
        "especificacion_producto": especificacion.id,
        "resultado": evaluacion.resultado,
        "estado_solicitud": solicitud.estado,
    }
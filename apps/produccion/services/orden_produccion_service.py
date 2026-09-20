from django.db import transaction

from apps.produccion.models import (
    OrdenProduccion,
    ProduccionOperacion,
)


@transaction.atomic
def completar_orden_produccion(
    orden_produccion_id,
    usuario,
):
    orden = OrdenProduccion.objects.select_for_update().get(
        id=orden_produccion_id
    )

    if orden.estado != OrdenProduccion.Estado.EN_PROCESO:
        return {
            "exito": False,
            "mensaje": (
                "La orden de producción debe estar "
                "en estado 'en_proceso'."
            ),
            "orden_produccion": orden.id,
        }

    operaciones_pendientes = ProduccionOperacion.objects.filter(
        orden_ruta__orden_produccion=orden
    ).exclude(
        estado=ProduccionOperacion.Estado.COMPLETADA
    ).exists()

    if operaciones_pendientes:
        return {
            "exito": False,
            "mensaje": (
                "No se puede completar la orden porque "
                "existen operaciones pendientes."
            ),
            "orden_produccion": orden.id,
        }

    orden.estado = OrdenProduccion.Estado.COMPLETADA

    orden.save(
        update_fields=[
            "estado",
            "updated_at",
        ]
    )

    return {
        "exito": True,
        "mensaje": "Orden de producción completada correctamente.",
        "orden_produccion": orden.id,
        "numero_orden": orden.numero,
        "estado": orden.estado,
        "usuario": usuario.username,
    }
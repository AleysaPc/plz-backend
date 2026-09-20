from apps.produccion.services.control_produccion_service import (
    validar_calidad_para_transferencia,
)

"""
Servicio para gestionar transferencias de producción entre operaciones.

Flujo:
1. Crear transferencia pendiente.
2. Aprobar o rechazar la transferencia.
3. Completar transferencia.
4. Al completar, las bobinas pasan a la operación destino.
"""

from django.db import transaction
from django.utils import timezone

from apps.produccion.models import (
    TransferenciaProduccion,
    DetalleTransferenciaProduccion,
    ProduccionOperacion,
    BobinaProduccion,
)
from apps.calidad.models import ControlCalidad


@transaction.atomic
def crear_transferencia(
    operacion_origen_id,
    operacion_destino_id,
    bobinas,
    usuario,
    observaciones="",
):
    """
    Crea una transferencia de bobinas entre dos operaciones.

    Args:
        operacion_origen_id: ID de la operación origen.
        operacion_destino_id: ID de la operación destino.
        bobinas: lista de IDs de BobinaProduccion.
        usuario: usuario que registra la transferencia.
        observaciones: observaciones adicionales.

    Returns:
        dict con el resultado de la operación.
    """

    operacion_origen = ProduccionOperacion.objects.get(
        id=operacion_origen_id
    )

    operacion_destino = ProduccionOperacion.objects.get(
        id=operacion_destino_id
    )

    # Las operaciones deben pertenecer a la misma ruta de producción.
    if operacion_origen.orden_ruta_id != operacion_destino.orden_ruta_id:
        return {
            "exito": False,
            "mensaje": (
                "Las operaciones origen y destino deben "
                "pertenecer a la misma OrdenRuta."
            ),
        }

    if operacion_origen_id == operacion_destino_id:
        return {
            "exito": False,
            "mensaje": "La operación origen y destino no pueden ser la misma.",
        }

    if not bobinas:
        return {
            "exito": False,
            "mensaje": "Debe existir al menos una bobina para transferir.",
        }

    bobinas_obj = BobinaProduccion.objects.filter(
        id__in=bobinas
    )

    if bobinas_obj.count() != len(bobinas):
        return {
            "exito": False,
            "mensaje": "Una o más bobinas no existen.",
        }

    # Verificar que todas las bobinas pertenezcan a la operación origen.
    bobinas_invalidas = bobinas_obj.exclude(
        produccion_operacion=operacion_origen
    )

    if bobinas_invalidas.exists():
        return {
            "exito": False,
            "mensaje": (
                "Una o más bobinas no pertenecen "
                "a la operación origen."
            ),
        }

    # Verificar que las bobinas estén disponibles para transferencia.
    bobinas_no_disponibles = bobinas_obj.exclude(
        estado__in=[
            BobinaProduccion.Estado.EN_PRODUCCION,
            BobinaProduccion.Estado.TERMINADA,
        ]
    )

    if bobinas_no_disponibles.exists():
        return {
            "exito": False,
            "mensaje": (
                "Una o más bobinas no están disponibles "
                "para ser transferidas."
            ),
            "bobinas_no_disponibles": [
                b.codigo for b in bobinas_no_disponibles
            ],
        }

    cantidad_total = sum(
        bobina.peso for bobina in bobinas_obj
    )

    transferencia = TransferenciaProduccion.objects.create(
        operacion_origen=operacion_origen,
        operacion_destino=operacion_destino,
        cantidad_total=cantidad_total,
        unidad_medida="kg",
        estado=TransferenciaProduccion.Estado.PENDIENTE,
        usuario=usuario,
        observaciones=observaciones,
    )

    detalles = []

    for bobina in bobinas_obj:
        detalle = DetalleTransferenciaProduccion.objects.create(
            transferencia=transferencia,
            bobina=bobina,
            cantidad=bobina.peso,
            unidad_medida="kg",
        )
        detalles.append(detalle)

    return {
        "exito": True,
        "mensaje": "Transferencia creada correctamente.",
        "transferencia": transferencia.id,
        "operacion_origen": operacion_origen.id,
        "operacion_destino": operacion_destino.id,
        "cantidad_total": cantidad_total,
        "bobinas": [
            {
                "id": b.id,
                "codigo": b.codigo,
                "peso": b.peso,
            }
            for b in bobinas_obj
        ],
    }


@transaction.atomic
def aprobar_transferencia(
    transferencia_id,
    control_calidad_id,
    usuario,
    observaciones="",
):
    """
    Aprueba una transferencia después de validar
    el control de calidad de la operación origen.
    """

    transferencia = TransferenciaProduccion.objects.get(
        id=transferencia_id
    )

    if transferencia.estado != TransferenciaProduccion.Estado.PENDIENTE:
        return {
            "exito": False,
            "mensaje": (
                "Solo se pueden aprobar transferencias "
                "en estado pendiente."
            ),
        }

    # Validar calidad de la operación origen
    validacion = validar_calidad_para_transferencia(
        produccion_operacion_id=transferencia.operacion_origen_id
    )

    if not validacion["puede_transferir"]:
        return {
            "exito": False,
            "mensaje": validacion["mensaje"],
            "transferencia": transferencia.id,
        }

    # Obtener el control de calidad indicado
    control_calidad = ControlCalidad.objects.get(
        id=control_calidad_id
    )

    # El control debe pertenecer a la operación origen
    if (
        control_calidad.produccion_operacion_id
        != transferencia.operacion_origen_id
    ):
        return {
            "exito": False,
            "mensaje": (
                "El control de calidad no pertenece "
                "a la operación origen de la transferencia."
            ),
            "transferencia": transferencia.id,
        }

    # El control seleccionado debe estar aprobado
    if control_calidad.resultado != "aprobado":
        return {
            "exito": False,
            "mensaje": (
                "El control de calidad seleccionado "
                "no está aprobado."
            ),
            "transferencia": transferencia.id,
            "control_calidad": control_calidad.id,
        }

    transferencia.control_calidad = control_calidad
    transferencia.estado = TransferenciaProduccion.Estado.APROBADA

    if observaciones:
        transferencia.observaciones += (
            f"\n[Aprobación]: {observaciones}"
        )

    transferencia.save()

    return {
        "exito": True,
        "mensaje": "Transferencia aprobada correctamente.",
        "transferencia": transferencia.id,
        "control_calidad": control_calidad.id,
        "usuario": usuario.username,
    }

@transaction.atomic
def rechazar_transferencia(
    transferencia_id,
    usuario,
    observaciones="",
):
    """
    Rechaza una transferencia pendiente.
    """

    transferencia = TransferenciaProduccion.objects.get(
        id=transferencia_id
    )

    if transferencia.estado != TransferenciaProduccion.Estado.PENDIENTE:
        return {
            "exito": False,
            "mensaje": (
                "Solo se pueden rechazar transferencias "
                "en estado pendiente."
            ),
        }

    transferencia.estado = TransferenciaProduccion.Estado.RECHAZADA

    if observaciones:
        transferencia.observaciones += (
            f"\n[Rechazo]: {observaciones}"
        )

    transferencia.save()

    return {
        "exito": True,
        "mensaje": "Transferencia rechazada.",
        "transferencia": transferencia.id,
        "usuario": usuario.username,
    }


@transaction.atomic
def completar_transferencia(
    transferencia_id,
    usuario,
    observaciones="",
):
    """
    Completa una transferencia aprobada.

    Al completar:
    - Las bobinas pasan a estado TRANSFERIDA.
    - Se establece la operación destino.
    - Se registra la fecha de transferencia.
    - La transferencia pasa a COMPLETADA.
    - Se habilita la siguiente operación de la ruta.
    """

    transferencia = TransferenciaProduccion.objects.select_for_update().get(
        id=transferencia_id
    )

    if transferencia.estado != TransferenciaProduccion.Estado.APROBADA:
        return {
            "exito": False,
            "mensaje": (
                "La transferencia debe estar aprobada "
                "antes de completarse."
            ),
        }

    detalles = transferencia.detalles.select_related(
        "bobina"
    ).all()

    if not detalles.exists():
        return {
            "exito": False,
            "mensaje": "La transferencia no tiene bobinas asociadas.",
        }

    # ---------------------------------------------------------
    # VALIDAR OPERACIÓN ORIGEN
    # ---------------------------------------------------------

    operacion_origen = transferencia.operacion_origen

    if operacion_origen.estado != ProduccionOperacion.Estado.COMPLETADA:
        return {
            "exito": False,
            "mensaje": (
                "La operación origen debe estar completada "
                "antes de completar la transferencia."
            ),
            "operacion_origen": operacion_origen.id,
        }

    # ---------------------------------------------------------
    # VALIDAR CONTROL DE CALIDAD DE LA TRANSFERENCIA
    # ---------------------------------------------------------

    if not transferencia.control_calidad:
        return {
            "exito": False,
            "mensaje": (
                "La transferencia debe tener un control "
                "de calidad aprobado."
            ),
            "transferencia": transferencia.id,
        }

    if transferencia.control_calidad.resultado != "aprobado":
        return {
            "exito": False,
            "mensaje": (
                "El control de calidad asociado a la "
                "transferencia no está aprobado."
            ),
            "transferencia": transferencia.id,
        }

    # ---------------------------------------------------------
    # VALIDAR OPERACIÓN DESTINO
    # ---------------------------------------------------------

    operacion_destino = transferencia.operacion_destino

    if operacion_destino.estado != ProduccionOperacion.Estado.PENDIENTE:
        return {
            "exito": False,
            "mensaje": (
                "La operación destino debe estar pendiente "
                "para poder iniciarse."
            ),
            "operacion_destino": operacion_destino.id,
        }

    # ---------------------------------------------------------
    # VALIDAR QUE SEA LA SIGUIENTE OPERACIÓN
    # ---------------------------------------------------------

    if (
        operacion_destino.numero_operacion
        != operacion_origen.numero_operacion + 1
    ):
        return {
            "exito": False,
            "mensaje": (
                "La operación destino no es la siguiente "
                "operación de la ruta de producción."
            ),
            "operacion_origen": operacion_origen.id,
            "operacion_destino": operacion_destino.id,
        }

    ahora = timezone.now()
    bobinas_transferidas = []

    # ---------------------------------------------------------
    # TRANSFERIR BOBINAS
    # ---------------------------------------------------------

    for detalle in detalles:
        bobina = detalle.bobina

        if bobina.estado not in [
            BobinaProduccion.Estado.EN_PRODUCCION,
            BobinaProduccion.Estado.TERMINADA,
        ]:
            return {
                "exito": False,
                "mensaje": (
                    f"La bobina {bobina.codigo} "
                    "ya no está disponible para transferencia."
                ),
            }

        bobina.estado = BobinaProduccion.Estado.TRANSFERIDA
        bobina.operacion_destino = operacion_destino
        bobina.fecha_transferencia = ahora
        bobina.save()

        bobinas_transferidas.append(bobina.codigo)

    # ---------------------------------------------------------
    # COMPLETAR TRANSFERENCIA
    # ---------------------------------------------------------

    transferencia.estado = TransferenciaProduccion.Estado.COMPLETADA
    transferencia.fecha_transferencia = ahora

    if observaciones:
        transferencia.observaciones += (
            f"\n[Completada]: {observaciones}"
        )

    transferencia.save()

    # ---------------------------------------------------------
    # INICIAR OPERACIÓN DESTINO
    # ---------------------------------------------------------

    operacion_destino.estado = ProduccionOperacion.Estado.EN_PROCESO
    operacion_destino.fecha_inicio_real = ahora
    operacion_destino.save(
        update_fields=[
            "estado",
            "fecha_inicio_real",
            "updated_at",
        ]
    )

    return {
        "exito": True,
        "mensaje": (
            "Transferencia completada y "
            "siguiente operación iniciada correctamente."
        ),
        "transferencia": transferencia.id,
        "operacion_origen": {
            "id": operacion_origen.id,
            "numero_operacion": operacion_origen.numero_operacion,
            "estado": operacion_origen.estado,
        },
        "operacion_destino": {
            "id": operacion_destino.id,
            "numero_operacion": operacion_destino.numero_operacion,
            "proceso": operacion_destino.ruta_operacion.ruta_paso.nombre,
            "equipo": operacion_destino.equipo.nombre,
            "estado": operacion_destino.estado,
            "fecha_inicio": operacion_destino.fecha_inicio_real,
        },
        "bobinas_transferidas": bobinas_transferidas,
        "cantidad_total": transferencia.cantidad_total,
        "fecha_transferencia": ahora,
        "usuario": usuario.username,
    }
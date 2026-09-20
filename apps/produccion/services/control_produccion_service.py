"""
Servicio para gestión de controles de calidad durante la producción.

Permite:
- Crear un control de calidad para una operación.
- Completar/actualizar un control posteriormente.
- Consultar los controles de una operación.
- Determinar si una operación puede continuar o transferirse.
"""

from django.db import transaction
from django.utils import timezone

from apps.calidad.models import ControlCalidad
from apps.produccion.models import ProduccionOperacion


@transaction.atomic
def crear_control_calidad(
    produccion_operacion_id,
    usuario,
    momento_control,
    observaciones="",
):
    """
    Crea un control de calidad asociado a una operación.

    El control puede quedar pendiente de completar posteriormente.
    """

    operacion = ProduccionOperacion.objects.get(
        id=produccion_operacion_id
    )

    if operacion.estado not in (
        ProduccionOperacion.Estado.EN_PROCESO,
        ProduccionOperacion.Estado.COMPLETADA,
    ):
        return {
            "exito": False,
            "mensaje": (
                "Solo se puede registrar control de calidad "
                "en una operación en proceso o completada."
            ),
            "operacion": operacion.id,
        }

    control = ControlCalidad.objects.create(
        produccion_operacion=operacion,
        usuario=usuario,
        momento_control=momento_control,
        resultado="pendiente",
        observaciones=observaciones,
        fecha_control=timezone.now(),
    )

    return {
        "exito": True,
        "mensaje": "Control de calidad creado correctamente.",
        "control_calidad": control.id,
        "operacion": operacion.id,
        "resultado": control.resultado,
    }


@transaction.atomic
def completar_control_calidad(
    control_calidad_id,
    usuario,
    resultado,
    observaciones="",
    tiempo_control=None,
):
    """
    Completa un control de calidad creado previamente.

    resultado:
    - aprobado
    - observado
    - rechazado
    """

    control = ControlCalidad.objects.select_for_update().get(
        id=control_calidad_id
    )

    resultados_validos = {
        "aprobado",
        "observado",
        "rechazado",
    }

    if resultado not in resultados_validos:
        return {
            "exito": False,
            "mensaje": f"Resultado de calidad no válido: {resultado}",
            "control_calidad": control.id,
        }

    control.resultado = resultado

    if observaciones:
        control.observaciones = observaciones

    if tiempo_control is not None:
        control.tiempo_control = tiempo_control

    control.fecha_control = timezone.now()

    control.save()

    return {
        "exito": True,
        "mensaje": "Control de calidad actualizado correctamente.",
        "control_calidad": control.id,
        "operacion": control.produccion_operacion_id,
        "resultado": control.resultado,
    }


def obtener_controles_operacion(produccion_operacion_id):
    """
    Obtiene todos los controles de calidad de una operación.
    """

    operacion = ProduccionOperacion.objects.get(
        id=produccion_operacion_id
    )

    controles = (
        ControlCalidad.objects
        .filter(produccion_operacion=operacion)
        .order_by("-fecha_control")
    )

    controles_data = []

    for control in controles:
        controles_data.append({
            "id": control.id,
            "resultado": control.resultado,
            "momento_control": control.momento_control,
            "tiempo_control": control.tiempo_control,
            "observaciones": control.observaciones,
            "fecha_control": control.fecha_control,
            "usuario": control.usuario.username,
        })

    return {
        "operacion": operacion.id,
        "proceso": operacion.ruta_operacion.ruta_paso.nombre,
        "cantidad_controles": len(controles_data),
        "controles": controles_data,
    }


def validar_calidad_para_transferencia(
    produccion_operacion_id,
):
    """
    Determina si una operación tiene calidad aprobada
    para poder transferir su producción.

    Se considera válida cuando existe al menos un control
    de calidad aprobado y no existe un control rechazado.
    """

    operacion = ProduccionOperacion.objects.get(
        id=produccion_operacion_id
    )

    controles = ControlCalidad.objects.filter(
        produccion_operacion=operacion
    )

    if not controles.exists():
        return {
            "puede_transferir": False,
            "mensaje": "La operación no tiene controles de calidad.",
            "operacion": operacion.id,
        }

    if controles.filter(resultado="rechazado").exists():
        return {
            "puede_transferir": False,
            "mensaje": (
                "La operación tiene un control de calidad rechazado."
            ),
            "operacion": operacion.id,
        }

    if not controles.filter(resultado="aprobado").exists():
        return {
            "puede_transferir": False,
            "mensaje": (
                "La operación no tiene ningún control de calidad aprobado."
            ),
            "operacion": operacion.id,
        }

    return {
        "puede_transferir": True,
        "mensaje": "La calidad permite la transferencia.",
        "operacion": operacion.id,
    }
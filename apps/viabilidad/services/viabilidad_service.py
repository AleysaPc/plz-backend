"""
Servicio orquestador para evaluación de viabilidad de productos.

Coordina la evaluación de Extrusión + Flexografía + Confección
según la ruta que corresponda al producto.
"""
from decimal import Decimal
from django.db.models import Model
from django.utils import timezone


def convertir_resultado_json(obj):
    if isinstance(obj, Decimal):
        return float(obj)

    if isinstance(obj, Model):
        return {
            "id": obj.id,
            "nombre": str(obj),
        }

    if isinstance(obj, dict):
        return {
            clave: convertir_resultado_json(valor)
            for clave, valor in obj.items()
        }

    if isinstance(obj, list):
        return [
            convertir_resultado_json(item)
            for item in obj
        ]

    return obj


from apps.viabilidad.models import (
    EvaluacionViabilidad,
    EvaluacionProceso,
)

from apps.viabilidad.services.ruta_service import (
    determinar_ruta_producto,
    obtener_descripcion_ruta,
)

from apps.viabilidad.services.extrusion_service import (
    evaluar_extrusion_completa,
    guardar_resultados_viabilidad_extrusion,
)

from apps.viabilidad.services.flexografia_service import (
    evaluar_flexografia_completa,
    guardar_resultados_viabilidad_flexografia,
)

from apps.viabilidad.services.confeccion_service import (
    evaluar_confeccion_completa,
    guardar_resultados_viabilidad_confeccion,
)

def evaluar_viabilidad_producto(
    especificacion_producto,
    usuario,
):
    """
    Orquesta la evaluación completa de viabilidad de un producto.

    Flujo:
    1. Determina la ruta del producto (según diseño/impresión)
    2. Evalúa cada proceso según la ruta
    3. Consolida resultados globales
    4. Crea/actualiza EvaluacionViabilidad
    5. Crea EvaluacionProceso para cada proceso
    6. Guarda ResultadoViabilidad para cada máquina evaluada

    Args:
        especificacion_producto: EspecificacionProductoSolicitado
        usuario: Usuario que realiza la evaluación

    Returns:
        dict: Resultado global de la evaluación con:
            - evaluacion_viabilidad: objeto EvaluacionViabilidad
            - ruta: lista de procesos
            - resultados_por_proceso: dict con resultados de cada proceso
            - viable_global: bool (viable si todos los procesos requeridos son viables)
    """
    # Paso 1: Determinar la ruta del producto
    ruta = determinar_ruta_producto(especificacion_producto)
    descripcion_ruta = obtener_descripcion_ruta(ruta)

    # Obtener especificaciones relacionadas
    especificacion_bolsa = getattr(especificacion_producto,'especificacion_bolsa',None)

    # Paso 2: Crear EvaluacionViabilidad
    evaluacion_comercial = (
        especificacion_producto.evaluaciones_comerciales
        .order_by("-fecha")
        .first()
    )
    if not evaluacion_comercial:
        return {
            "exito": False,
            "mensaje": (
                "La especificación del producto no tiene una "
                "evaluación comercial registrada."
            ),
            "especificacion_producto": especificacion_producto.id,
        }

    evaluacion_viabilidad = EvaluacionViabilidad.objects.create(
        evaluacion_comercial=evaluacion_comercial,
        usuario=usuario,
        resultado="en_proceso",
        fecha_inicio=timezone.now(),
        observaciones=f"Ruta determinada: {descripcion_ruta}",
    )

    # Paso 3: Evaluar cada proceso según la ruta
    resultados_por_proceso = {}
    procesos_viables = []

    for proceso in ruta:
        # Crear EvaluacionProceso para este proceso
        evaluacion_proceso = EvaluacionProceso.objects.create(
            evaluacion_viabilidad=evaluacion_viabilidad,
            usuario=usuario,
            fecha_inicio=timezone.now(),
            estado=EvaluacionProceso.Estado.EN_PROCESO,
            proceso=proceso,
        )

        # Evaluar según el tipo de proceso
        if proceso == "extrusion":
            resultado = evaluar_extrusion_completa(
                especificacion=especificacion_producto,
                especificacion_bolsa=especificacion_bolsa,
            )
            guardar_resultados_viabilidad_extrusion(
                resultado["resultados_evaluacion"],
                evaluacion_proceso,
            )

        elif proceso == "flexografia":
            resultado = evaluar_flexografia_completa(
                especificacion=especificacion_producto,
                especificacion_bolsa=especificacion_bolsa,
            )
            guardar_resultados_viabilidad_flexografia(
                resultado["resultados_evaluacion"],
                evaluacion_proceso,
            )

        elif proceso == "confeccion":
            resultado = evaluar_confeccion_completa(
                especificacion=especificacion_producto,
                especificacion_bolsa=especificacion_bolsa,
            )
            guardar_resultados_viabilidad_confeccion(
                resultado["resultados_evaluacion"],
                evaluacion_proceso,
            )

        # Marcar la evaluación del proceso como completada
        evaluacion_proceso.estado = EvaluacionProceso.Estado.COMPLETADA
        evaluacion_proceso.fecha_fin = timezone.now()
        evaluacion_proceso.save()

        # Guardar resultado del proceso
        resultados_por_proceso[proceso] = convertir_resultado_json(resultado)

        # Verificar si el proceso es viable
        if resultado["viable"]:
            procesos_viables.append(proceso)

    # Paso 4: Determinar resultado global
    viable_global = len(procesos_viables) == len(ruta)

    # Actualizar EvaluacionViabilidad con el resultado global
    evaluacion_viabilidad.resultado = (
        "viable" if viable_global else "no_viable"
    )
    evaluacion_viabilidad.fecha_fin = timezone.now()

    if viable_global:
        evaluacion_viabilidad.observaciones = (
            f"Producto viable. Ruta: {descripcion_ruta}. "
            f"Procesos viables: {', '.join(procesos_viables)}"
        )
    else:
        procesos_no_viables = [
            p for p in ruta if p not in procesos_viables
        ]
        evaluacion_viabilidad.observaciones = (
            f"Producto no viable. Ruta: {descripcion_ruta}. "
            f"Procesos no viables: {', '.join(procesos_no_viables)}"
        )

    evaluacion_viabilidad.save()

    return {
        "evaluacion_viabilidad": evaluacion_viabilidad,
        "ruta": ruta,
        "descripcion_ruta": descripcion_ruta,
        "resultados_por_proceso": resultados_por_proceso,
        "viable_global": viable_global,
        "procesos_viables": procesos_viables,
        "procesos_no_viables": [
            p for p in ruta if p not in procesos_viables
        ],
    }


def obtener_resumen_evaluacion(evaluacion_viabilidad_id):
    """
    Obtiene un resumen de una evaluación de viabilidad existente.

    Args:
        evaluacion_viabilidad_id: ID de la EvaluacionViabilidad

    Returns:
        dict: Resumen de la evaluación con resultados por proceso
    """
    evaluacion_viabilidad = EvaluacionViabilidad.objects.get(
        id=evaluacion_viabilidad_id
    )

    evaluaciones_proceso = evaluacion_viabilidad.evaluaciones_proceso.all()

    resumen = {
        "evaluacion_viabilidad": {
            "id": evaluacion_viabilidad.id,
            "resultado": evaluacion_viabilidad.resultado,
            "fecha_inicio": evaluacion_viabilidad.fecha_inicio,
            "fecha_fin": evaluacion_viabilidad.fecha_fin,
            "observaciones": evaluacion_viabilidad.observaciones,
        },
        "procesos": [],
    }

    for eval_proceso in evaluaciones_proceso:
        resultados = eval_proceso.resultados_viabilidad.all()

        maquinas_viables = [
            {
                "equipo": r.equipo.nombre,
                "puntaje": r.puntaje_viabilidad,
                "es_recomendada": r.es_recomendada,
            }
            for r in resultados
            if r.resultado == "viable"
        ]

        resumen["procesos"].append({
            "proceso": eval_proceso.proceso,
            "estado": eval_proceso.estado,
            "maquinas_viables": maquinas_viables,
            "cantidad_viables": len(maquinas_viables),
        })

    return resumen
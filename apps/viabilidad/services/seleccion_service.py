"""
Servicio para selección de máquinas en la evaluación de viabilidad.

Implementa la lógica:
- 1 viable → selección automática
- 2+ viables → usuario selecciona
- 0 viables → solicitud no viable
"""
from django.utils import timezone

from apps.viabilidad.models import (
    EvaluacionProceso,
    ResultadoViabilidad,
)
from apps.recursos.models import Equipo


def seleccionar_maquina_proceso(
    evaluacion_proceso_id,
    equipo_id,
    usuario,
):
    """
    Selecciona una máquina específica para un proceso de evaluación.

    Args:
        evaluacion_proceso_id: ID de la EvaluacionProceso
        equipo_id: ID del Equipo seleccionado
        usuario: Usuario que realiza la selección

    Returns:
        dict: Resultado de la selección
    """
    evaluacion_proceso = EvaluacionProceso.objects.get(
        id=evaluacion_proceso_id
    )
    
    equipo = Equipo.objects.get(id=equipo_id)
    
    # Verificar que el equipo sea viable para este proceso
    resultado_viabilidad = ResultadoViabilidad.objects.filter(
        evaluacion_proceso=evaluacion_proceso,
        equipo=equipo,
        resultado="viable"
    ).first()
    
    if not resultado_viabilidad:
        return {
            "exito": False,
            "mensaje": f"El equipo {equipo.nombre} no es viable para este proceso",
            "evaluacion_proceso": evaluacion_proceso.id,
        }
    
    # Actualizar la máquina seleccionada en la evaluación del proceso
    evaluacion_proceso.maquina_seleccionada = equipo
    evaluacion_proceso.save()
    
    # Actualizar es_recomendada en los resultados de viabilidad
    # Solo el seleccionado debe tener es_recomendada=True
    ResultadoViabilidad.objects.filter(
        evaluacion_proceso=evaluacion_proceso
    ).update(es_recomendada=False)
    
    resultado_viabilidad.es_recomendada = True
    resultado_viabilidad.save()
    
    return {
        "exito": True,
        "mensaje": f"Máquina {equipo.nombre} seleccionada correctamente",
        "evaluacion_proceso": evaluacion_proceso.id,
        "equipo_seleccionado": equipo.nombre,
        "proceso": evaluacion_proceso.proceso,
    }


def seleccionar_maquina_automaticamente(
    evaluacion_proceso_id,
    usuario,
):
    """
    Selecciona automáticamente la máquina recomendada cuando hay solo 1 viable.

    Args:
        evaluacion_proceso_id: ID de la EvaluacionProceso
        usuario: Usuario que realiza la selección

    Returns:
        dict: Resultado de la selección automática
    """
    evaluacion_proceso = EvaluacionProceso.objects.get(
        id=evaluacion_proceso_id
    )
    
    # Buscar resultados viables
    resultados_viables = ResultadoViabilidad.objects.filter(
        evaluacion_proceso=evaluacion_proceso,
        resultado="viable"
    )
    
    if resultados_viables.count() == 0:
        return {
            "exito": False,
            "mensaje": "No hay máquinas viables para seleccionar automáticamente",
            "evaluacion_proceso": evaluacion_proceso.id,
        }
    
    if resultados_viables.count() > 1:
        return {
            "exito": False,
            "mensaje": f"Hay {resultados_viables.count()} máquinas viables, el usuario debe seleccionar",
            "evaluacion_proceso": evaluacion_proceso.id,
            "requiere_seleccion_usuario": True,
        }
    
    # Hay exactamente 1 viable, seleccionarla automáticamente
    resultado_unico = resultados_viables.first()
    
    return seleccionar_maquina_proceso(
        evaluacion_proceso_id=evaluacion_proceso_id,
        equipo_id=resultado_unico.equipo.id,
        usuario=usuario,
    )


def obtener_alternativas_seleccion(evaluacion_proceso_id):
    """
    Obtiene las máquinas viables disponibles para selección por el usuario.

    Args:
        evaluacion_proceso_id: ID de la EvaluacionProceso

    Returns:
        dict: Con las alternativas disponibles
    """
    evaluacion_proceso = EvaluacionProceso.objects.get(
        id=evaluacion_proceso_id
    )
    
    resultados_viables = ResultadoViabilidad.objects.filter(
        evaluacion_proceso=evaluacion_proceso,
        resultado="viable"
    )
    
    alternativas = []
    for resultado in resultados_viables:
        alternativas.append({
            "equipo_id": resultado.equipo.id,
            "equipo_nombre": resultado.equipo.nombre,
            "puntaje_viabilidad": resultado.puntaje_viabilidad,
            "es_recomendada": resultado.es_recomendada,
            "criterios_evaluados": resultado.criterios_evaluados,
        })
    
    return {
        "evaluacion_proceso": evaluacion_proceso.id,
        "proceso": evaluacion_proceso.proceso,
        "cantidad_alternativas": len(alternativas),
        "alternativas": alternativas,
        "requiere_seleccion_usuario": len(alternativas) > 1,
    }


def seleccionar_maquinas_evaluacion_completa(
    evaluacion_viabilidad_id,
    usuario,
    selecciones_usuario=None,
):
    """
    Selecciona máquinas para todos los procesos de una evaluación.

    Args:
        evaluacion_viabilidad_id: ID de la EvaluacionViabilidad
        usuario: Usuario que realiza las selecciones
        selecciones_usuario: dict {proceso: equipo_id} para selecciones manuales

    Returns:
        dict: Resultado global de las selecciones
    """
    from apps.viabilidad.models import EvaluacionViabilidad
    
    evaluacion_viabilidad = EvaluacionViabilidad.objects.get(
        id=evaluacion_viabilidad_id
    )
    
    evaluaciones_proceso = evaluacion_viabilidad.evaluaciones_proceso.all()
    
    resultados_seleccion = {}
    procesos_con_seleccion = []
    procesos_sin_seleccion = []
    
    for eval_proceso in evaluaciones_proceso:
        proceso = eval_proceso.proceso
        
        # Si el usuario proporcionó una selección para este proceso
        if selecciones_usuario and proceso in selecciones_usuario:
            resultado = seleccionar_maquina_proceso(
                evaluacion_proceso_id=eval_proceso.id,
                equipo_id=selecciones_usuario[proceso],
                usuario=usuario,
            )
        else:
            # Intentar selección automática
            resultado = seleccionar_maquina_automaticamente(
                evaluacion_proceso_id=eval_proceso.id,
                usuario=usuario,
            )
        
        resultados_seleccion[proceso] = resultado
        
        if resultado["exito"]:
            procesos_con_seleccion.append(proceso)
        else:
            procesos_sin_seleccion.append(proceso)
    
    # Determinar si la evaluación está completamente seleccionada
    completamente_seleccionada = (
        len(procesos_con_seleccion) == len(evaluaciones_proceso)
    )
    
    return {
        "evaluacion_viabilidad": evaluacion_viabilidad_id,
        "completamente_seleccionada": completamente_seleccionada,
        "procesos_con_seleccion": procesos_con_seleccion,
        "procesos_sin_seleccion": procesos_sin_seleccion,
        "resultados_por_proceso": resultados_seleccion,
        "requiere_seleccion_usuario": len(procesos_sin_seleccion) > 0,
    }
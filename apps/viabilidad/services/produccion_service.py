from apps.comercial.models import(
    PedidoDetalle
)
from django.db import transaction
"""
Servicio para aprobación e inicio de producción desde evaluación de viabilidad.

Conecta el flujo de viabilidad con:
- OrdenProduccion
- OrdenRuta
- ProduccionOperacion
"""
from django.utils import timezone
from apps.viabilidad.services.ruta_service import determinar_ruta_producto

from apps.viabilidad.models import (
    EvaluacionViabilidad,
    EvaluacionProceso,
    ResultadoViabilidad,
)
from apps.produccion.models import (
    OrdenProduccion,
    OrdenRuta,
    ProduccionOperacion,
    RutaProduccion,
    PasoRuta,
    RutaOperacion,
    OrdenProduccionDetalle,
)
from apps.recursos.models import Equipo


def aprobar_evaluacion_viabilidad(
    evaluacion_viabilidad_id,
    usuario,
    observaciones="",
):
    """
    Aprueba una evaluación de viabilidad.

    Args:
        evaluacion_viabilidad_id: ID de la EvaluacionViabilidad
        usuario: Usuario que aprueba
        observaciones: Observaciones de la aprobación

    Returns:
        dict: Resultado de la aprobación
    """
    evaluacion_viabilidad = EvaluacionViabilidad.objects.get(
        id=evaluacion_viabilidad_id
    )
    
    # Verificar que la evaluación sea viable
    if evaluacion_viabilidad.resultado != "viable":
        return {
            "exito": False,
            "mensaje": "Solo se pueden aprobar evaluaciones viables",
            "evaluacion_viabilidad": evaluacion_viabilidad_id,
        }
    
    # Verificar que todos los procesos tengan máquina seleccionada
    evaluaciones_proceso = evaluacion_viabilidad.evaluaciones_proceso.all()
    
    procesos_sin_seleccion = [
        ep.proceso 
        for ep in evaluaciones_proceso 
        if not ep.maquina_seleccionada
    ]
    
    if procesos_sin_seleccion:
        return {
            "exito": False,
            "mensaje": f"Faltan seleccionar máquinas para: {', '.join(procesos_sin_seleccion)}",
            "evaluacion_viabilidad": evaluacion_viabilidad_id,
            "procesos_sin_seleccion": procesos_sin_seleccion,
        }
    
    # Actualizar estado de aprobación
    evaluacion_viabilidad.estado_aprobacion = (
        EvaluacionViabilidad.EstadoAprobacion.APROBADA
    )
    evaluacion_viabilidad.fecha_aprobacion = timezone.now()
    evaluacion_viabilidad.aprobado_por = usuario
    if observaciones:
        evaluacion_viabilidad.observaciones += f"\n[Aprobación]: {observaciones}"
    evaluacion_viabilidad.save()
    
    return {
        "exito": True,
        "mensaje": "Evaluación aprobada correctamente",
        "evaluacion_viabilidad": evaluacion_viabilidad_id,
        "fecha_aprobacion": evaluacion_viabilidad.fecha_aprobacion,
        "aprobado_por": usuario.username,
    }


def rechazar_evaluacion_viabilidad(
    evaluacion_viabilidad_id,
    usuario,
    observaciones="",
):
    """
    Rechaza una evaluación de viabilidad.

    Args:
        evaluacion_viabilidad_id: ID de la EvaluacionViabilidad
        usuario: Usuario que rechaza
        observaciones: Motivo del rechazo

    Returns:
        dict: Resultado del rechazo
    """
    evaluacion_viabilidad = EvaluacionViabilidad.objects.get(
        id=evaluacion_viabilidad_id
    )
    
    # Actualizar estado de rechazo
    evaluacion_viabilidad.estado_aprobacion = (
        EvaluacionViabilidad.EstadoAprobacion.RECHAZADA
    )
    evaluacion_viabilidad.fecha_aprobacion = timezone.now()
    evaluacion_viabilidad.aprobado_por = usuario
    if observaciones:
        evaluacion_viabilidad.observaciones += f"\n[Rechazo]: {observaciones}"
    evaluacion_viabilidad.save()
    
    return {
        "exito": True,
        "mensaje": "Evaluación rechazada",
        "evaluacion_viabilidad": evaluacion_viabilidad_id,
        "fecha_aprobacion": evaluacion_viabilidad.fecha_aprobacion,
        "aprobado_por": usuario.username,
    }

@transaction.atomic
def crear_orden_produccion_desde_viabilidad(
    evaluacion_viabilidad_id,
    usuario,
    cantidad_planificada,
    pedido_detalle_id=None,
    fecha_inicio_planificada=None,
    fecha_fin_planificada=None,
    prioridad="normal",
    observaciones="",
):
    """
    Crea una orden de producción a partir de una evaluación de viabilidad aprobada.
    """

    evaluacion_viabilidad = EvaluacionViabilidad.objects.get(
        id=evaluacion_viabilidad_id
    )

    # Verificar que esté aprobada
    if evaluacion_viabilidad.estado_aprobacion != (
        EvaluacionViabilidad.EstadoAprobacion.APROBADA
    ):
        return {
            "exito": False,
            "mensaje": "La evaluación debe estar aprobada para crear orden de producción",
            "evaluacion_viabilidad": evaluacion_viabilidad_id,
        }

    # Verificar que no tenga orden ya creada
    if evaluacion_viabilidad.ordenes_produccion.exists():
        return {
            "exito": False,
            "mensaje": "Ya existe una orden de producción para esta evaluación",
            "evaluacion_viabilidad": evaluacion_viabilidad_id,
        }

    # Obtener pedido detalle si fue proporcionado
    pedido_detalle = None

    if pedido_detalle_id:
        try:
            pedido_detalle = PedidoDetalle.objects.get(
                id=pedido_detalle_id
            )
        except PedidoDetalle.DoesNotExist:
            return {
                "exito": False,
                "mensaje": "El detalle del pedido no existe",
                "pedido_detalle": pedido_detalle_id,
            }

        # Verificar que el pedido esté finalizado
        if pedido_detalle.pedido.estado != "finalizado":
            return {
                "exito": False,
                "mensaje": "El pedido debe estar finalizado para crear la orden de producción",
                "pedido": pedido_detalle.pedido.id,
            }

    # Fechas por defecto
    if not fecha_inicio_planificada:
        fecha_inicio_planificada = timezone.now()

    if not fecha_fin_planificada:
        from datetime import timedelta
        fecha_fin_planificada = fecha_inicio_planificada + timedelta(days=7)

    # Generar número de orden
    numero_orden = (
        f"OP-{timezone.now().strftime('%Y%m%d')}-{evaluacion_viabilidad.id}"
    )

    # Crear OrdenProduccion
    orden_produccion = OrdenProduccion.objects.create(
        evaluacion_viabilidad=evaluacion_viabilidad,
        pedido_detalle=pedido_detalle,
        numero=numero_orden,
        cantidad_planificada=cantidad_planificada,
        fecha_inicio_planificada=fecha_inicio_planificada,
        fecha_fin_planificada=fecha_fin_planificada,
        prioridad=prioridad,
        observaciones=observaciones,
    )

    # Crear detalle de orden de producción
    if pedido_detalle:
        OrdenProduccionDetalle.objects.create(
            orden_produccion=orden_produccion,
            pedido_detalle=pedido_detalle,
            cantidad_programada=cantidad_planificada,
        )

    return {
        "exito": True,
        "mensaje": "Orden de producción creada correctamente",
        "orden_produccion": orden_produccion.id,
        "numero_orden": orden_produccion.numero,
        "evaluacion_viabilidad": evaluacion_viabilidad_id,
        "pedido_detalle": pedido_detalle_id,
    }


@transaction.atomic
def crear_ruta_produccion(
    orden_produccion_id,
    usuario,
):
    """
    Crea la OrdenRuta y las ProduccionOperacion
    utilizando una RutaProduccion previamente configurada.

    La ruta se determina según la especificación del producto
    y se utilizan los PasoRuta y RutaOperacion existentes.
    """

    orden_produccion = OrdenProduccion.objects.get(
        id=orden_produccion_id
    )

    evaluacion_viabilidad = orden_produccion.evaluacion_viabilidad

    if not evaluacion_viabilidad:
        return {
            "exito": False,
            "mensaje": "La orden no tiene una evaluación de viabilidad asociada.",
            "orden_produccion": orden_produccion_id,
        }

    # Obtener el producto evaluado
    if not evaluacion_viabilidad.evaluacion_comercial:
        return {
            "exito": False,
            "mensaje": "La evaluación de viabilidad no tiene evaluación comercial asociada.",
            "orden_produccion": orden_produccion_id,
        }

    especificacion_producto = (
        evaluacion_viabilidad
        .evaluacion_comercial
        .especificacion_producto_solicitado
    )

    # Determinar la ruta que necesita el producto
    procesos_requeridos = determinar_ruta_producto(
        especificacion_producto
    )

    # Buscar una RutaProduccion activa cuya secuencia de pasos
    # coincida con los procesos requeridos (manejo de tildes simplificado)
    rutas_activas = RutaProduccion.objects.filter(
        estado=RutaProduccion.Estado.ACTIVA
    )

    ruta_produccion = None

    # Función simple para normalizar texto (quitar tildes comunes)
    def normalizar_texto(texto):
        replacements = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        }
        for old, new in replacements.items():
            texto = texto.replace(old, new)
        return texto.strip().lower()
    
    procesos_requeridos_normalizados = [
        normalizar_texto(proceso)
        for proceso in procesos_requeridos
    ]

    for ruta in rutas_activas:

        pasos = list(
            ruta.pasos
            .filter(
                estado=PasoRuta.Estado.ACTIVO
            )
            .order_by("orden_ejecucion")
        )

        procesos_ruta = [
            normalizar_texto(paso.nombre)
            for paso in pasos
        ]

        # Verificar coincidencia exacta de procesos
        if procesos_ruta == procesos_requeridos_normalizados:
            ruta_produccion = ruta
            break

    if not ruta_produccion:
        return {
            "exito": False,
            "mensaje": (
                "No existe una RutaProduccion activa configurada "
                f"para la ruta: {' → '.join(procesos_requeridos)}"
            ),
            "orden_produccion": orden_produccion_id,
            "ruta_requerida": procesos_requeridos,
        }

    # Crear OrdenRuta utilizando la ruta existente
    orden_ruta = OrdenRuta.objects.create(
        orden_produccion=orden_produccion,
        ruta_produccion=ruta_produccion,
        version=1,
        estado=OrdenRuta.Estado.ACTIVA,
    )

    operaciones_creadas = []

    # Crear las operaciones respetando el orden de los pasos
    for numero_operacion, proceso in enumerate(
        procesos_requeridos,
        start=1,
    ):

        # Buscar el PasoRuta correspondiente usando la misma normalización
        proceso_normalizado = normalizar_texto(proceso)
        
        paso_ruta = next(
            (
                paso
                for paso in ruta_produccion.pasos.filter(
                    estado=PasoRuta.Estado.ACTIVO
                )
                if normalizar_texto(paso.nombre) == proceso_normalizado
            ),
            None,
        )

        if not paso_ruta:
            raise ValueError(
                f"No se encontró el PasoRuta para el proceso '{proceso}'."
            )

        # Buscar la operación existente del paso
        ruta_operacion = (
            RutaOperacion.objects
            .filter(
                ruta_paso=paso_ruta,
                estado=RutaOperacion.Estado.ACTIVA,
            )
            .order_by("orden_ejecucion")
            .first()
        )

        if not ruta_operacion:
            raise ValueError(
                f"No existe una RutaOperacion activa para el proceso '{proceso}'."
            )

        # Obtener la evaluación del proceso
        evaluacion_proceso = (
            evaluacion_viabilidad
            .evaluaciones_proceso
            .filter(
                proceso=proceso,
                maquina_seleccionada__isnull=False,
            )
            .first()
        )

        if not evaluacion_proceso:
            raise ValueError(
                f"No existe una máquina seleccionada para el proceso '{proceso}'."
            )

        # Obtener el resultado de viabilidad de la máquina seleccionada
        resultado_viabilidad = (
            ResultadoViabilidad.objects
            .filter(
                evaluacion_proceso=evaluacion_proceso,
                equipo=evaluacion_proceso.maquina_seleccionada,
                resultado="viable",
            )
            .first()
        )

        if not resultado_viabilidad:
            raise ValueError(
                f"No existe un ResultadoViabilidad viable para "
                f"el equipo seleccionado en '{proceso}'."
            )

        # Utilizar el tiempo real configurado en RutaOperacion
        tiempo_estandar = ruta_operacion.tiempo_estandar_min

        fecha_inicio = orden_produccion.fecha_inicio_planificada

        from datetime import timedelta

        fecha_fin = fecha_inicio + timedelta(
            minutes=float(tiempo_estandar)
        )

        produccion_operacion = ProduccionOperacion.objects.create(
            orden_ruta=orden_ruta,
            ruta_operacion=ruta_operacion,
            resultado_viabilidad=resultado_viabilidad,
            equipo=evaluacion_proceso.maquina_seleccionada,
            numero_operacion=numero_operacion,
            fecha_inicio_planificada=fecha_inicio,
            fecha_fin_planificada=fecha_fin,
            estado=ProduccionOperacion.Estado.PENDIENTE,
        )

        operaciones_creadas.append({
            "numero": numero_operacion,
            "proceso": proceso,
            "equipo": evaluacion_proceso.maquina_seleccionada.nombre,
            "operacion_id": produccion_operacion.id,
            "tiempo_estandar_min": float(tiempo_estandar),
        })

    return {
        "exito": True,
        "mensaje": "Ruta de producción creada correctamente",
        "orden_ruta": orden_ruta.id,
        "orden_produccion": orden_produccion_id,
        "ruta_produccion": ruta_produccion.codigo,
        "procesos": procesos_requeridos,
        "operaciones_creadas": operaciones_creadas,
    }


def iniciar_produccion_completa(
    evaluacion_viabilidad_id,
    usuario,
    cantidad_programada,
    prioridad="normal",
    observaciones="",
):
    """
    Función DEPRECADA: Esta función automatiza todo el proceso.
    Usar las funciones individuales para seguir el flujo correcto.
    
    El flujo correcto es:
    1. aprobar_evaluacion_viabilidad()
    2. crear_orden_produccion_desde_viabilidad()
    3. crear_ruta_produccion()
    4. iniciar_produccion() (nueva función)
    
    Esta función se mantiene por compatibilidad pero no se recomienda su uso.
    """
    # Paso 1: Aprobar evaluación
    resultado_aprobacion = aprobar_evaluacion_viabilidad(
        evaluacion_viabilidad_id=evaluacion_viabilidad_id,
        usuario=usuario,
        observaciones=observaciones,
    )
    
    if not resultado_aprobacion["exito"]:
        return {
            "exito": False,
            "mensaje": "Error al aprobar evaluación",
            "error_aprobacion": resultado_aprobacion["mensaje"],
        }
    
    # Paso 2: Crear orden de producción
    resultado_orden = crear_orden_produccion_desde_viabilidad(
        evaluacion_viabilidad_id=evaluacion_viabilidad_id,
        usuario=usuario,
        cantidad_programada=cantidad_programada,
        prioridad=prioridad,
        observaciones=observaciones,
    )
    
    if not resultado_orden["exito"]:
        return {
            "exito": False,
            "mensaje": "Error al crear orden de producción",
            "error_orden": resultado_orden["mensaje"],
        }
    
    # Paso 3: Crear ruta de producción
    resultado_ruta = crear_ruta_produccion(
        orden_produccion_id=resultado_orden["orden_produccion"],
        usuario=usuario,
    )
    
    if not resultado_ruta["exito"]:
        return {
            "exito": False,
            "mensaje": "Error al crear ruta de producción",
            "error_ruta": resultado_ruta["mensaje"],
        }
    
    return {
        "exito": True,
        "mensaje": "Producción configurada correctamente (usar iniciar_produccion para comenzar)",
        "evaluacion_viabilidad": evaluacion_viabilidad_id,
        "orden_produccion": resultado_orden["orden_produccion"],
        "numero_orden": resultado_orden["numero_orden"],
        "orden_ruta": resultado_ruta["orden_ruta"],
        "operaciones_creadas": resultado_ruta["operaciones_creadas"],
        "nota": "La producción está planificada. Usar iniciar_produccion() para comenzar.",
    }


def iniciar_produccion(orden_produccion_id, usuario, observaciones=""):
    orden_produccion = OrdenProduccion.objects.get(id=orden_produccion_id)

    # La orden debe estar planificada
    if orden_produccion.estado != OrdenProduccion.Estado.PLANIFICADA:
        return {
            "exito": False,
            "mensaje": "La orden de producción debe estar planificada para iniciar",
            "orden_produccion": orden_produccion_id,
        }

    # La orden debe tener una ruta configurada
    if not orden_produccion.rutas.exists():
        return {
            "exito": False,
            "mensaje": "La orden no tiene ruta de producción configurada",
            "orden_produccion": orden_produccion_id,
        }

    orden_ruta = orden_produccion.rutas.first()

    # Obtener operaciones ordenadas
    operaciones = orden_ruta.operaciones.all().order_by("numero_operacion")

    if not operaciones.exists():
        return {
            "exito": False,
            "mensaje": "La ruta no tiene operaciones configuradas",
            "orden_produccion": orden_produccion_id,
        }

    # ---------------------------------------------------------
    # INICIAR LA ORDEN
    # ---------------------------------------------------------

    orden_produccion.estado = OrdenProduccion.Estado.EN_PROCESO

    if observaciones:
        if orden_produccion.observaciones:
            orden_produccion.observaciones += f"\n{observaciones}"
        else:
            orden_produccion.observaciones = observaciones

    orden_produccion.save()

    # ---------------------------------------------------------
    # SOLO INICIAR LA PRIMERA OPERACIÓN
    # ---------------------------------------------------------

    primera_operacion = operaciones.first()

    primera_operacion.estado = ProduccionOperacion.Estado.EN_PROCESO
    primera_operacion.fecha_inicio_real = timezone.now()
    primera_operacion.save()

    return {
        "exito": True,
        "mensaje": "Producción iniciada correctamente",
        "orden_produccion": str(orden_produccion.id),
        "numero_orden": orden_produccion.numero,
        "fecha_inicio": primera_operacion.fecha_inicio_real,
        "operacion_iniciada": {
            "operacion_id": primera_operacion.id,
            "numero_operacion": primera_operacion.numero_operacion,
            "equipo": primera_operacion.equipo.nombre if primera_operacion.equipo else None,
            "estado": primera_operacion.estado,
        },
        "total_operaciones": operaciones.count(),
    }
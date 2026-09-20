"""
Servicio para la ejecución de operaciones de producción.

Responsabilidades:
- Iniciar una operación.
- Registrar producción mediante lotes y bobinas.
- Registrar scrap mediante ConsumoProduccion.
- Finalizar una operación.

La transferencia entre operaciones se gestiona
en service.py.
"""

from django.db import transaction
from django.utils import timezone
from decimal import Decimal

from apps.produccion.models import (
    ProduccionOperacion,
    LoteProduccion,
    BobinaProduccion,
    ConsumoProduccion,
    ResultadoProduccion,
)
from apps.recursos.models import Equipo
from apps.calidad.models import ControlCalidad

@transaction.atomic
def iniciar_operacion(
    produccion_operacion_id,
    usuario,
    observaciones="",
):
    """
    Inicia una operación de producción.

    Validaciones:
    - La operación debe estar pendiente.
    - El equipo debe estar operativo.
    - El equipo no debe estar ocupado.
    - Si existe una operación anterior:
        - debe estar completada;
        - debe tener control final aprobado.

    pendiente → en_proceso
    """

    operacion = (
        ProduccionOperacion.objects
        .select_for_update()
        .select_related(
            "orden_ruta",
            "ruta_operacion__ruta_paso",
        )
        .get(id=produccion_operacion_id)
    )

    # --------------------------------------------------
    # 1. VALIDAR ESTADO DE LA OPERACIÓN
    # --------------------------------------------------

    if operacion.estado != ProduccionOperacion.Estado.PENDIENTE:
        return {
            "exito": False,
            "mensaje": (
                "La operación debe estar en estado "
                "'pendiente' para poder iniciarse."
            ),
            "operacion": operacion.id,
        }
    # Bloquear el equipo durante la transaccion
    equipo = (
        Equipo.objects
        .select_for_update()
        .get(pk=operacion.equipo_id)
    )
    if equipo.estado != Equipo.Estado.OPERATIVO:
        return{
            "exito":False,
            "mensaje": f"El equipo '{equipo.nombre}' no está operativo.",
            "operacion": equipo.nombre,
        }
    equipo_ocupado = (
        ProduccionOperacion.objects
        .filter(
            equipo_id=equipo.id,
            estado=ProduccionOperacion.Estado.EN_PROCESO,
        )
        .exclude(id=operacion.id)
        .exists()
    )
    if equipo_ocupado:
        return{
            "exito": False,
            "mensaje": f"El equipo '{equipo.nombre}' esta siendo utilizado por otra operación",
            "operacion": operacion.id,
            "equipo": equipo.nombre,
        }

    # --------------------------------------------------
    # 2. VALIDAR EQUIPO
    # --------------------------------------------------

    if not operacion.equipo:
        return {
            "exito": False,
            "mensaje": (
                "La operación no tiene un equipo asignado."
            ),
            "operacion": operacion.id,
        }

    if operacion.equipo.estado != Equipo.Estado.OPERATIVO:
        return {
            "exito": False,
            "mensaje": (
                f"El equipo '{operacion.equipo.nombre}' "
                "no está operativo."
            ),
            "operacion": operacion.id,
            "equipo": operacion.equipo.nombre,
            "estado_equipo": operacion.equipo.estado,
        }

    # --------------------------------------------------
    # 3. VALIDAR QUE EL EQUIPO NO ESTÉ OCUPADO
    # --------------------------------------------------

    equipo_ocupado = (
        ProduccionOperacion.objects
        .filter(
            equipo=operacion.equipo,
            estado=ProduccionOperacion.Estado.EN_PROCESO,
        )
        .exclude(id=operacion.id)
        .exists()
    )

    if equipo_ocupado:
        return {
            "exito": False,
            "mensaje": (
                f"El equipo '{operacion.equipo.nombre}' "
                "está siendo utilizado por otra operación."
            ),
            "operacion": operacion.id,
            "equipo": operacion.equipo.nombre,
        }

    # --------------------------------------------------
    # 4. BUSCAR OPERACIÓN ANTERIOR
    # --------------------------------------------------

    operacion_anterior = None

    if operacion.numero_operacion > 1:
        operacion_anterior = (
            ProduccionOperacion.objects
            .select_for_update()
            .filter(
                orden_ruta=operacion.orden_ruta,
                numero_operacion=operacion.numero_operacion - 1,
            )
            .first()
        )

        if not operacion_anterior:
            return {
                "exito": False,
                "mensaje": (
                    "No se encontró la operación anterior "
                    "necesaria para iniciar esta operación."
                ),
                "operacion": operacion.id,
            }

        # --------------------------------------------------
        # 5. VALIDAR FINALIZACIÓN DE LA ANTERIOR
        # --------------------------------------------------

        if (
            operacion_anterior.estado
            != ProduccionOperacion.Estado.COMPLETADA
        ):
            return {
                "exito": False,
                "mensaje": (
                    "La operación anterior todavía no está "
                    "completada."
                ),
                "operacion": operacion.id,
                "operacion_anterior": operacion_anterior.id,
                "estado_anterior": operacion_anterior.estado,
            }

        # --------------------------------------------------
        # 6. VALIDAR CALIDAD FINAL
        # --------------------------------------------------

        calidad_aprobada = (
            operacion_anterior.controles_calidad
            .filter(
                momento_control=ControlCalidad.MomentoControl.FINAL,
                resultado=ControlCalidad.Resultado.APROBADO,
            )
            .exists()
        )

        if not calidad_aprobada:
            return {
                "exito": False,
                "mensaje": (
                    "La operación anterior no tiene un "
                    "control de calidad final aprobado."
                ),
                "operacion": operacion.id,
                "operacion_anterior": operacion_anterior.id,
            }

    # --------------------------------------------------
    # 7. INICIAR OPERACIÓN
    # --------------------------------------------------

    operacion.estado = ProduccionOperacion.Estado.EN_PROCESO
    operacion.fecha_inicio_real = timezone.now()

    if observaciones:
        operacion.observaciones += (
            f"\n[Inicio operación]: {observaciones}"
        )

    operacion.save(
        update_fields=[
            "estado",
            "fecha_inicio_real",
            "observaciones",
            "updated_at",
        ]
    )

    return {
        "exito": True,
        "mensaje": "Operación iniciada correctamente.",
        "operacion": operacion.id,
        "proceso": operacion.ruta_operacion.ruta_paso.nombre,
        "equipo": operacion.equipo.nombre,
        "estado": operacion.estado,
        "fecha_inicio": operacion.fecha_inicio_real,
    }


@transaction.atomic
def registrar_produccion(
    produccion_operacion_id,
    usuario,
    cantidad,
    unidad_medida,
    codigo_lote,
    bobinas,
    producto_version=None,
    observaciones="",
    datos_resultado=None,
):
    """
    Registra la producción obtenida en una operación.

    Extrusión:
    - Crea un LoteProduccion.
    - Crea una o varias BobinaProduccion.

    Flexografía / Confección:
    - Crea un LoteProduccion.
    - Crea un ResultadoProduccion.
    """

    operacion = ProduccionOperacion.objects.select_for_update().get(
        id=produccion_operacion_id
    )

    proceso = operacion.ruta_operacion.ruta_paso.nombre
    es_confeccion = proceso == "Confección"
    es_extrusion = proceso == "Extrusión"

    # Obtener automáticamente el producto final solamente en Confección
    if es_confeccion and producto_version is None:
        orden_produccion = operacion.orden_ruta.orden_produccion

        if orden_produccion.pedido_detalle_id:
            producto_version = (
                orden_produccion.pedido_detalle.producto_version
            )

    if operacion.estado != ProduccionOperacion.Estado.EN_PROCESO:
        return {
            "exito": False,
            "mensaje": (
                "Solo se puede registrar producción "
                "en una operación en proceso."
            ),
            "operacion": operacion.id,
        }

    if cantidad <= 0:
        return {
            "exito": False,
            "mensaje": "La cantidad producida debe ser mayor que cero.",
            "operacion": operacion.id,
        }

    # Las bobinas solamente son obligatorias para Extrusión
    if es_extrusion:

        if not bobinas:
            return {
                "exito": False,
                "mensaje": "Debe registrarse al menos una bobina.",
                "operacion": operacion.id,
            }

        peso_bobinas = sum(
            Decimal(str(bobina["peso"]))
            for bobina in bobinas
        )

        if round(peso_bobinas, 2) != round(
            Decimal(str(cantidad)),
            2,
        ):
            return {
                "exito": False,
                "mensaje": (
                    "La cantidad total de las bobinas "
                    "no coincide con la cantidad producida."
                ),
                "cantidad_producida": cantidad,
                "cantidad_bobinas": peso_bobinas,
            }

    lote = LoteProduccion.objects.create(
        produccion_operacion=operacion,
        producto_version=producto_version,
        codigo=codigo_lote,
        cantidad_total=cantidad,
        unidad_medida=unidad_medida,
        observaciones=observaciones,
    )

    datos_resultado = datos_resultado or {}

    resultado_produccion = ResultadoProduccion.objects.create(
        produccion_operacion=operacion,
        lote=lote,
        codigo=f"RES-{codigo_lote}",
        cantidad=cantidad,
        unidad_medida=unidad_medida,

        # Extrusión
        ancho_obtenido=datos_resultado.get("ancho_obtenido"),
        micraje_obtenido=datos_resultado.get("micraje_obtenido"),
        material_obtenido=datos_resultado.get("material_obtenido", ""),
        color_obtenido=datos_resultado.get("color_obtenido", ""),
        olor=datos_resultado.get("olor", ""),
        peso_obtenido=datos_resultado.get("peso_obtenido"),

        # Flexografía
        impresion=datos_resultado.get("impresion", False),
        colores_obtenidos=datos_resultado.get("colores_obtenidos", []),
        calidad_color=datos_resultado.get("calidad_color", ""),
        tonalidad=datos_resultado.get("tonalidad", ""),
        diseno=datos_resultado.get("diseno", ""),
        posicion_impresion=datos_resultado.get("posicion_impresion", ""),
        distancia_arriba=datos_resultado.get("distancia_arriba"),
        distancia_abajo=datos_resultado.get("distancia_abajo"),
        distancia_izquierda=datos_resultado.get("distancia_izquierda"),
        distancia_derecha=datos_resultado.get("distancia_derecha"),

        # Confección
        largo_obtenido=datos_resultado.get("largo_obtenido"),
        tipo_sello=datos_resultado.get("tipo_sello", ""),
        tipo_troquel=datos_resultado.get("tipo_troquel", ""),

        observaciones=datos_resultado.get(
            "observaciones",
            observaciones,
        ),
    )

    bobinas_creadas = []

    # Las bobinas solamente se crean en Extrusión
    if es_extrusion:

        for datos in bobinas:

            bobina = BobinaProduccion.objects.create(
                produccion_operacion=operacion,
                lote=lote,
                codigo=datos["codigo"],
                peso=datos["peso"],
                ancho=datos.get("ancho"),
                diametro=datos.get("diametro"),
                diametro_nucleo=datos.get("diametro_nucleo"),
                longitud=datos.get("longitud"),
                estado=BobinaProduccion.Estado.TERMINADA,
                calidad=BobinaProduccion.Calidad.PENDIENTE,
                observaciones=datos.get("observaciones", ""),
            )

            bobinas_creadas.append({
                "id": bobina.id,
                "codigo": bobina.codigo,
                "peso": bobina.peso,
            })

    # Se actualiza para Extrusión, Flexografía y Confección
    operacion.cantidad_producida += Decimal(str(cantidad))
    operacion.save(
        update_fields=[
            "cantidad_producida",
            "updated_at",
        ]
    )

    return {
        "exito": True,
        "mensaje": "Producción registrada correctamente.",
        "operacion": operacion.id,
        "lote": lote.id,
        "codigo_lote": lote.codigo,
        "cantidad_total": lote.cantidad_total,
        "bobinas": bobinas_creadas,
        "resultado_produccion": {
            "id": resultado_produccion.id,
            "codigo": resultado_produccion.codigo,
            "cantidad": resultado_produccion.cantidad,
            "unidad_medida": resultado_produccion.unidad_medida,
        },
    }


@transaction.atomic
def registrar_scrap(
    produccion_operacion_id,
    usuario,
    materia_prima_id,
    cantidad_entregada,
    cantidad_utilizada,
    cantidad_scrap,
    unidad_medida,
    observaciones="",
):
    """
    Registra el consumo y scrap de materia prima.

    El scrap se almacena en ConsumoProduccion.cantidad_scrap.
    """

    operacion = ProduccionOperacion.objects.get(
        id=produccion_operacion_id
    )

    if cantidad_scrap < 0:
        return {
            "exito": False,
            "mensaje": "La cantidad de scrap no puede ser negativa.",
        }

    consumo = ConsumoProduccion.objects.create(
        produccion_operacion=operacion,
        materia_prima_id=materia_prima_id,
        cantidad_entregada=cantidad_entregada,
        cantidad_utilizada=cantidad_utilizada,
        cantidad_scrap=cantidad_scrap,
        unidad_medida=unidad_medida,
        observaciones=observaciones,
    )

    return {
        "exito": True,
        "mensaje": "Consumo y scrap registrados correctamente.",
        "consumo": consumo.id,
        "cantidad_scrap": consumo.cantidad_scrap,
    }


@transaction.atomic
def finalizar_operacion(
    produccion_operacion_id,
    usuario,
    observaciones="",
):
    """
    Finaliza una operación de produccion.
    Validaciones:
     - La operacióln debe estar en proceso.

     Flujo:
     en_proceso -> completada
     La finalizacion de la Orden de Producción
     se gestion mediante completar_orden_produccion()
    """

    operacion = ProduccionOperacion.objects.select_for_update().get(
        id=produccion_operacion_id
    )

    if operacion.estado != ProduccionOperacion.Estado.EN_PROCESO:
        return {
            "exito": False,
            "mensaje": (
                "La operación debe estar en estado "
                "'en_proceso' para finalizarse."
            ),
            "operacion": operacion.id,
        }

    operacion.estado = ProduccionOperacion.Estado.COMPLETADA
    operacion.fecha_fin_real = timezone.now()

    if observaciones:
        operacion.observaciones += (
            f"\n[Finalización operación]: {observaciones}"
        )

    operacion.save(
        update_fields=[
            "estado",
            "fecha_fin_real",
            "observaciones",
            "updated_at",
        ]
    )

    return {
        "exito": True,
        "mensaje": "Operación finalizada correctamente.",
        "operacion": operacion.id,
        "proceso": operacion.ruta_operacion.ruta_paso.nombre,
        "equipo": operacion.equipo.nombre,
        "estado": operacion.estado,
        "fecha_fin": operacion.fecha_fin_real,
        "cantidad_producida": operacion.cantidad_producida,
    }
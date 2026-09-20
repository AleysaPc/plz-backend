"""
Servicio para gestión de cotizaciones.

Flujo:
SolicitudComercial → Cotizacion → CotizacionVersion → CotizacionDetalle
"""

from django.db import transaction
from django.utils import timezone
from apps.comercial.models import (
    SolicitudComercial,
    Cotizacion,
    CotizacionVersion,
    CotizacionDetalle,
)
from apps.productos.models import ProductoVersion
from apps.viabilidad.models import (
    EvaluacionComercial,
    EvaluacionViabilidad, 
)


@transaction.atomic
def crear_cotizacion(
    solicitud_comercial_id,
    usuario,
    fecha_vencimiento=None,
    observaciones="",
):
    """
    Crea una cotización para una solicitud comercial.
    
    Requiere que la solicitud tenga viabilidad aprobada.
    """
    solicitud = SolicitudComercial.objects.get(id=solicitud_comercial_id)
    
    especificaciones = solicitud.especificaciones_producto.all()
    if not especificaciones.exists():
        return {
            "exito": False,
            "mensaje": "La solicitud no tiene especificaciones de producto",
            "solicitud_comercial": solicitud_comercial_id,
        }
    
    especificacion = especificaciones.first()
    evaluaciones_comercial = EvaluacionComercial.objects.filter(
        especificacion_producto_solicitado=especificacion
    )
    
    if not evaluaciones_comercial.exists():
        return {
            "exito": False,
            "mensaje": "La especificación no tiene evaluación comercial asociada",
            "solicitud_comercial": solicitud_comercial_id,
            "especificacion": especificacion.id,
        }
    
    # Verificar que la evaluación comercial sea aprobada
    evaluacion_comercial = evaluaciones_comercial.last()
    if evaluacion_comercial.resultado.lower() not in ["aprobado", "aprobada", "viable"]:
        return {
            "exito": False,
            "mensaje": "La solicitud debe tener evaluación comercial aprobada para cotizar",
            "solicitud_comercial": solicitud_comercial_id,
            "resultado_evaluacion": evaluacion_comercial.resultado,
        }
    evaluacion_viabilidad = (
        EvaluacionViabilidad.objects
        .filter(evaluacion_comercial=evaluacion_comercial)
        .order_by("-id")
        .first()
    )

    if not evaluacion_viabilidad:
        return {
            "exito": False,
            "mensaje": "La especificación no tiene evaluación de viabilidad asociada",
            "solicitud_comercial": solicitud_comercial_id,
            "especificacion": especificacion.id,
        }

    if evaluacion_viabilidad.resultado != "viable":
        return {
            "exito": False,
            "mensaje": "La evaluación de viabilidad debe ser viable para poder cotizar",
            "evaluacion_viabilidad": evaluacion_viabilidad.id,
            "resultado": evaluacion_viabilidad.resultado,
        }

    if evaluacion_viabilidad.estado_aprobacion != "aprobada":
        return {
            "exito": False,
            "mensaje": "La evaluación de viabilidad debe estar aprobada para poder cotizar",
            "evaluacion_viabilidad": evaluacion_viabilidad.id,
            "estado_aprobacion": evaluacion_viabilidad.estado_aprobacion,
        }
        
    # Generar número de cotización
    numero_cotizacion = f"COT-{timezone.now().strftime('%Y%m%d')}-{solicitud.id}"
    
    # Verificar unicidad del número
    if Cotizacion.objects.filter(numero=numero_cotizacion).exists():
        # Si existe, agregar sufijo
        contador = 1
        while Cotizacion.objects.filter(numero=f"{numero_cotizacion}-{contador}").exists():
            contador += 1
        numero_cotizacion = f"{numero_cotizacion}-{contador}"
    
    # Crear cotización
    cotizacion = Cotizacion.objects.create(
        solicitud_comercial=solicitud,
        numero=numero_cotizacion,
        fecha_emision=timezone.now(),
        fecha_vencimiento=fecha_vencimiento,
        estado=Cotizacion.Estado.BORRADOR,
    )
    
    # Actualizar estado de solicitud
    solicitud.estado = SolicitudComercial.Estado.EN_NEGOCIACION
    solicitud.save(update_fields=["estado", "updated_at"])
    
    return {
        "exito": True,
        "mensaje": "Cotización creada correctamente",
        "cotizacion": cotizacion.id,
        "numero": cotizacion.numero,
        "solicitud_comercial": solicitud_comercial_id,
        "estado_solicitud": solicitud.estado,
    }


@transaction.atomic
def crear_version_cotizacion(
    cotizacion_id,
    usuario,
    moneda="BOB",
    precio_total=0,
    estado="borrador",
):
    """
    Crea una nueva versión de una cotización existente.
    """
    cotizacion = Cotizacion.objects.get(id=cotizacion_id)
    
    # Obtener última versión
    ultima_version = cotizacion.versiones.order_by('-version').first()
    nuevo_numero_version = 1 if not ultima_version else ultima_version.version + 1
    
    # Crear nueva versión
    version = CotizacionVersion.objects.create(
        cotizacion=cotizacion,
        version=nuevo_numero_version,
        moneda=moneda,
        precio_total=precio_total,
        estado=estado,
    )
    
    return {
        "exito": True,
        "mensaje": "Versión de cotización creada correctamente",
        "cotizacion_version": version.id,
        "version": version.version,
        "cotizacion": cotizacion_id,
    }


@transaction.atomic
def agregar_detalle_cotizacion(
    cotizacion_version_id,
    producto_version_id,
    cantidad,
    precio_unitario,
    usuario,
):
    """
    Agrega un detalle a una versión de cotización.

    Calcula automáticamente el precio total.
    """
    from decimal import Decimal

    # Obtener versión de cotización
    try:
        cotizacion_version = CotizacionVersion.objects.get(
            id=cotizacion_version_id
        )
    except CotizacionVersion.DoesNotExist:
        return {
            "exito": False,
            "mensaje": "La versión de cotización no existe",
        }

    # Obtener versión del producto
    try:
        producto_version = ProductoVersion.objects.get(
            id=producto_version_id
        )
    except ProductoVersion.DoesNotExist:
        return {
            "exito": False,
            "mensaje": "La versión del producto no existe",
        }

    cantidad = Decimal(str(cantidad))
    precio_unitario = Decimal(str(precio_unitario))

    if cantidad <= 0:
        return {
            "exito": False,
            "mensaje": "La cantidad debe ser mayor que cero",
        }

    if precio_unitario < 0:
        return {
            "exito": False,
            "mensaje": "El precio unitario no puede ser negativo",
        }

    precio_total = cantidad * precio_unitario

    # Crear detalle
    detalle = CotizacionDetalle.objects.create(
        cotizacion_version=cotizacion_version,
        producto_version=producto_version,
        cantidad=cantidad,
        precio_unitario=precio_unitario,
        precio_total=precio_total,
    )

    # Actualizar precio total de la versión
    cotizacion_version.precio_total += precio_total
    cotizacion_version.save(
        update_fields=["precio_total", "updated_at"]
    )

    return {
        "exito": True,
        "mensaje": "Detalle de cotización agregado correctamente",
        "cotizacion_detalle": detalle.id,
        "cotizacion_version": cotizacion_version_id,
        "producto_version": producto_version_id,
        "precio_total_detalle": float(precio_total),
        "precio_total_version": float(cotizacion_version.precio_total),
    }


@transaction.atomic
def aprobar_cotizacion(
    cotizacion_version_id,
    usuario,
    observaciones="",
):
    """
    Aprueba una versión de cotización.
    
    Cambia el estado de la versión a 'aceptada' y el estado de la cotización a 'activa'.
    """
    cotizacion_version = CotizacionVersion.objects.select_related('cotizacion').get(
        id=cotizacion_version_id
    )
    
    # Verificar que tenga detalles
    if not cotizacion_version.detalles.exists():
        return {
            "exito": False,
            "mensaje": "La versión de cotización no tiene detalles",
            "cotizacion_version": cotizacion_version_id,
        }
    if cotizacion_version.estado != CotizacionVersion.Estado.BORRADOR:
        return {
            "exito": False,
            "mensaje": "Solo se pueden aprobar versiones en estado borrador",
            "cotizacion_version": cotizacion_version_id,
            "estado_actual": cotizacion_version.estado,
        }
        
    # Actualizar estado de la versión
    cotizacion_version.estado = CotizacionVersion.Estado.ACEPTADA
    cotizacion_version.save(update_fields=["estado", "updated_at"])
    
    # Actualizar estado de la cotización
    cotizacion_version.cotizacion.estado = Cotizacion.Estado.ACTIVA
    cotizacion_version.cotizacion.save(update_fields=["estado", "updated_at"])
    
    return {
        "exito": True,
        "mensaje": "Cotización aprobada correctamente",
        "cotizacion_version": cotizacion_version_id,
        "cotizacion": cotizacion_version.cotizacion.id,
        "estado_cotizacion": cotizacion_version.cotizacion.estado,
    }


@transaction.atomic
def rechazar_cotizacion(
    cotizacion_version_id,
    usuario,
    motivo="",
):
    """
    Rechaza una versión de cotización.
    """
    cotizacion_version = CotizacionVersion.objects.select_related('cotizacion').get(
        id=cotizacion_version_id
    )
    estados_rechazables = [
        CotizacionVersion.Estado.BORRADOR,
        CotizacionVersion.Estado.ENVIADA,
    ]

    if cotizacion_version.estado not in estados_rechazables:
        return {
            "exito": False,
            "mensaje": "La versión de cotización no puede ser rechazada en su estado actual",
            "estado_actual": cotizacion_version.estado,
        }
    
    # Actualizar estado de la versión
    cotizacion_version.estado = CotizacionVersion.Estado.RECHAZADA
    cotizacion_version.save(update_fields=["estado", "updated_at"])
    
    
    return {
        "exito": True,
        "mensaje": "Cotización rechazada",
        "cotizacion_version": cotizacion_version_id,
        "motivo": motivo,
    }


@transaction.atomic
def cerrar_cotizacion(
    cotizacion_id,
    usuario,
    observaciones="",
):
    """
    Cierra una cotización.
    """
    cotizacion = Cotizacion.objects.get(id=cotizacion_id)
    
    cotizacion.estado = Cotizacion.Estado.CERRADA
    cotizacion.save(update_fields=["estado", "updated_at"])
    
    return {
        "exito": True,
        "mensaje": "Cotización cerrada correctamente",
        "cotizacion": cotizacion_id,
    }
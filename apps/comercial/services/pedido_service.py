"""
Servicio para gestión de pedidos.

Flujo:
CotizacionVersion → Pedido → PedidoDetalle
"""

from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.comercial.models import (
    CotizacionVersion,
    Cotizacion,
    Pedido,
    PedidoDetalle,
    SolicitudComercial,
)
from apps.productos.models import ProductoVersion


@transaction.atomic
def crear_pedido_desde_cotizacion(
    cotizacion_version_id,
    usuario,
    fecha_entrega_comprometida=None,
    observaciones="",
):
    """
    Crea un pedido a partir de una versión de cotización aprobada.
    
    Requiere que la cotización esté aprobada/aceptada.
    """
    cotizacion_version = CotizacionVersion.objects.select_related(
        'cotizacion__solicitud_comercial__cuenta_comercial'
    ).get(id=cotizacion_version_id)
    
    # Verificar que la versión esté aceptada
    if cotizacion_version.estado != CotizacionVersion.Estado.ACEPTADA:
        return {
            "exito": False,
            "mensaje": "Solo se pueden crear pedidos desde cotizaciones aceptadas",
            "cotizacion_version": cotizacion_version_id,
            "estado_actual": cotizacion_version.estado,
        }
    
    # Verificar que la cotización esté activa
    if cotizacion_version.cotizacion.estado != Cotizacion.Estado.ACTIVA:
        return {
            "exito": False,
            "mensaje": "La cotización debe estar activa para crear un pedido",
            "cotizacion": cotizacion_version.cotizacion.id,
            "estado_cotizacion": cotizacion_version.cotizacion.estado,
        }
    
    # Verificar que no exista ya un pedido para esta versión
    if cotizacion_version.pedidos.exists():
        return {
            "exito": False,
            "mensaje": "Ya existe un pedido para esta versión de cotización",
            "cotizacion_version": cotizacion_version_id,
        }
    
    cuenta_comercial = cotizacion_version.cotizacion.solicitud_comercial.cuenta_comercial
    
    # Generar número de pedido
    numero_pedido = f"PED-{timezone.now().strftime('%Y%m%d')}-{cotizacion_version.id}"
    
    # Verificar unicidad del número
    if Pedido.objects.filter(numero=numero_pedido).exists():
        contador = 1
        while Pedido.objects.filter(numero=f"{numero_pedido}-{contador}").exists():
            contador += 1
        numero_pedido = f"{numero_pedido}-{contador}"
    
    # Fecha de entrega por defecto (30 días)
    if not fecha_entrega_comprometida:
        from datetime import timedelta
        fecha_entrega_comprometida = timezone.now() + timedelta(days=30)
    
    # Crear pedido
    pedido = Pedido.objects.create(
        cotizacion_version=cotizacion_version,
        cuenta_comercial=cuenta_comercial,
        numero=numero_pedido,
        fecha_pedido=timezone.now(),
        estado=Pedido.Estado.EN_PROCESO,
        fecha_entrega_comprometida=fecha_entrega_comprometida,
        observaciones=observaciones,
    )
    
    # Actualizar estado de solicitud
    solicitud = cotizacion_version.cotizacion.solicitud_comercial
    solicitud.estado = SolicitudComercial.Estado.APROBADA
    solicitud.save(update_fields=["estado", "updated_at"])
    
    return {
        "exito": True,
        "mensaje": "Pedido creado correctamente desde cotización",
        "pedido": pedido.id,
        "numero": pedido.numero,
        "cotizacion_version": cotizacion_version_id,
        "cuenta_comercial": cuenta_comercial.id,
        "fecha_entrega_comprometida": pedido.fecha_entrega_comprometida,
    }


@transaction.atomic
def crear_detalle_pedido(
    pedido_id,
    producto_version_id,
    cantidad,
    precio_unitario,
    fecha_entrega_comprometida=None,
    observaciones="",
):
    """
    Crea un detalle de pedido.
    
    Hereda información de la cotización cuando corresponda.
    """
    from decimal import Decimal
    
    pedido = Pedido.objects.get(id=pedido_id)
    producto_version = ProductoVersion.objects.get(id=producto_version_id)
    
    # Calcular precio total
    precio_total = Decimal(str(cantidad)) * Decimal(str(precio_unitario))
    
    # Fecha de entrega por defecto (la del pedido)
    if not fecha_entrega_comprometida:
        fecha_entrega_comprometida = pedido.fecha_entrega_comprometida
    
    # Crear detalle
    detalle = PedidoDetalle.objects.create(
        pedido=pedido,
        producto_version=producto_version,
        cantidad=Decimal(str(cantidad)),
        precio_unitario=Decimal(str(precio_unitario)),
        precio_total=precio_total,
        fecha_entrega_comprometida=fecha_entrega_comprometida,
        observaciones=observaciones,
    )
    
    return {
        "exito": True,
        "mensaje": "Detalle de pedido creado correctamente",
        "pedido_detalle": detalle.id,
        "pedido": pedido_id,
        "producto_version": producto_version_id,
        "precio_total": float(precio_total),
    }


@transaction.atomic
def crear_detalles_pedido_desde_cotizacion(
    pedido_id,
    usuario,
):
    """
    Crea automáticamente los detalles de un pedido 
    copiando los detalles de la cotización asociada.
    """
    pedido = Pedido.objects.select_related('cotizacion_version').get(id=pedido_id)
    cotizacion_version = pedido.cotizacion_version
    
    # Verificar que no tenga detalles ya creados
    if pedido.detalles.exists():
        return {
            "exito": False,
            "mensaje": "El pedido ya tiene detalles creados",
            "pedido": pedido_id,
        }

    # Verificar que la cotización tenga detalles
    if not cotizacion_version.detalles.exists():
        return {
            "exito": False,
            "mensaje": "La versión de cotización no tiene detalles",
            "cotizacion_version": cotizacion_version.id,
            "pedido": pedido_id,
        }

    # Copiar detalles de la cotización
    detalles_creados = []
    for detalle_cotizacion in cotizacion_version.detalles.all():
        detalle_pedido = PedidoDetalle.objects.create(
            pedido=pedido,
            producto_version=detalle_cotizacion.producto_version,
            cantidad=detalle_cotizacion.cantidad,
            precio_unitario=detalle_cotizacion.precio_unitario,
            precio_total=detalle_cotizacion.precio_total,
            fecha_entrega_comprometida=pedido.fecha_entrega_comprometida,
            observaciones=f"Copiado de cotización versión {cotizacion_version.version}",
        )
        detalles_creados.append(detalle_pedido.id)
    
    return {
        "exito": True,
        "mensaje": f"Detalles de pedido creados correctamente ({len(detalles_creados)})",
        "pedido": pedido_id,
        "detalles_creados": detalles_creados,
        "cantidad_detalles": len(detalles_creados),
    }


@transaction.atomic
def confirmar_pedido(
    pedido_id,
    usuario,
    observaciones="",
):
    """
    Confirma un pedido para iniciar el proceso de producción.
    
    Cambia el estado del pedido a 'finalizado'.
    """
    pedido = Pedido.objects.get(id=pedido_id)
    
    # Verificar que tenga detalles
    if not pedido.detalles.exists():
        return {
            "exito": False,
            "mensaje": "El pedido no tiene detalles, no se puede confirmar",
            "pedido": pedido_id,
        }
    
    # Verificar que esté en proceso
    if pedido.estado != Pedido.Estado.EN_PROCESO:
        return {
            "exito": False,
            "mensaje": "Solo se pueden confirmar pedidos en proceso",
            "pedido": pedido_id,
            "estado_actual": pedido.estado,
        }
    
    # Actualizar estado
    pedido.estado = Pedido.Estado.FINALIZADO
    if observaciones:
        pedido.observaciones += f"\n[Confirmación]: {observaciones}"
    pedido.save(update_fields=["estado", "observaciones", "updated_at"])
    
    return {
        "exito": True,
        "mensaje": "Pedido confirmado correctamente",
        "pedido": pedido_id,
        "estado": pedido.estado,
    }


def obtener_pedido_con_detalles(pedido_id):
    """
    Obtiene un pedido con todos sus detalles y relacionados.
    """
    pedido = Pedido.objects.select_related(
        'cotizacion_version__cotizacion__solicitud_comercial',
        'cuenta_comercial',
    ).prefetch_related(
        'detalles__producto_version',
    ).get(id=pedido_id)
    
    detalles_data = []
    for detalle in pedido.detalles.all():
        detalles_data.append({
            "id": detalle.id,
            "producto_version": {
                "id": detalle.producto_version.id,
                "producto": detalle.producto_version.producto.nombre,
                "version": detalle.producto_version.numero_version,
                "material": detalle.producto_version.material,
            },
            "cantidad": float(detalle.cantidad),
            "precio_unitario": float(detalle.precio_unitario),
            "precio_total": float(detalle.precio_total),
            "fecha_entrega_comprometida": detalle.fecha_entrega_comprometida,
        })
    
    return {
        "pedido": {
            "id": pedido.id,
            "numero": pedido.numero,
            "fecha_pedido": pedido.fecha_pedido,
            "estado": pedido.estado,
            "fecha_entrega_comprometida": pedido.fecha_entrega_comprometida,
            "observaciones": pedido.observaciones,
            "cuenta_comercial": {
                "id": pedido.cuenta_comercial.id,
                "razon_social": pedido.cuenta_comercial.razon_social,
            },
            "cotizacion_version": {
                "id": pedido.cotizacion_version.id,
                "version": pedido.cotizacion_version.version,
                "precio_total": float(pedido.cotizacion_version.precio_total),
            },
        },
        "detalles": detalles_data,
        "cantidad_detalles": len(detalles_data),
    }
from decimal import Decimal

from django.db import transaction

from apps.inventario.models import (
    Inventario,
    MovimientoInventario,
)
from apps.produccion.models import (
    LoteProduccion,
)


@transaction.atomic
def registrar_entrada_produccion(
    lote_produccion_id,
    almacen_id,
    usuario,
    motivo="Ingreso de producción",
    observaciones="",
):
    """
    Registra el ingreso de un lote de producción al inventario.

    Flujo:

    LoteProduccion
        ↓
    ProductoVersion
        ↓
    Producto
        ↓
    Inventario
        ↓
    MovimientoInventario
    """

    lote = LoteProduccion.objects.select_for_update().get(
        id=lote_produccion_id
    )

    # --------------------------------------------------------
    # 1. Validar producto
    # --------------------------------------------------------

    if not lote.producto_version:
        return {
            "exito": False,
            "mensaje": (
                "El lote de producción no tiene "
                "un producto asociado."
            ),
        }

    producto = lote.producto_version.producto

    # --------------------------------------------------------
    # 2. Evitar ingreso duplicado del mismo lote
    # --------------------------------------------------------

    if MovimientoInventario.objects.filter(
        lote_produccion=lote,
        tipo_movimiento="entrada",
    ).exists():
        return {
            "exito": False,
            "mensaje": (
                "El lote de producción ya fue "
                "ingresado al inventario."
            ),
            "lote": lote.id,
        }

    # --------------------------------------------------------
    # 3. Obtener o crear inventario del producto
    # --------------------------------------------------------

    inventario, creado = Inventario.objects.get_or_create(
        almacen_id=almacen_id,
        producto=producto,
        materia_prima=None,
        pintura=None,
        defaults={
            "cantidad": Decimal("0"),
            "unidad_medida": lote.unidad_medida,
            "estado": Inventario.Estado.DISPONIBLE,
        },
    )

    # --------------------------------------------------------
    # 4. Actualizar stock
    # --------------------------------------------------------

    inventario.cantidad += Decimal(
        str(lote.cantidad_total)
    )

    inventario.unidad_medida = lote.unidad_medida
    inventario.estado = Inventario.Estado.DISPONIBLE

    inventario.save(
        update_fields=[
            "cantidad",
            "unidad_medida",
            "estado",
            "updated_at",
        ]
    )

    # --------------------------------------------------------
    # 5. Registrar movimiento
    # --------------------------------------------------------

    movimiento = MovimientoInventario.objects.create(
        inventario=inventario,
        lote_produccion=lote,
        produccion_operacion=lote.produccion_operacion,
        usuario=usuario,
        tipo_movimiento="entrada",
        cantidad=lote.cantidad_total,
        fecha=lote.created_at,
        motivo=motivo,
        observaciones=observaciones,
    )

    return {
        "exito": True,
        "mensaje": (
            "Entrada de producción registrada "
            "correctamente."
        ),
        "inventario": inventario.id,
        "producto": producto.id,
        "lote": lote.id,
        "movimiento": movimiento.id,
        "cantidad_ingresada": lote.cantidad_total,
        "cantidad_actual": inventario.cantidad,
        "almacen": almacen_id,
    }
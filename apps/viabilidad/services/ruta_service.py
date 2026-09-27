"""
Servicio para determinar la ruta de producción de un producto.

Separa la lógica de "qué procesos necesita el producto" de 
"qué máquinas pueden realizarlos".
"""

from apps.comercial.models import EspecificacionBolsaSolicitada

def determinar_ruta_producto(especificacion_producto):
    """
    Determina la ruta de producción según el tipo de producto
    y si requiere impresión.

    Reglas:
    - Bobina final sin impresión → Extrusión
    - Bolsa sin impresión → Extrusión → Confección
    - Bolsa con impresión → Extrusión → Flexografía → Confección
    """

    tiene_impresion = especificacion_producto.impresion
    es_bolsa = EspecificacionBolsaSolicitada.objects.filter(
        especificacion_producto_solicitado=especificacion_producto
    ).exists()

    if es_bolsa:
        if tiene_impresion:
            return ["extrusion", "flexografia", "confeccion"]

        return ["extrusion", "confeccion"]

    return ["extrusion"]


def validar_ruta_completa(ruta):
    """
    Valida que la ruta sea válida según las rutas posibles.

    Args:
        ruta: Lista de procesos

    Returns:
        dict: Con keys 'valida' (bool) y 'mensaje' (str)
    """
    rutas_validas = [
        ["extrusion"],
        ["extrusion", "confeccion"],
        ["extrusion", "flexografia", "confeccion"],
    ]

    if ruta in rutas_validas:
        return {
            "valida": True,
            "mensaje": "Ruta válida"
        }

    return {
        "valida": False,
        "mensaje": f"Ruta no válida: {ruta}. Rutas permitidas: {rutas_validas}"
    }


def obtener_descripcion_ruta(ruta):
    """
    Retorna una descripción legible de la ruta.

    Args:
        ruta: Lista de procesos

    Returns:
        str: Descripción de la ruta
    """
    descripciones = {
        "extrusion": "Extrusión",
        "flexografia": "Flexografía",
        "confeccion": "Confección",
    }

    procesos = [descripciones.get(p, p) for p in ruta]
    return " -> ".join(procesos)
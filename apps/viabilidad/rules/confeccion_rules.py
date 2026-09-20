from apps.viabilidad.services.dimensiones_producto_service import (
    obtener_ancho_bobina_intermedia,
)
def validar_material(especificacion, capacidad):
    """
    RT-C-01
    Verifica que el material solicitado
    sea compatible con la máquina de confección.
    """

    material_solicitado = (especificacion.material or "").strip().upper()
    materiales_permitidos = [
        material.strip().upper()
        for material in (capacidad.materiales or [])
    ]

    cumple = material_solicitado in materiales_permitidos

    return {
        "criterio": "material",
        "cumple": cumple,
        "valor_solicitado": material_solicitado,
        "valor_capacidad": materiales_permitidos,
        "mensaje": (
            "El material es compatible con la máquina."
            if cumple
            else
            "El material solicitado no es compatible con la máquina."
        ),
    }
def validar_ancho_bobina(especificacion_bolsa, capacidad):
    """
    RT-C-07
    Valida que el ancho de la bobina de entrada
    esté dentro del rango aceptado por la máquina.
    """

    ancho_bobina = obtener_ancho_bobina_intermedia(
        especificacion_bolsa
    )
    if ancho_bobina is None:
        return {
            "criterio": "ancho_bobina",
            "cumple": False,
            "valor_solicitado": None,
            "valor_capacidad": {
                "min": capacidad.bobina_ancho_min,
                "max": capacidad.bobina_ancho_max,
            },
            "mensaje":(
                "No se puedo determina el ancho de  "
                "la bobina intermedia"
            ),
        }
    
    cumple = (
        capacidad.bobina_ancho_min
        <= ancho_bobina
        <= capacidad.bobina_ancho_max
    )

    return {
        "criterio": "ancho_bobina",
        "cumple": cumple,
        "valor_solicitado": ancho_bobina,
        "valor_capacidad": {
            "min": capacidad.bobina_ancho_min,
            "max": capacidad.bobina_ancho_max,
        },
        "mensaje": (
            "El ancho de la bobina está dentro "
            "del rango permitido."
            if cumple
            else
            "El ancho de la bobina está fuera "
            "del rango permitido."
        ),
    }


def validar_tipo_sello(especificacion_bolsa, capacidad):
    """
    RT-C-02
    Verifica que el tipo de sello solicitado
    sea una de las opciones de sello que puede realizar
    la máquina de confección.
    """

    tipo_sello_solicitado = (
        especificacion_bolsa.tipo_sello or ""
    ).strip().lower()

    tipo_sello_capacidad = (
        capacidad.tipo_sello or ""
    ).strip().lower()

    if not tipo_sello_solicitado:
        return {
            "criterio": "tipo_sello",
            "cumple": True,
            "valor_solicitado": None,
            "valor_capacidad": tipo_sello_capacidad,
            "mensaje": "No se especificó un tipo de sello.",
        }

    if tipo_sello_capacidad == "ninguna":
        cumple = False
    else:
        capacidades_sello = [
            valor.strip()
            for valor in tipo_sello_capacidad.replace(",", "-").split("-")
            if valor.strip()
        ]

        # "fondo y precorte" debe reconocer "fondo"
        capacidades_sello = [
            valor.replace(" y precorte", "").strip()
            for valor in capacidades_sello
        ]

        cumple = tipo_sello_solicitado in capacidades_sello

    return {
        "criterio": "tipo_sello",
        "cumple": cumple,
        "valor_solicitado": tipo_sello_solicitado,
        "valor_capacidad": tipo_sello_capacidad,
        "mensaje": (
            "El tipo de sello es compatible con la máquina."
            if cumple
            else "El tipo de sello solicitado no es compatible con la máquina."
        ),
    }


def validar_tipo_troquel(especificacion_bolsa, capacidad):
    """
    RT-C-03
    Verifica que el tipo de troquel solicitado
    sea una de las opciones que puede realizar
    la máquina de confección.
    """

    tipo_troquel_solicitado = (
        especificacion_bolsa.tipo_troquel or ""
    ).strip().lower()

    tipo_troquel_capacidad = (
        capacidad.tipo_troquel or ""
    ).strip().lower()

    if not tipo_troquel_solicitado:
        return {
            "criterio": "tipo_troquel",
            "cumple": True,
            "valor_solicitado": None,
            "valor_capacidad": tipo_troquel_capacidad,
            "mensaje": "No se requiere troquelado.",
        }

    if tipo_troquel_capacidad == "ninguno":
        cumple = False
    else:
        capacidades_troquel = [
            valor.strip()
            for valor in tipo_troquel_capacidad.split(",")
            if valor.strip()
        ]

        cumple = tipo_troquel_solicitado in capacidades_troquel

    return {
        "criterio": "tipo_troquel",
        "cumple": cumple,
        "valor_solicitado": tipo_troquel_solicitado,
        "valor_capacidad": tipo_troquel_capacidad,
        "mensaje": (
            "El tipo de troquel es compatible con la máquina."
            if cumple
            else "El tipo de troquel solicitado no es compatible con la máquina."
        ),
    }


def validar_acabado_especial(especificacion_bolsa, capacidad):
    """
    RT-C-04
    Verifica que el acabado especial solicitado
    sea compatible con la máquina de confección.
    """

    acabado_solicitado = (
        especificacion_bolsa.acabado_especial or "").strip().lower()
    acabado_capacidad = (
        capacidad.acabado_especial or "" ).strip().lower()

    if not acabado_solicitado:
        return {
            "criterio": "acabado_especial",
            "cumple": True,
            "valor_solicitado": None,
            "valor_capacidad": acabado_capacidad,
            "mensaje": "No se requiere acabado especial.",
        }

    if not acabado_capacidad:
        return {
            "criterio": "acabado_especial",
            "cumple": False,
            "valor_solicitado": acabado_solicitado,
            "valor_capacidad": acabado_capacidad,
            "mensaje": "La máquina no soporta acabados especiales.",
        }

    cumple = acabado_solicitado == acabado_capacidad

    return {
        "criterio": "acabado_especial",
        "cumple": cumple,
        "valor_solicitado": acabado_solicitado,
        "valor_capacidad": acabado_capacidad,
        "mensaje": (
            "El acabado especial es compatible con la máquina."
            if cumple
            else "El acabado especial solicitado no es compatible con la máquina."
        ),
    }


def validar_ancho_producto(especificacion_bolsa, capacidad):
    """
    RT-C-05
    Valida que el ancho del producto terminado
    esté dentro del rango aceptado por la máquina.
    """

    ancho_producto = especificacion_bolsa.ancho_doblado

    if capacidad.producto_ancho_min is None or capacidad.producto_ancho_max is None:
        return {
            "criterio": "ancho_producto",
            "cumple": True,
            "valor_solicitado": ancho_producto,
            "valor_capacidad": {
                "min": capacidad.producto_ancho_min,
                "max": capacidad.producto_ancho_max,
            },
            "mensaje": "La máquina no tiene restricciones de ancho de producto.",
        }

    cumple = (
        capacidad.producto_ancho_min
        <= ancho_producto
        <= capacidad.producto_ancho_max
    )

    return {
        "criterio": "ancho_producto",
        "cumple": cumple,
        "valor_solicitado": ancho_producto,
        "valor_capacidad": {
            "min": capacidad.producto_ancho_min,
            "max": capacidad.producto_ancho_max,
        },
        "mensaje": (
            "El ancho del producto está dentro del rango permitido."
            if cumple
            else "El ancho del producto está fuera del rango permitido."
        ),
    }


def validar_largo_producto(especificacion_bolsa, capacidad):
    """
    RT-C-06
    Valida que el largo del producto terminado
    esté dentro del rango aceptado por la máquina.
    """

    largo_producto = especificacion_bolsa.largo_doblado

    cumple = (
        capacidad.largo_min
        <= largo_producto
        <= capacidad.largo_max
    )

    return {
        "criterio": "largo_producto",
        "cumple": cumple,
        "valor_solicitado": largo_producto,
        "valor_capacidad": {
            "min": capacidad.largo_min,
            "max": capacidad.largo_max,
        },
        "mensaje": (
            "El largo del producto está dentro del rango permitido."
            if cumple
            else "El largo del producto está fuera del rango permitido."
        ),
    }


def validar_fuelle_producto(especificacion_bolsa, capacidad):
    """
    RT-C-08
    Verifica si el fuelle solicitado es compatible
    con la capacidad de la máquina de confección.
    """

    if not especificacion_bolsa.fuelle:
        return {
            "criterio": "fuelle_producto",
            "cumple": True,
            "valor_solicitado": False,
            "valor_capacidad": {
                "min": capacidad.fuelle_min,
                "max": capacidad.fuelle_max,
            },
            "mensaje": "El producto no requiere fuelle.",
        }

    dimensiones = [
        especificacion_bolsa.fuelle_izquierdo,
        especificacion_bolsa.fuelle_derecho,
        especificacion_bolsa.fuelle_inferior,
        especificacion_bolsa.fuelle_superior,
    ]

    dimensiones_validas = [
        dimension
        for dimension in dimensiones
        if dimension is not None
    ]

    if not dimensiones_validas:
        return {
            "criterio": "fuelle_producto",
            "cumple": False,
            "valor_solicitado": None,
            "valor_capacidad": {
                "min": capacidad.fuelle_min,
                "max": capacidad.fuelle_max,
            },
            "mensaje": "Se requiere fuelle, pero no se especificó su dimensión.",
        }

    cumple = all(
        (
            capacidad.fuelle_min is None
            or dimension >= capacidad.fuelle_min
        )
        and
        (
            capacidad.fuelle_max is None
            or dimension <= capacidad.fuelle_max
        )
        for dimension in dimensiones_validas
    )

    return {
        "criterio": "fuelle_producto",
        "cumple": cumple,
        "valor_solicitado": dimensiones_validas,
        "valor_capacidad": {
            "min": capacidad.fuelle_min,
            "max": capacidad.fuelle_max,
        },
        "mensaje": (
            "Las dimensiones del fuelle son compatibles."
            if cumple
            else "Las dimensiones del fuelle están fuera del rango permitido."
        ),
    }
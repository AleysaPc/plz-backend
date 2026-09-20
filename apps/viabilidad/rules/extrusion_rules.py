"""
Su responsabilidad es responder preguntas como:
¿El material es compatible?
¿El ancho está dentro del rango?
¿El micraje está dentro del rango?
¿La cantidad de capas es compatible?
¿El fuelle está dentro de la capacidad?
"""
from decimal import Decimal

def _resultado(
    criterio,
    cumple,
    valor_solicitado,
    valor_capacidad,
    mensaje,
):
    """
    Devuelve el resultado estándar de una regla de viabilidad.
    """
    return {
        "criterio": criterio,
        "cumple": cumple,
        "valor_solicitado": valor_solicitado,
        "valor_capacidad": valor_capacidad,
        "mensaje": mensaje,
    }


def validar_material(especificacion, capacidad):
    """
    Verifica que el material solicitado sea compatible
    con la máquina de extrusión.
    """

    material = especificacion.material
    material_capacidad = capacidad.material

    cumple = material == material_capacidad

    return _resultado(
        criterio="material",
        cumple=cumple,
        valor_solicitado=material,
        valor_capacidad=material_capacidad,
        mensaje=(
            "El material es compatible con la máquina."
            if cumple
            else "El material solicitado no es compatible con la máquina."
        ),
    )


def validar_ancho(especificacion_bolsa, capacidad):
    """
    Verifica que el ancho doblado solicitado esté dentro
    del rango permitido por la máquina de extrusión.
    """

    ancho = especificacion_bolsa.ancho_doblado
    ancho_min = capacidad.ancho_min
    ancho_max = capacidad.ancho_max

    cumple = ancho_min <= ancho <= ancho_max

    return _resultado(
        criterio="ancho",
        cumple=cumple,
        valor_solicitado=ancho,
        valor_capacidad={
            "min": ancho_min,
            "max": ancho_max,
        },
        mensaje=(
            "El ancho solicitado está dentro del rango permitido."
            if cumple
            else "El ancho solicitado está fuera del rango permitido."
        ),
    )


def validar_micraje(especificacion, capacidad):
    """
    Verifica que el micraje solicitado esté dentro
    del rango permitido por la máquina.
    """

    micraje = especificacion.micraje

    if micraje is None:
        return _resultado(
            criterio="micronaje",
            cumple=False,
            valor_solicitado=None,
            valor_capacidad={
                "min": capacidad.micronaje_min,
                "max": capacidad.micronaje_max,
            },
            mensaje="No se especificó el micronaje solicitado.",
        )

    micraje = Decimal(str(micraje))

    cumple = (
        capacidad.micronaje_min
        <= micraje
        <= capacidad.micronaje_max
    )

    return _resultado(
        criterio="micronaje",
        cumple=cumple,
        valor_solicitado=micraje,
        valor_capacidad={
            "min": capacidad.micronaje_min,
            "max": capacidad.micronaje_max,
        },
        mensaje=(
            "El micronaje solicitado está dentro del rango permitido."
            if cumple
            else "El micronaje solicitado está fuera del rango permitido."
        ),
    )


def validar_capas(especificacion, capacidad):
    """
    Verifica que la cantidad de capas solicitada
    sea compatible con la capacidad de la máquina.
    """

    mapa_capas = {
        "monocapa": 1,
        "bicapa": 2,
        "tricapa": 3,
    }

    capas_solicitadas = mapa_capas.get(especificacion.capas)

    if capas_solicitadas is None:
        return _resultado(
            criterio="capas",
            cumple=False,
            valor_solicitado=especificacion.capas,
            valor_capacidad=capacidad.capas,
            mensaje="La cantidad de capas solicitada no es válida.",
        )

    cumple = capas_solicitadas <= capacidad.capas

    return _resultado(
        criterio="capas",
        cumple=cumple,
        valor_solicitado=especificacion.capas,
        valor_capacidad=capacidad.capas,
        mensaje=(
            "La cantidad de capas es compatible."
            if cumple
            else "La cantidad de capas solicitada no es compatible con la máquina."
        ),
    )


def validar_fuelle(especificacion_bolsa, capacidad):
    """
    Verifica si el fuelle solicitado es compatible
    con la capacidad de la máquina.
    """

    if not especificacion_bolsa.fuelle:
        return _resultado(
            criterio="fuelle",
            cumple=True,
            valor_solicitado=False,
            valor_capacidad={
                "min": capacidad.fuelle_minimo,
                "max": capacidad.fuelle_maximo,
            },
            mensaje="El producto no requiere fuelle.",
        )

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
        return _resultado(
            criterio="fuelle",
            cumple=False,
            valor_solicitado=None,
            valor_capacidad={
                "min": capacidad.fuelle_minimo,
                "max": capacidad.fuelle_maximo,
            },
            mensaje="Se requiere fuelle, pero no se especificó su dimensión.",
        )

    fuelle_min = capacidad.fuelle_minimo
    fuelle_max = capacidad.fuelle_maximo

    if fuelle_min is None or fuelle_max is None:
        return _resultado(
            criterio="fuelle",
            cumple=False,
            valor_solicitado=dimensiones_validas,
            valor_capacidad={
                "min": fuelle_min,
                "max": fuelle_max,
            },
            mensaje="La máquina no tiene definido un rango de fuelle.",
        )

    cumple = all(
        fuelle_min <= dimension <= fuelle_max
        for dimension in dimensiones_validas
    )

    return _resultado(
        criterio="fuelle",
        cumple=cumple,
        valor_solicitado=dimensiones_validas,
        valor_capacidad={
            "min": fuelle_min,
            "max": fuelle_max,
        },
        mensaje=(
            "Las dimensiones del fuelle son compatibles."
            if cumple
            else "Las dimensiones del fuelle están fuera del rango permitido."
        ),
    )
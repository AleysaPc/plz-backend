from apps.viabilidad.services.dimensiones_producto_service import (
    obtener_ancho_bobina_intermedia,
)

def validar_ancho(especificacion_bolsa, capacidad):
    """
    Valida que el ancho de la bobina intermedia
    esté dentro del rango permitido por la capacidad
    flexográfica.
    """

    ancho = obtener_ancho_bobina_intermedia(
        especificacion_bolsa
    )

    if ancho is None:
        return {
            "criterio": "ancho_bobina",
            "cumple": False,
            "valor_solicitado": None,
            "valor_capacidad": {
                "min": capacidad.ancho_min,
                "max": capacidad.ancho_max,
            },
            "mensaje": (
                "No se pudo determinar el ancho "
                "de la bobina intermedia."
            ),
        }

    cumple = (
        capacidad.ancho_min
        <= ancho
        <= capacidad.ancho_max
    )

    return {
        "criterio": "ancho_bobina",
        "cumple": cumple,
        "valor_solicitado": ancho,
        "valor_capacidad": {
            "min": capacidad.ancho_min,
            "max": capacidad.ancho_max,
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

def validar_colores(especificacion, capacidad):
    """
    Valida que la cantidad de colores solicitada
    esté dentro de la capacidad de la máquina.
    """
    cantidad_colores = len(
        especificacion.color_impresion
    )

    cumple = (
        capacidad.colores_min
        <= cantidad_colores
        <= capacidad.colores_max
    )

    return {
        "criterio": "colores",
        "cumple": cumple,
        "valor_solicitado": cantidad_colores,
        "valor_capacidad": {
            "min": capacidad.colores_min,
            "max": capacidad.colores_max,
        },
        "mensaje": (
            "La cantidad de colores está dentro del rango permitido."
            if cumple
            else "La cantidad de colores está fuera del rango permitido."
        ),
    }


def validar_cara_impresion(especificacion, capacidad):
    """
    Valida la cara o caras donde se requiere impresión.
    """

    cara = especificacion.cara_impresion

    capacidades = {
        "anverso": capacidad.puede_anverso,
        "reverso": capacidad.puede_reverso,
        "ambas": capacidad.puede_ambas_caras,
    }

    cumple = capacidades.get(cara, False)

    return {
        "criterio": "cara_impresion",
        "cumple": cumple,
        "valor_solicitado": cara,
        "valor_capacidad": capacidades,
        "mensaje": (
            "La cara de impresión es compatible con la máquina."
            if cumple
            else "La cara de impresión no es compatible con la máquina."
        ),
    }


def validar_tratamiento_impresion(
    especificacion,
    capacidad,
):
    """
    Valida el tratamiento de impresión solicitado.
    """

    tratamiento = especificacion.tratamiento_impresion

    if tratamiento == "degradado":
        cumple = capacidad.puede_degradado

    elif tratamiento == "trameado":
        cumple = capacidad.puede_trameado

    else:
        cumple = True

    return {
        "criterio": "tratamiento_impresion",
        "cumple": cumple,
        "valor_solicitado": tratamiento,
        "valor_capacidad": {
            "puede_degradado": capacidad.puede_degradado,
            "puede_trameado": capacidad.puede_trameado,
        },
        "mensaje": (
            "El tratamiento de impresión es compatible."
            if cumple
            else "El tratamiento de impresión no es compatible con la máquina."
        ),
    }


def validar_cliche(
    especificacion,
    cliches,
):
    """
    Valida que exista un cliché activo asociado
    al diseño solicitado.
    """

    diseno = getattr(
        especificacion,
        "diseno",
        None,
    )

    if not diseno:
        cumple = False
    else:
        cumple = cliches.filter(
            diseno=diseno,
            estado="activo",
        ).exists()

    return {
        "criterio": "cliche",
        "cumple": cumple,
        "valor_solicitado": (
            diseno.id
            if diseno
            else None
        ),
        "valor_capacidad": (
            "cliché activo disponible"
        ),
        "mensaje": (
            "Existe un cliché activo para el diseño solicitado."
            if cumple
            else "No existe un cliché activo para el diseño solicitado."
        ),
    }


def validar_rodillo(
    capacidad,
    rodillos,
):
    """
    Valida que exista al menos un rodillo disponible
    asociado a la capacidad flexográfica.
    """

    cumple = rodillos.filter(
        capacidad_flexografia=capacidad,
        estado="disponible",
    ).exists()

    return {
        "criterio": "rodillo",
        "cumple": cumple,
        "valor_solicitado": "rodillo requerido",
        "valor_capacidad": "rodillo disponible",
        "mensaje": (
            "Existe un rodillo disponible para la máquina."
            if cumple
            else "No existe un rodillo disponible para la máquina."
        ),
    }
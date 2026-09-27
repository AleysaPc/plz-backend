"""
Que máquinas cunplen, cual recomiendo y como guardo el resultado. 
"""
from django.utils import timezone
from decimal import Decimal
from apps.recursos.models import (
    CapacidadExtrusion,
    Equipo,
)
from apps.viabilidad.models import (
    ResultadoViabilidad,
)
from apps.viabilidad.rules.extrusion_rules import (
    validar_material,
    validar_ancho,
    validar_micraje,
    validar_capas,
    validar_fuelle,
)

def evaluar_maquina_extrusion(
    especificacion,
    especificacion_bolsa,
    especificacion_bobina,
    capacidad,
):
    """
    Evalúa una máquina de extrusión contra una especificación
    de producto solicitada.
    """

    ancho_requerido = obtener_ancho_requerido_extrusion(
        especificacion_bolsa=especificacion_bolsa,
        especificacion_bobina=especificacion_bobina,
    )

    resultados = [
        validar_material(
            especificacion,
            capacidad,
        ),
        validar_ancho(
            ancho_requerido,
            capacidad,
        ),
        validar_micraje(
            especificacion,
            capacidad,
        ),
        validar_capas(
            especificacion,
            capacidad,
        ),
    ]

    if especificacion_bolsa is not None:
        resultados.append(
            validar_fuelle(
                especificacion_bolsa,
                capacidad,
            )
        )

    cumple_todo = all(
        resultado["cumple"]
        for resultado in resultados
    )

    equipo = capacidad.maquinaria.equipo

    return {
        "resultado": "viable" if cumple_todo else "no_viable",
        "cumple": cumple_todo,
        "disponibilidad": equipo.estado,
        "criterios": resultados,
        "observaciones": (
            "La máquina cumple todos los criterios de extrusión."
            if cumple_todo
            else "La máquina no cumple uno o más criterios de extrusión."
        ),
    }
def evaluar_extrusion(
    especificacion,
    especificacion_bolsa,
    especificacion_bobina,
    ):
    """
    Evalúa todas las máquinas de extrusión registradas
    en el sistema.
    """

    capacidades = (
        CapacidadExtrusion.objects
        .select_related("maquinaria__equipo")
        .filter(
            material=especificacion.material
        )
    )

    resultados = []

    for capacidad in capacidades:

        resultado = evaluar_maquina_extrusion(
            especificacion=especificacion,
            especificacion_bolsa=especificacion_bolsa,
            especificacion_bobina=especificacion_bobina,
            capacidad=capacidad,
        )

        resultados.append({
            "capacidad_id": capacidad.id,
            "maquinaria_id": capacidad.maquinaria.id,
            "equipo_id": capacidad.maquinaria.equipo.id,
            "equipo": capacidad.maquinaria.equipo.nombre,
            **resultado,
        })

    return resultados

def convertir_a_json(valor):
    """
    Convierte valores Decimal a float para poder
    almacenarlos correctamente en JSONField.
    """

    if isinstance(valor, Decimal):
        return float(valor)

    if isinstance(valor, dict):
        return {
            clave: convertir_a_json(valor)
            for clave, valor in valor.items()
        }

    if isinstance(valor, list):
        return [
            convertir_a_json(item)
            for item in valor
        ]

    return valor

def consolidar_resultados_extrusion(resultados):
    """
    Consolida los resultados obtenidos de las máquinas
    de extrusión.

    No guarda información en la base de datos.
    """

    maquinas_viables = []
    maquinas_no_viables = []
    maquinas_no_disponibles = []

    for resultado in resultados:

        if resultado["disponibilidad"] != "operativo":
            maquinas_no_disponibles.append(resultado)
            continue

        if resultado["cumple"]:
            maquinas_viables.append(resultado)
        else:
            maquinas_no_viables.append(resultado)

    return {
        "viable": len(maquinas_viables) > 0,
        "cantidad_viables": len(maquinas_viables),
        "maquinas_viables": maquinas_viables,
        "maquinas_no_viables": maquinas_no_viables,
        "maquinas_no_disponibles": maquinas_no_disponibles,
    }

def seleccionar_alternativa_extrusion(resultados):
    """
    Selecciona una máquina recomendada entre las alternativas
    técnicamente viables y operativas.

    No guarda información en la base de datos.
    """

    maquinas_viables = [
        resultado
        for resultado in resultados
        if (
            resultado["cumple"]
            and resultado["disponibilidad"] == "operativo"
        )
    ]

    if not maquinas_viables:
        return {
            "hay_alternativa": False,
            "recomendada": None,
            "alternativas": [],
        }

    # Por ahora no aplicamos un puntaje adicional.
    # Se toma como recomendada la primera alternativa viable.
    recomendada = maquinas_viables[0]

    alternativas = maquinas_viables[1:]

    return {
        "hay_alternativa": True,
        "recomendada": recomendada,
        "alternativas": alternativas,
    }
def calcular_puntaje_extrusion(resultado):
    """
    Calcula el puntaje de viabilidad de una máquina
    a partir de los criterios evaluados.
    """

    criterios = resultado.get("criterios", [])

    if not criterios:
        return 0

    criterios_cumplidos = sum(
        1
        for criterio in criterios
        if criterio["cumple"]
    )

    total_criterios = len(criterios)

    puntaje = (
        criterios_cumplidos / total_criterios
    ) * 100

    return round(puntaje, 2)

def preparar_resultado_viabilidad_extrusion(
    resultado,
    es_recomendada=False,
):
    """
    Prepara el resultado de una máquina de extrusión
    para posteriormente crear un ResultadoViabilidad.
    """

    puntaje = calcular_puntaje_extrusion(resultado)

    criterios = resultado.get("criterios", [])

    return {
        "equipo": resultado["equipo"],
        "resultado": resultado["resultado"],
        "puntaje_viabilidad": puntaje,
        "criterios_evaluados": convertir_a_json(
            criterios
        ),
        "es_recomendada": es_recomendada,
        "requiere_adaptacion": False,
        "adaptacion_propuesta": "",
        "observacion": resultado["observaciones"],
    }

def guardar_resultados_viabilidad_extrusion(
    resultados,
    evaluacion_proceso,
):
    """
    Guarda o actualiza los resultados de extrusión
    asociados a una EvaluacionProceso.

    Para una misma evaluación y equipo:
    - crea el resultado si no existe;
    - actualiza el resultado si ya existe.

    Evita duplicados al repetir una evaluación.
    """

    seleccion = seleccionar_alternativa_extrusion(
        resultados
    )

    recomendada = seleccion["recomendada"]

    resultados_guardados = []

    for resultado in resultados:

        equipo = Equipo.objects.get(
            id=resultado["equipo_id"]
        )

        es_recomendada = (
            recomendada is not None
            and resultado["equipo"]
            == recomendada["equipo"]
        )

        resultado_preparado = (
            preparar_resultado_viabilidad_extrusion(
                resultado,
                es_recomendada=es_recomendada,
            )
        )

        resultado_viabilidad, creado = (
            ResultadoViabilidad.objects.update_or_create(
                evaluacion_proceso=evaluacion_proceso,
                equipo=equipo,
                defaults={
                    "usuario": evaluacion_proceso.usuario,
                    "resultado": (
                        resultado_preparado[
                            "resultado"
                        ]
                    ),
                    "puntaje_viabilidad": (
                        resultado_preparado[
                            "puntaje_viabilidad"
                        ]
                    ),
                    "criterios_evaluados": (
                        resultado_preparado[
                            "criterios_evaluados"
                        ]
                    ),
                    "es_recomendada": (
                        resultado_preparado[
                            "es_recomendada"
                        ]
                    ),
                    "requiere_adaptacion": (
                        resultado_preparado[
                            "requiere_adaptacion"
                        ]
                    ),
                    "adaptacion_propuesta": (
                        resultado_preparado[
                            "adaptacion_propuesta"
                        ]
                    ),
                    "observacion": (
                        resultado_preparado[
                            "observacion"
                        ]
                    ),
                    "fecha_evaluacion": timezone.now(),
                },
            )
        )

        resultados_guardados.append(
            {
                "objeto": resultado_viabilidad,
                "creado": creado,
            }
        )

    return resultados_guardados

def evaluar_extrusion_completa(
    especificacion,
    especificacion_bolsa,
    especificacion_bobina,
):
    """
    Ejecuta el flujo completo de viabilidad de extrusión.

    Flujo:
    1. Evalúa las capacidades de las máquinas.
    2. Consolida los resultados.
    3. Selecciona la alternativa recomendada.
    4. Calcula el puntaje.
    5. Prepara los resultados para persistencia.

    No guarda información en la base de datos.
    """

    resultados = evaluar_extrusion(
        especificacion=especificacion,
        especificacion_bolsa=especificacion_bolsa,
        especificacion_bobina=especificacion_bobina,
    )

    consolidado = consolidar_resultados_extrusion(
        resultados
    )

    seleccion = seleccionar_alternativa_extrusion(
        resultados
    )

    resultados_preparados = []

    recomendada = seleccion["recomendada"]

    for resultado in resultados:

        es_recomendada = (
            recomendada is not None
            and resultado["equipo"]
            == recomendada["equipo"]
        )

        resultado_preparado = (
            preparar_resultado_viabilidad_extrusion(
                resultado,
                es_recomendada=es_recomendada,
            )
        )

        resultados_preparados.append(
            resultado_preparado
        )

    return {
        "proceso": "extrusion",

        "viable": consolidado["viable"],

        "cantidad_viables": (
            consolidado["cantidad_viables"]
        ),

        # Resultados originales de las reglas
        "resultados_evaluacion": resultados,

        # Resultados preparados para ResultadoViabilidad
        "resultados": resultados_preparados,

        "recomendada": (
            seleccion["recomendada"]
        ),

        "alternativas": (
            seleccion["alternativas"]
        ),

        "no_viables": (
            consolidado["maquinas_no_viables"]
        ),

        "no_disponibles": (
            consolidado["maquinas_no_disponibles"]
        ),
    }
def obtener_ancho_requerido_extrusion(
    especificacion_bolsa=None,
    especificacion_bobina=None,
):
    """
    Determina el ancho de película que debe producir Extrusión.

    Bolsa con fuelle:
        ancho_doblado

    Bolsa sin fuelle:
        ancho_desdoblado

    Bobina:
        ancho
    """

    if especificacion_bobina is not None:
        return especificacion_bobina.ancho

    if especificacion_bolsa is not None:

        if especificacion_bolsa.fuelle:
            return especificacion_bolsa.ancho_doblado

        return especificacion_bolsa.ancho_desdoblado

    return None
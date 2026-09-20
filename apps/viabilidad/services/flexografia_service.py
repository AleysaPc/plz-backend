from apps.viabilidad.rules.flexografia_rules import (
    validar_ancho,
    validar_colores,
    validar_cara_impresion,
    validar_tratamiento_impresion,
    validar_cliche,
    validar_rodillo,
)

def evaluar_maquina_flexografia(
    especificacion,
    especificacion_bolsa,
    capacidad,
):
    """
    Evalúa una máquina flexográfica contra
    una especificación de producto.

    No guarda información en la base de datos.
    """

    from apps.recursos.models import Cliche, Rodillo

    cliches = Cliche.objects.filter(
        maquinaria=capacidad.maquinaria
    )

    rodillos = Rodillo.objects.filter(
        capacidad_flexografia=capacidad
    )

    resultados = [
        validar_ancho(
            especificacion_bolsa,
            capacidad,
        ),

        validar_colores(
            especificacion,
            capacidad,
        ),

        validar_cara_impresion(
            especificacion,
            capacidad,
        ),

        validar_tratamiento_impresion(
            especificacion,
            capacidad,
        ),

        validar_cliche(
            especificacion,
            cliches,
        ),

        validar_rodillo(
            capacidad,
            rodillos,
        ),
    ]

    cumple_todo = all(
        resultado["cumple"]
        for resultado in resultados
    )

    equipo = capacidad.maquinaria.equipo

    return {
        "resultado": (
            "viable"
            if cumple_todo
            else "no_viable"
        ),

        "cumple": cumple_todo,

        "disponibilidad": equipo.estado,

        "criterios": resultados,

        "observaciones": (
            "La máquina cumple todos los criterios de flexografía."
            if cumple_todo
            else "La máquina no cumple uno o más criterios de flexografía."
        ),
    }
def evaluar_flexografia(
    especificacion,
    especificacion_bolsa,
):
    """
    Evalúa todas las capacidades flexográficas
    registradas en el sistema.
    """

    from apps.recursos.models import CapacidadFlexografia

    capacidades = (
        #Busca todas las capacidadFlexografia
        CapacidadFlexografia.objects
        .select_related("maquinaria__equipo")
        .filter(
            maquinaria__area_produccion__nombre="Flexografía"
        )
    )

    resultados = []

    for capacidad in capacidades:
                    #Evalua cada maquina 
        resultado = evaluar_maquina_flexografia(
            especificacion=especificacion,
            especificacion_bolsa=especificacion_bolsa,
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

#Esta función recibe los resultados de evaular_flexografia()
#Ademas determina si existe al menos una maquina viable
def consolidar_resultados_flexografia(resultados):
    """
    Consolida los resultados de las máquinas flexográficas.

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

#Esta funcion de las maquinas visibles F1, F2, F3 selecciona 
#Recomendad --> primera viable
#Alternativas --> Restantes
def seleccionar_alternativa_flexografia(resultados):
    """
    Selecciona una máquina flexográfica recomendada
    entre las alternativas técnicamente viables y operativas.

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

    recomendada = maquinas_viables[0]

    alternativas = maquinas_viables[1:]

    return {
        "hay_alternativa": True,
        "recomendada": recomendada,
        "alternativas": alternativas,
    }
def calcular_puntaje_flexografia(resultado):
    """
    Calcula el puntaje de viabilidad de una máquina
    flexográfica a partir de sus criterios evaluados.
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

def convertir_a_json_serializable(valor):
    """
    Convierte valores Decimal y estructuras anidadas
    a tipos compatibles con JSON.
    """

    from decimal import Decimal

    if isinstance(valor, Decimal):
        return float(valor)

    if isinstance(valor, list):
        return [
            convertir_a_json_serializable(item)
            for item in valor
        ]

    if isinstance(valor, dict):
        return {
            clave: convertir_a_json_serializable(valor)
            for clave, valor in valor.items()
        }

    return valor
def preparar_resultado_viabilidad_flexografia(
        resultado,
        es_recomendada=False
):
    """
    Prepara el resultado de una maquia flexografica para posteriromente
     crear ResultadoViabilidad
    """
    from apps.recursos.models import (
        CapacidadFlexografia,
        Cliche,
        Rodillo
    )

    puntaje = calcular_puntaje_flexografia(
        resultado
    )
    criterios = resultado.get(
        "criterios", []
    )

    capacidad = CapacidadFlexografia.objects.get(
        id=resultado["capacidad_id"]
    )
        # --------------------------------------------------------
    # OBTENER CLICHÉ
    # --------------------------------------------------------

    criterio_cliche = None

    for criterio in criterios:
        if criterio["criterio"] == "cliche":
            criterio_cliche = criterio
            break

    cliche = None

    if (
        criterio_cliche is not None
        and criterio_cliche["cumple"]
        and criterio_cliche["valor_solicitado"]
    ):
        cliche = (
            Cliche.objects
            .filter(
                maquinaria=capacidad.maquinaria,
                diseno_id=criterio_cliche["valor_solicitado"],
                estado="activo",
            )
            .first()
        )
    rodillo = (
        Rodillo.objects.filter(
            capacidad_flexografia=capacidad,
            estado="disponible",
        )
        .first()
    )
    criterios_json = convertir_a_json_serializable(
    criterios
    )
    return {
        "equipo": resultado["equipo"],
        "resultado": resultado["resultado"],
        "puntaje_viabilidad": puntaje,
        "criterios_evaluados":criterios_json,
        "es_recomendada":es_recomendada,
        "requiere_adaptacion":False,
        "adaptacion_propuesta":"",
        "observacion":resultado["observaciones"],
        "cliche":cliche,
        "rodillo":rodillo,

    }
from django.utils import timezone

from apps.recursos.models import Equipo
from apps.viabilidad.models import ResultadoViabilidad


def guardar_resultados_viabilidad_flexografia(
    resultados,
    evaluacion_proceso,
):
    """
    Guarda o actualiza los resultados de flexografía
    asociados a una EvaluacionProceso.

    Para una misma evaluación y equipo:
    - crea el resultado si no existe;
    - actualiza el resultado si ya existe.

    Evita duplicados al repetir una evaluación.
    """

    seleccion = seleccionar_alternativa_flexografia(
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
            preparar_resultado_viabilidad_flexografia(
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

                    "cliche": (
                        resultado_preparado["cliche"]
                    ),

                    "rodillo": (
                        resultado_preparado["rodillo"]
                    ),

                    "resultado": (
                        resultado_preparado["resultado"]
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


def evaluar_flexografia_completa(
    especificacion,
    especificacion_bolsa,
):
    """
    Ejecuta el flujo completo de viabilidad de flexografía.

    Flujo:
    1. Evalúa las capacidades de las máquinas.
    2. Consolida los resultados.
    3. Selecciona la alternativa recomendada.
    4. Calcula el puntaje.
    5. Prepara los resultados para persistencia.

    No guarda información en la base de datos.
    """

    resultados = evaluar_flexografia(
        especificacion=especificacion,
        especificacion_bolsa=especificacion_bolsa,
    )

    consolidado = consolidar_resultados_flexografia(
        resultados
    )

    seleccion = seleccionar_alternativa_flexografia(
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
            preparar_resultado_viabilidad_flexografia(
                resultado,
                es_recomendada=es_recomendada,
            )
        )

        resultados_preparados.append(
            resultado_preparado
        )

    return {
        "proceso": "flexografia",
        "viable": consolidado["viable"],
        "cantidad_viables": consolidado["cantidad_viables"],
        "requiere_seleccion_usuario": len(seleccion["alternativas"]) > 0,
        # Resultados originales de las reglas
        "resultados_evaluacion": resultados,

        # Resultados preparados para ResultadoViabilidad
        "resultados": resultados_preparados,

        "recomendada": seleccion["recomendada"],
        "alternativas": seleccion["alternativas"],

        "no_viables": consolidado["maquinas_no_viables"],
        "no_disponibles": consolidado["maquinas_no_disponibles"],
    }

"""What to measure to turn the program's assumptions into data.

The simulator carries more model than data: parameters that no source backs, and
weights fitted to reproduce ranges the literature already reports. This module
does not add another model. It states which experiment closes which gap, so a
week at the bench is worth more than any further coefficient.

Each assay names the gaps it resolves, by the ids registered in
`evidencia.PARAMETROS_SIN_FUENTE` and `hptlc`. Nothing here predicts anything.

Imports no Streamlit.
"""

from __future__ import annotations

from dataclasses import dataclass

from evidencia import PARAMETROS_SIN_FUENTE


@dataclass(frozen=True)
class Ensayo:
    """One experiment, and what it would settle."""

    id: str
    titulo: str
    pregunta: str
    cierra: tuple[str, ...]
    condiciones: tuple[str, ...]
    que_medir: str
    como_entra: str
    esfuerzo: str
    porque_ahora: str

    def __post_init__(self) -> None:
        """Every gap named must exist, so the plan cannot drift from the registry."""
        for clave in self.cierra:
            if clave not in PARAMETROS_SIN_FUENTE and not clave.startswith("hptlc:"):
                raise ValueError(f"ensayo '{self.id}' cierra un hueco inexistente: {clave}")


ENSAYOS: tuple[Ensayo, ...] = (
    Ensayo(
        id="prueba-aplicador",
        titulo="Prueba en frío del aplicador",
        pregunta="¿Pasa el NADES por el capilar sin taparlo ni cristalizar?",
        cierra=("hptlc:obstruccion-aplicador",),
        condiciones=(
            (
                "Primero en capilar de vidrio desechable o sembrador manual, NUNCA "
                "directo en el aplicador automático"
            ),
            "El NADES tal como se va a sembrar, y también diluido, para comparar",
            "Dejar una gota cargada en el capilar 30 min y volver a mirarla",
            (
                "Pesar una gota, esperar 30 min, volver a pesarla: da la velocidad de "
                "pérdida de agua, que es lo que dispara el problema"
            ),
        ),
        que_medir=(
            "Si sube y baja con fluidez; si al reposar aparece turbidez, sólido o "
            "anillo en la pared; cuánta masa pierde por evaporación en media hora. "
            "Un capilar que arrastra o deja residuo ya avisa antes de arriesgar la "
            "jeringa del equipo."
        ),
        como_entra=(
            "Cierra el vacío de obstrucción y arrastre del módulo HPTLC, que hoy está "
            "declarado sin fuente porque no hay literatura del cruce NADES × aplicador "
            "automático. También fija si hace falta diluir y cuánto."
        ),
        esfuerzo="Diez minutos y un capilar. Antes que cualquier otra cosa.",
        porque_ahora=(
            "Es lo único que puede dañar material caro. El agua es el único componente "
            "volátil del NADES: al perderse en un capilar de mucha superficie, la "
            "mezcla se aleja del eutéctico hidratado y la viscosidad sube unas ocho "
            "veces; el cloruro de colina puro funde a 302 °C, así que lo que quede no "
            "es un líquido espeso. La literatura reporta ChCl:ácido cítrico estable en "
            "frasco, pero nadie ha publicado qué pasa dentro de una aguja."
        ),
    ),
    Ensayo(
        id="serie-etanol",
        titulo="Serie de composición de etanol",
        pregunta="¿Cuál es la polaridad que realmente prefieren tus polifenoles?",
        cierra=("polaridad-optima", "sigma-polaridad"),
        condiciones=(
            "EtOH:H₂O 30:70 acidificado",
            "EtOH:H₂O 50:50 acidificado",
            "EtOH:H₂O 70:30 acidificado",
            "Misma matriz, misma masa, misma temperatura y tiempo en las tres",
        ),
        que_medir=(
            "Contenido de antocianinas y de flavonoles en cada extracto. El máximo de "
            "la curva frente a la composición da la polaridad óptima; el ancho de la "
            "curva da la σ."
        ),
        como_entra=(
            "Se cargan en la bitácora. Cada composición tiene su ETN por las ecuaciones "
            "de Spange 2024, así que la curva queda en unidades de polaridad "
            "directamente comparables con los NADES."
        ),
        esfuerzo="Tres extracciones y sus lecturas. Una jornada.",
        porque_ahora=(
            "Es el único experimento que vuelve afirmable la comparación principal. Hoy "
            "el orden entre NADES e hidroalcohólico se invierte dentro del rango de "
            "incertidumbre de un parámetro que nadie ha medido."
        ),
    ),
    Ensayo(
        id="cinetica-almacenamiento",
        titulo="Cinética de almacenamiento",
        pregunta="¿Cuánto llega vivo a la placa, y sustituye el NADES a la atmósfera inerte?",
        cierra=("estabilidad-pesos", "bonus-des"),
        condiciones=(
            "Dos solventes: el NADES elegido y el hidroalcohólico de referencia",
            "Lecturas a día 0, 7, 15 y 30",
            "Misma temperatura y exclusión de luz en ambos; sin purga de nitrógeno",
            "Un blanco de solvente sin extracto en cada serie",
        ),
        que_medir=(
            "Retención de antocianinas frente al día 0. La razón entre ambas series es "
            "la ventaja de conservación, medida en vez de calibrada."
        ),
        como_entra=(
            "Reemplaza los pesos calibrados de stability_score por un ajuste propio. "
            "Mientras no exista, el índice de estabilidad reproduce por construcción lo "
            "que ya dice la literatura y no puede usarse como evidencia."
        ),
        esfuerzo="Un mes de calendario, pero solo cuatro sesiones de medición.",
        porque_ahora=(
            "Es la hipótesis central de la tesis — que la red del solvente reemplaza al "
            "nitrógeno — y hoy está afirmada por cita ajena, no por dato propio. "
            "Empezar temprano importa: el reloj de 30 días corre solo."
        ),
    ),
    Ensayo(
        id="siembra-rp18",
        titulo="Siembra directa en RP-18",
        pregunta="¿Se puede sembrar el extracto NADES sin limpieza previa?",
        cierra=("hptlc:cruce-nades-rp18", "hptlc:obstruccion-aplicador"),
        condiciones=(
            "Placa RP-18 W F₂₅₄s, o con zona de concentración como resguardo",
            "El mismo extracto por duplicado: directo y con limpieza previa",
            "Un blanco de NADES sin extracto, para ver qué aporta la matriz sola",
            "Volumen según el ensayo de aptitud Ph. Eur.: 2 µL en placa de partícula fina",
        ),
        que_medir=(
            "Forma de banda y Rf. Si la banda directa no arrastra cola frente a la "
            "limpiada, la siembra directa funciona."
        ),
        como_entra=(
            "Cierra el vacío central del módulo HPTLC, que hoy sale SIN_EVIDENCIA "
            "porque el cruce NADES × RP-18 no existe en la literatura."
        ),
        esfuerzo="Una placa.",
        porque_ahora=(
            "De esto depende si el NADES conserva entera su ventaja de estabilidad o si "
            "pierde parte en un paso de limpieza. Y si resulta, no es solo un dato "
            "interno: es publicable, porque nadie lo ha reportado."
        ),
    ),
)
"""The assays, ordered by how much each unlocks."""


def huecos_abiertos() -> dict[str, tuple[str, ...]]:
    """Map each declared gap to the assays that would close it.

    Returns:
        Gap id to the ids of the assays covering it. A gap with an empty tuple has
        no experiment planned and is worth noticing.
    """
    mapa: dict[str, list[str]] = {k: [] for k in PARAMETROS_SIN_FUENTE}
    for ensayo in ENSAYOS:
        for clave in ensayo.cierra:
            mapa.setdefault(clave, []).append(ensayo.id)
    return {k: tuple(v) for k, v in mapa.items()}


def sin_ensayo() -> tuple[str, ...]:
    """Return the declared gaps that no planned assay would close."""
    return tuple(sorted(k for k, v in huecos_abiertos().items() if not v))

"""Plain-language reading of each computed property.

The simulator already cited its sources, but as footnotes under charts: the number
and the reason it matters were never in the same place. This module pairs each
computed quantity with what its value means for Berberis polyphenols, and with the
source that backs the claim.

Imports neither Streamlit nor the model: it reads the properties dict and nothing else.
"""

from __future__ import annotations

from dataclasses import dataclass

from evidencia import EVIDENCIA, Nivel


@dataclass(frozen=True)
class Lectura:
    """One property, read in plain language and backed by a source."""

    clave: str
    titulo: str
    valor: float
    unidad: str
    calificativo: str
    por_que: str
    fuente_id: str
    nivel: Nivel

    def __post_init__(self) -> None:
        """Keep the project-wide rule: no claim without a resolvable source."""
        if self.fuente_id not in EVIDENCIA:
            raise ValueError(f"lectura '{self.clave}' sin fuente resoluble")


def _tramo(valor: float, bajo: float, alto: float, etiquetas: tuple[str, str, str]) -> str:
    """Return the qualitative label for a value against two cut points."""
    if valor < bajo:
        return etiquetas[0]
    if valor > alto:
        return etiquetas[2]
    return etiquetas[1]


def explicar_propiedades(props: dict) -> tuple[Lectura, ...]:
    """Read the five NADES properties in plain language.

    Args:
        props: Output of `model.calculate_nades_properties`.

    Returns:
        One `Lectura` per property, each carrying its source.
    """
    return (
        Lectura(
            clave="polaridad",
            titulo="Polaridad (ETN)",
            valor=float(props["polaridad"]),
            unidad="",
            calificativo=_tramo(float(props["polaridad"]), 0.45, 0.80, ("baja", "media", "alta")),
            por_que=(
                "Las antocianinas 3-glicosiladas del calafate son muy polares: el azúcar "
                "unido al flavilio las lleva hacia la fracción acuosa. Un NADES de "
                "polaridad alta las solvata mejor, pero se aleja de los flavonoles, que "
                "son menos polares. Por eso el óptimo no es el máximo, y por eso el "
                "score combinado penaliza la asimetría entre fracciones."
            ),
            fuente_id="espino2016",
            nivel=Nivel.MEDIDO,
        ),
        Lectura(
            clave="viscosidad",
            titulo="Viscosidad",
            valor=float(props["viscosidad"]),
            unidad="cP",
            calificativo=_tramo(float(props["viscosidad"]), 50.0, 200.0, ("baja", "media", "alta")),
            por_que=(
                "La viscosidad gobierna la difusión del soluto desde la matriz vegetal: "
                "más viscoso extrae más lento y satura antes, y por eso el agua añadida "
                "sube el rendimiento aunque baje la polaridad relativa del solvente. Es "
                "además uno de los dos obstáculos que la literatura atribuye a los NADES "
                "en el análisis posterior por capa fina."
            ),
            fuente_id="liu2017",
            nivel=Nivel.MEDIDO,
        ),
        Lectura(
            clave="pH",
            titulo="pH efectivo",
            valor=float(props["pH"]),
            unidad="",
            calificativo=_tramo(
                float(props["pH"]), 3.5, 5.5, ("muy ácido", "ácido", "cercano a neutro")
            ),
            por_que=(
                "El pH decide en qué forma está la antocianina. Bajo pH 3 domina el "
                "catión flavilio, rojo y estable; sobre pH 4 aparecen la pseudobase "
                "carbinol y la chalcona, incoloras y lábiles. Un NADES ácido no solo "
                "extrae el pigmento: lo mantiene en la forma que se puede medir."
            ),
            fuente_id="espino2016",
            nivel=Nivel.MEDIDO,
        ),
        Lectura(
            clave="cap_hbd",
            titulo="Capacidad HBD efectiva",
            valor=float(props["cap_hbd"]),
            unidad="",
            calificativo=_tramo(float(props["cap_hbd"]), 1.5, 3.0, ("baja", "media", "alta")),
            por_que=(
                "Los donadores de puente de hidrógeno del solvente compiten con la pared "
                "celular por los hidroxilos fenólicos. Más capacidad HBD libera más "
                "polifenol unido a la matriz, que es justamente el mecanismo detrás de "
                "la fracción no extraíble (NEP)."
            ),
            fuente_id="espino2016",
            nivel=Nivel.MEDIDO,
        ),
        Lectura(
            clave="antioxidant_nades",
            titulo="Antioxidante del NADES",
            valor=float(props["antioxidant_nades"]),
            unidad="",
            calificativo=_tramo(
                float(props["antioxidant_nades"]), 0.25, 0.55, ("bajo", "medio", "alto")
            ),
            por_que=(
                "En este trabajo el NADES sustituye a la atmósfera inerte: el "
                "laboratorio no tiene línea de nitrógeno, y la hipótesis es que la red "
                "supramolecular del solvente aporta por sí sola la protección frente a "
                "oxidación. Este número es esa hipótesis, cuantificada."
            ),
            fuente_id="dai2013",
            nivel=Nivel.INFERIDO,
        ),
    )

"""HPTLC direct-spotting compatibility for NADES extracts.

Every emitted value carries a resolvable source. Where the literature is silent
the module declares the gap instead of producing a number: that distinction is
the point of the module, not a limitation of it.

Imports neither Streamlit nor the extraction model, so it can be tested and reused
(notably by SimEluent) on its own.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from evidencia import EVIDENCIA, Nivel


@dataclass(frozen=True)
class Placa:
    """A real catalogued plate with the specifications the model needs."""

    id: str
    nombre: str
    catalogo: str
    modo: str
    grado: str
    particula_um: tuple[float, float]
    espesor_um: float
    humectable_agua: bool
    indicador: str
    zona_concentracion: bool

    def __post_init__(self) -> None:
        """Validate the fields the verdict logic branches on."""
        if self.modo not in {"NP", "RP"}:
            raise ValueError("placa.modo debe ser 'NP' o 'RP'")
        if self.grado not in {"TLC", "HPTLC"}:
            raise ValueError("placa.grado debe ser 'TLC' o 'HPTLC'")
        if self.indicador not in {"F254", "F254s", "ninguno"}:
            raise ValueError("placa.indicador debe ser 'F254', 'F254s' o 'ninguno'")


PLACAS: dict[str, Placa] = {
    "silice-60G-F254": Placa(
        id="silice-60G-F254",
        nombre="TLC Sílica 60G F254 (yeso) — la del laboratorio",
        catalogo="1.00390",
        modo="NP",
        grado="TLC",
        particula_um=(10.0, 12.0),
        espesor_um=250.0,
        humectable_agua=False,
        indicador="F254",
        zona_concentracion=False,
    ),
    "rp18-f254s": Placa(
        id="rp18-f254s",
        nombre="HPTLC Sílica 60 RP-18 F254s",
        catalogo="1.13724",
        modo="RP",
        grado="HPTLC",
        particula_um=(5.0, 6.0),
        espesor_um=200.0,
        humectable_agua=False,
        indicador="F254s",
        zona_concentracion=False,
    ),
    "rp18-w-f254s": Placa(
        id="rp18-w-f254s",
        nombre="HPTLC Sílica 60 RP-18 W F254s (humectable con agua)",
        catalogo="1.13124",
        modo="RP",
        grado="HPTLC",
        particula_um=(5.0, 6.0),
        espesor_um=200.0,
        humectable_agua=True,
        indicador="F254s",
        zona_concentracion=False,
    ),
    "rp18-zona-concentracion": Placa(
        id="rp18-zona-concentracion",
        nombre="HPTLC RP-18 F254s con zona de concentración 20 x 2,5 cm",
        catalogo="1.15498",
        modo="RP",
        grado="HPTLC",
        particula_um=(5.0, 6.0),
        espesor_um=200.0,
        humectable_agua=False,
        indicador="F254s",
        zona_concentracion=True,
    ),
    "silice-zona-concentracion": Placa(
        id="silice-zona-concentracion",
        nombre="TLC Sílica 60 F254 con zona de concentración 2,5 x 20 cm",
        catalogo="1.11798",
        modo="NP",
        grado="TLC",
        particula_um=(10.0, 12.0),
        espesor_um=250.0,
        humectable_agua=False,
        indicador="F254",
        zona_concentracion=True,
    ),
}
"""Catalogued plates. Specifications from EVIDENCIA['merck-placas']."""


class Estado(str, Enum):
    """Verdict for one plate."""

    VIABLE = "VIABLE"
    REQUIERE_LIMPIEZA = "REQUIERE_LIMPIEZA"
    NO_VIABLE = "NO_VIABLE"
    SIN_EVIDENCIA = "SIN_EVIDENCIA"


@dataclass(frozen=True)
class Factor:
    """One evaluated aspect, with its evidence level and source."""

    id: str
    titulo: str
    nivel: Nivel
    texto: str
    fuente_id: str | None = None
    valor: float | None = None

    def __post_init__(self) -> None:
        """Enforce the project-wide rule: no value without a resolvable source."""
        if self.valor is not None and self.fuente_id not in EVIDENCIA:
            raise ValueError(f"factor '{self.id}' emite valor sin fuente resoluble")
        if self.nivel is Nivel.SIN_FUENTE and self.valor is not None:
            raise ValueError(f"factor '{self.id}' es SIN_FUENTE pero trae valor")


@dataclass(frozen=True)
class Veredicto:
    """Result of evaluating one plate against one NADES."""

    placa: Placa
    estado: Estado
    factores: tuple[Factor, ...]
    vacios: tuple[Factor, ...]


# El punto de fracaso publicado, en uL de NADES neto por banda: la quinoa aplicó
# 4-8 uL de extracto diluido 1/10 sobre sílica y aun así obtuvo colas severas.
FRACASO_NP_UL_NETO = (0.4, 0.8)

# Volúmenes del ensayo de aptitud de Ph. Eur., por grado de placa.
VOLUMEN_PH_EUR_UL: dict[str, float] = {"TLC": 10.0, "HPTLC": 2.0}


def _vacios_base() -> tuple[Factor, ...]:
    """Return the gaps that apply to every evaluation."""
    return (
        Factor(
            id="umbral-viscosidad",
            titulo="Umbral de dosificación del aplicador",
            nivel=Nivel.SIN_FUENTE,
            texto=(
                "El límite de viscosidad dosificable es una especificación del "
                "aplicador, no un dato de literatura. Consultar el manual del equipo."
            ),
        ),
        Factor(
            id="carga-tolerable",
            titulo="Carga no volátil tolerable por banda",
            nivel=Nivel.SIN_FUENTE,
            texto=(
                "No hay valor publicado de cuánta matriz no volátil admite una banda "
                "antes de distorsionarse. Lo que sí hay es el punto de fracaso ajeno "
                "que el factor 'carga no volátil' usa como referencia."
            ),
        ),
        Factor(
            id="revelado-sin-limpieza",
            titulo="Interferencia en revelado sin limpieza previa",
            nivel=Nivel.SIN_FUENTE,
            texto=(
                "Lo documentado es que NP/PEG, DPPH y α-amilasa funcionan después de "
                "SPE. Sin SPE no hay dato."
            ),
        ),
        Factor(
            id="componentes-hptlc",
            titulo="Volatilidad e higroscopicidad por componente",
            nivel=Nivel.SIN_FUENTE,
            texto=(
                "No existe como tabla publicada para los 39 componentes del "
                "simulador. Requiere sourcear componente por componente."
            ),
        ),
        Factor(
            id="raspado-hplc",
            titulo="Raspado de banda y reinyección en HPLC",
            nivel=Nivel.SIN_FUENTE,
            texto=(
                "Sin fuente específica para NADES. Solo hay guía genérica de TLC "
                "preparativa. Pregunta abierta de la tesis."
            ),
        ),
        Factor(
            id="obstruccion-aplicador",
            titulo="Obstrucción de aguja y arrastre entre muestras",
            nivel=Nivel.SIN_FUENTE,
            texto=(
                "Sin fuente. No se afirma que un líquido viscoso no volátil tape la "
                "boquilla ni que contamine la muestra siguiente."
            ),
        ),
    )


def evaluar_placa(
    props: dict,
    placa: Placa,
    volumen_uL: float,
    dilucion: float,
) -> Veredicto:
    """Evaluate direct spotting of a NADES extract on one plate.

    Args:
        props: Properties from `model.calculate_nades_properties`. Only
            `viscosidad`, `water_pct` and `pH` are read.
        placa: The catalogued plate to evaluate.
        volumen_uL: Volume applied per band, in microlitres.
        dilucion: Dilution factor of the extract (10.0 means 1/10).

    Returns:
        The verdict, with every factor carrying its evidence level.

    Raises:
        ValueError: If `dilucion` or `volumen_uL` are not positive.
    """
    if dilucion <= 0:
        raise ValueError("dilucion debe ser positiva")
    if volumen_uL <= 0:
        raise ValueError("volumen_uL debe ser positivo")

    factores: list[Factor] = []
    neto = volumen_uL / dilucion

    bajo, alto = FRACASO_NP_UL_NETO
    factores.append(
        Factor(
            id="carga-no-volatil",
            titulo="Carga no volátil en el origen",
            nivel=Nivel.MEDIDO,
            fuente_id="quinoa2025",
            valor=round(neto, 3),
            texto=(
                f"Se depositan {neto:.2f} µL de NADES neto por banda. El punto de "
                f"fracaso publicado en fase normal está en {bajo}-{alto} µL netos, "
                "que produjo colas severas incluso a dilución 1/10."
            ),
        )
    )

    factores.append(
        Factor(
            id="viscosidad",
            titulo="Viscosidad efectiva",
            nivel=Nivel.MEDIDO,
            fuente_id="liu2017",
            valor=float(props["viscosidad"]),
            texto=(
                f"{props['viscosidad']:.0f} cP a la temperatura de trabajo. La alta "
                "viscosidad es uno de los dos obstáculos analíticos que la fuente "
                "primaria atribuye a los NADES."
            ),
        )
    )

    if placa.zona_concentracion:
        factores.append(
            Factor(
                id="enfoque-banda",
                titulo="Enfoque de banda",
                nivel=Nivel.INFERIDO,
                fuente_id="merck-zona",
                texto=(
                    "La zona de concentración enfoca por migración cromatográfica en "
                    "el adsorbente inerte, no por evaporación, y el fabricante la "
                    "declara además como paso de limpieza para matrices complejas. "
                    "Es un mecanismo que sigue operando con matriz no volátil."
                ),
            )
        )
    else:
        factores.append(
            Factor(
                id="enfoque-banda",
                titulo="Enfoque de banda",
                nivel=Nivel.INFERIDO,
                fuente_id="camag-linomat",
                texto=(
                    "El spray-on forma banda angosta porque el disolvente se evapora "
                    "durante la aplicación. Un NADES no evapora, así que el mecanismo "
                    "de enfoque no opera sobre esa fracción: el aplicador dosifica un "
                    "volumen reproducible pero no lo convierte en banda estrecha."
                ),
            )
        )

    agua = float(props["water_pct"])
    if placa.modo == "RP":
        factores.append(
            Factor(
                id="agua",
                titulo="Agua del NADES",
                nivel=Nivel.INFERIDO,
                fuente_id="jchemed2019",
                valor=agua,
                texto=(
                    f"{agua:.0f}% de agua. En fase reversa el agua es eluyente débil, "
                    "lo que se aprovecha para aplicar muestras acuosas como banda "
                    "estrecha: aquí el agua juega a favor."
                ),
            )
        )
    else:
        factores.append(
            Factor(
                id="agua",
                titulo="Agua del NADES",
                nivel=Nivel.MEDIDO,
                fuente_id="quinoa2025",
                valor=agua,
                texto=(
                    f"{agua:.0f}% de agua. En sílica el agua es eluyente fuerte y la "
                    "muestra polar se desparrama: aquí el agua juega en contra."
                ),
            )
        )

    if placa.modo == "RP" and not placa.humectable_agua:
        factores.append(
            Factor(
                id="humectabilidad",
                titulo="Humectabilidad de la placa",
                nivel=Nivel.MEDIDO,
                fuente_id="merck-placas",
                texto=(
                    "Placa RP-18 sin el grado W. Con fases móviles muy acuosas conviene "
                    "la variante W, catalogada como completamente humectable con agua."
                ),
            )
        )

    pH = float(props["pH"])
    if placa.indicador == "F254" and pH < 4.5:
        factores.append(
            Factor(
                id="indicador",
                titulo="Indicador de fluorescencia",
                nivel=Nivel.MEDIDO,
                fuente_id="merck-placas",
                texto=(
                    f"NADES ácido (pH {pH:.1f}) sobre placa F254. El catálogo ofrece "
                    "F254s, indicador estable a ácido, para justamente este caso."
                ),
            )
        )
    else:
        factores.append(
            Factor(
                id="indicador",
                titulo="Indicador de fluorescencia",
                nivel=Nivel.MEDIDO,
                fuente_id="merck-placas",
                texto=f"Indicador {placa.indicador} frente a un NADES de pH {pH:.1f}.",
            )
        )

    vacios = list(_vacios_base())
    if placa.modo == "RP":
        vacios.insert(
            0,
            Factor(
                id="cruce-nades-rp18",
                titulo="NADES sembrado directo en RP-18",
                nivel=Nivel.SIN_FUENTE,
                texto=(
                    "El fracaso publicado es en fase normal; el mecanismo favorable en "
                    "RP está publicado con muestras acuosas, no con NADES. El cruce no "
                    "existe en la literatura: es hipótesis a ensayar, no predicción."
                ),
            ),
        )
        estado = Estado.SIN_EVIDENCIA
    else:
        estado = Estado.REQUIERE_LIMPIEZA

    return Veredicto(
        placa=placa,
        estado=estado,
        factores=tuple(factores),
        vacios=tuple(vacios),
    )


@dataclass(frozen=True)
class Protocolo:
    """Candidate application protocol derived from a verdict."""

    volumen_max_uL: float
    fuente_volumen: str
    limpieza_previa: bool
    notas: str


def protocolo_candidato(veredicto: Veredicto) -> Protocolo:
    """Build the candidate protocol for a verdict.

    Args:
        veredicto: The evaluated verdict.

    Returns:
        The protocol, whose volume comes from the Ph. Eur. suitability test
        rather than from any threshold chosen by this module.
    """
    placa = veredicto.placa
    volumen = VOLUMEN_PH_EUR_UL[placa.grado]

    if placa.zona_concentracion:
        limpieza = False
        notas = (
            "La zona de concentración incorpora, según el fabricante, una etapa de "
            "purificación y concentración: se ensaya sin limpieza previa y se compara "
            "contra un blanco de NADES sin extracto."
        )
    elif placa.modo == "NP":
        limpieza = True
        notas = (
            "En fase normal la siembra directa está documentada como fracaso incluso a "
            "dilución 1/10. Se requiere SPE previa (cartucho polimérico tipo Strata-X)."
        )
    else:
        limpieza = False
        notas = (
            "Sin evidencia publicada para NADES en RP-18. Se ensaya como hipótesis: "
            "sembrar por duplicado con y sin SPE, y registrar el resultado en la "
            "bitácora para confrontar la hipótesis con la placa."
        )

    return Protocolo(
        volumen_max_uL=volumen,
        fuente_volumen="merck-placas",
        limpieza_previa=limpieza,
        notas=notas,
    )

"""Single bibliographic registry for the whole program.

Shared by the HPTLC verdict and by the property explanations, so a source is
described once and cited from anywhere. Imports nothing from the rest of the app.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Nivel(str, Enum):
    """Evidence level attached to every claim the program makes."""

    MEDIDO = "MEDIDO"
    INFERIDO = "INFERIDO"
    SIN_FUENTE = "SIN_FUENTE"


@dataclass(frozen=True)
class Fuente:
    """A verifiable bibliographic source backing one or more claims."""

    id: str
    cita: str
    doi: str
    afirma: str


EVIDENCIA: dict[str, Fuente] = {
    "liu2017": Fuente(
        id="liu2017",
        cita=(
            "Liu X., Ahlgren S., Korthout H.A.A.J., Salomé-Abarca L.F., Bayona L.M., "
            "Verpoorte R., Choi Y.H. (2017). Broad range chemical profiling of natural "
            "deep eutectic solvent extracts using a high performance thin layer "
            "chromatography-based method. J. Chromatogr. A 1532:198-207."
        ),
        doi="10.1016/j.chroma.2017.12.009",
        afirma=(
            "Sitúa la dificultad analítica de los NADES en dos propiedades: baja presión "
            "de vapor y alta viscosidad. Óptimo de rendimiento cerca de 20% de agua (w/w)."
        ),
    ),
    "quinoa2025": Fuente(
        id="quinoa2025",
        cita=(
            "NADES para la extracción de compuestos bioactivos de hojas de quinoa "
            "(Chenopodium quinoa Willd.): análisis semicuantitativo por HPTLC. "
            "PMC12195850."
        ),
        doi="PMC12195850",
        afirma=(
            "Sobre sílica gel 60 F254 la aplicación directa perturbó la migración y "
            "produjo colas severas en todas las muestras, incluso diluyendo 1/10 con "
            "agua. Requirió SPE (Strata-X). Aplicaron 4-8 uL."
        ),
    ),
    "jchemed2019": Fuente(
        id="jchemed2019",
        cita=(
            "Reversed Phase High Performance Thin Layer Chromatography of Aqueous "
            "Samples in Student Laboratories Using the Example of Anthocyanin Patterns "
            "from Flower Petals. J. Chem. Educ. 2019, 96(9)."
        ),
        doi="10.1021/acs.jchemed.8b00900",
        afirma=(
            "En placas de fase reversa el agua tiene bajo poder eluyente, y eso se "
            "aprovecha para aplicar muestras acuosas como banda estrecha."
        ),
    ),
    "merck-placas": Fuente(
        id="merck-placas",
        cita=("Merck Millipore, folleto técnico 'Fast and precise Thin Layer " "Chromatography'."),
        doi="catalogo-merck",
        afirma=(
            "TLC: 10-12 um de partícula, capa 250 um en vidrio. HPTLC: 5-6 um, capa "
            "200 um. Ensayo de aptitud Ph. Eur.: 10 uL en placa TLC normal, 1-2 uL en "
            "placa de partícula fina. 'W' = completamente humectable con agua. F254s = "
            "indicador estable a ácido. 60G = aglutinante de yeso."
        ),
    ),
    "merck-zona": Fuente(
        id="merck-zona",
        cita=(
            "Merck Millipore, folleto técnico, sección 'Concentrating zone plates "
            "(TLC, HPTLC, PLC)'."
        ),
        doi="catalogo-merck",
        afirma=(
            "Dos adsorbentes: uno inerte de poro grande donde se siembra y la capa "
            "selectiva donde se separa. La muestra se concentra en banda estrecha en la "
            "interfaz en segundos, sin importar forma, tamaño ni posición del depósito. "
            "El fabricante declara que la zona sirve como paso de limpieza para "
            "matrices complejas."
        ),
    ),
    "camag-linomat": Fuente(
        id="camag-linomat",
        cita="CAMAG, documentación de la técnica spray-on del Linomat 5.",
        doi="documentacion-camag",
        afirma=(
            "En el spray-on el disolvente se evapora casi por completo durante la "
            "aplicación, y ese es el paso que concentra la muestra en banda angosta."
        ),
    ),
    "espino2016": Fuente(
        id="espino2016",
        cita=(
            "Espino M., de los Ángeles Fernández M., Gomez F.J.V., Silva M.F. (2016). "
            "Natural designer solvents for greening analytical chemistry. "
            "Talanta 162:412."
        ),
        doi="10.1016/j.talanta.2016.10.078",
        afirma=(
            "Modelo de extracción por polaridad, capacidad HBD y pH. Es la referencia "
            "que el simulador ya citaba al pie de los gráficos de índice EP."
        ),
    ),
    "dai2013": Fuente(
        id="dai2013",
        cita=(
            "Dai Y., van Spronsen J., Witkamp G.-J., Verpoorte R., Choi Y.H. (2013). "
            "Natural deep eutectic solvents as new potential media for green "
            "technology. Anal. Chim. Acta 766:61."
        ),
        doi="10.1016/j.aca.2012.12.019",
        afirma=(
            "Efecto del contenido de agua sobre la red supramolecular del NADES y sobre "
            "la estabilidad de los compuestos disueltos."
        ),
    ),
    "ruiz2024": Fuente(
        id="ruiz2024",
        cita=(
            "Ruiz A. et al. (2024). Calafate (Berberis microphylla G. Forst) "
            "populations from Chilean Patagonia exhibit similar structuring at the "
            "genetic and metabolic levels. Horticulturae 10:458."
        ),
        doi="10.3390/horticulturae10050458",
        afirma=(
            "Perfil de 28 polifenoles de Berberis microphylla por HPLC-DAD-ESI-MS/MS. "
            "Es la base de la fracción EP del simulador."
        ),
    ),
}
"""Verifiable sources. Every claim with a value must name one of these."""


@dataclass(frozen=True)
class ParametroSinFuente:
    """A model parameter that carries no published backing.

    Registered explicitly rather than left as a literal in the code, so the
    program can say which of its numbers are assumptions and how much the
    conclusions lean on them.
    """

    id: str
    titulo: str
    valor_actual: str
    donde: str
    afecta: str
    hallazgo: str
    como_cerrarlo: str


PARAMETROS_SIN_FUENTE: dict[str, ParametroSinFuente] = {
    "polaridad-optima": ParametroSinFuente(
        id="polaridad-optima",
        titulo="Polaridad óptima por polifenol",
        valor_actual="antocianinas 0,82–0,87 · flavonoles 0,71–0,75",
        donde="data.py, columna `polaridad_optima` de la base de polifenoles",
        afecta=(
            "El término de polaridad, que pesa 35 % en EP — el mayor del motor — y "
            "aporta la mayor parte de la ventaja de los NADES sobre los hidroalcohólicos."
        ),
        hallazgo=(
            "Los óptimos de extracción publicados para bayas implican ETN 0,73–0,78 "
            "(Berberis kaschgarica 56,5 % EtOH → 0,742; arándano acidificado 60,65 % → "
            "0,734; saúco 40,9 % → 0,779), frente al 0,842 que asume el modelo para "
            "antocianinas: un desfase de +0,09. La sensibilidad muestra que un "
            "desplazamiento de −0,10 invierte el orden y el etanol acuoso gana. "
            "Matiz: el óptimo empírico convoluciona solvatación, viscosidad y "
            "penetración, y el modelo ya trata la viscosidad aparte, así que igualarlos "
            "contaría dos veces."
        ),
        como_cerrarlo=(
            "Calibrar con extracciones propias a distinta composición de etanol y "
            "cargarlas en la bitácora: convierte el punto más atacable en un resultado "
            "experimental propio."
        ),
    ),
    "sigma-polaridad": ParametroSinFuente(
        id="sigma-polaridad",
        titulo="Ancho de la gaussiana de polaridad",
        valor_actual="σ = 0,08 en EP · σ = 0,10 en NEP",
        donde="model.py, SIGMA_POLARIDAD_EP y SIGMA_POLARIDAD_NEP",
        afecta="Cuán rápido cae el puntaje al alejarse de la polaridad óptima.",
        hallazgo=(
            "Con σ = 0,30 los tres sistemas quedan casi empatados (0,982 / 0,947 / "
            "0,939); con σ = 0,08 la brecha es 0,121. La ventaja de los NADES existe "
            "en buena medida porque la gaussiana es estrecha."
        ),
        como_cerrarlo=(
            "Ajustar el ancho contra una serie propia de composiciones, junto con la "
            "polaridad óptima."
        ),
    ),
}
"""Parameters the program uses but cannot cite. Shown, not hidden."""

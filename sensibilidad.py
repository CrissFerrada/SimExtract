"""Sensitivity of the extraction score to the parameters that carry no source.

The polarity term weighs 35 % of the EP score and rests on two unsourced numbers:
the per-compound optimal polarity and the width of the Gaussian around it. This
module measures how much a conclusion actually leans on them, so the program can
report a band and a stability verdict instead of a single figure that looks more
certain than it is.

It re-runs the real scoring functions over a shifted copy of the polyphenol table
rather than reimplementing them, so it can never drift from the model it audits.

Imports no Streamlit.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

import model
from model import ep_extraction_score

DESPLAZAMIENTOS = (-0.10, -0.05, 0.0, 0.05, 0.10)
"""Range explored for `polaridad_optima`, in ETN units.

±0.10 is not arbitrary: published extraction optima for berries imply ETN
0.73–0.78 against the 0.842 the model assumes for anthocyanins, a gap of +0.09.
"""

SIGMAS = (0.08, 0.12, 0.20, 0.30)
"""Gaussian widths explored, from the current value up to a broad one."""


@dataclass(frozen=True)
class Banda:
    """One system's EP score across the unsourced-parameter range."""

    etiqueta: str
    central: float
    minimo: float
    maximo: float

    @property
    def amplitud(self) -> float:
        """How wide the band is — how much the figure depends on assumptions."""
        return self.maximo - self.minimo


@dataclass(frozen=True)
class Comparacion:
    """Ranking of several systems, with whether it survives the range."""

    bandas: tuple[Banda, ...]
    estable: bool
    ganador_central: str
    otros_ganadores: tuple[str, ...]

    @property
    def veredicto(self) -> str:
        """One line on whether the ranking can be asserted."""
        if self.estable:
            return (
                f"{self.ganador_central} gana en todo el rango explorado: el orden no "
                "depende de los parámetros sin fuente."
            )
        rivales = " y ".join(self.otros_ganadores)
        return (
            f"El orden NO es estable. Con los valores actuales gana {self.ganador_central}, "
            f"pero dentro del rango explorado también gana {rivales}. La comparación no se "
            "puede afirmar sin medir la polaridad óptima."
        )


def _tabla_desplazada(poly_df: pd.DataFrame, desplazamiento: float) -> pd.DataFrame:
    """Return a copy of the polyphenol table with its optimal polarity shifted."""
    movida = poly_df.copy()
    movida["polaridad_optima"] = movida["polaridad_optima"] + desplazamiento
    return movida


def score_ep_medio(
    props: dict,
    poly_df: pd.DataFrame,
    desplazamiento: float = 0.0,
    sigma: float | None = None,
) -> float:
    """Mean EP score over the extractable polyphenols.

    Args:
        props: Solvent properties, as produced by `calculate_nades_properties`.
        poly_df: Polyphenol table; only its EP rows are used.
        desplazamiento: Shift applied to `polaridad_optima`, in ETN units.
        sigma: Gaussian width to use. Defaults to the model's current value.

    Returns:
        The mean total EP score.
    """
    ep = poly_df[poly_df["tipo"] == "EP"]
    if ep.empty:
        raise ValueError("la tabla de polifenoles no tiene filas EP")

    tabla = _tabla_desplazada(ep, desplazamiento) if desplazamiento else ep
    original = model.SIGMA_POLARIDAD_EP
    if sigma is not None:
        model.SIGMA_POLARIDAD_EP = sigma
    try:
        puntajes = [ep_extraction_score(props, fila)["total"] for _, fila in tabla.iterrows()]
    finally:
        model.SIGMA_POLARIDAD_EP = original
    return sum(puntajes) / len(puntajes)


def banda(
    etiqueta: str,
    props: dict,
    poly_df: pd.DataFrame,
    desplazamientos: tuple[float, ...] = DESPLAZAMIENTOS,
) -> Banda:
    """Return one system's score band across the shift range."""
    valores = [score_ep_medio(props, poly_df, d) for d in desplazamientos]
    return Banda(
        etiqueta=etiqueta,
        central=score_ep_medio(props, poly_df, 0.0),
        minimo=min(valores),
        maximo=max(valores),
    )


def comparar(
    sistemas: dict[str, dict],
    poly_df: pd.DataFrame,
    desplazamientos: tuple[float, ...] = DESPLAZAMIENTOS,
) -> Comparacion:
    """Compare several solvent systems and say whether the ranking is stable.

    Args:
        sistemas: Label to properties dict.
        poly_df: Polyphenol table.
        desplazamientos: Shifts to explore.

    Returns:
        The comparison, whose `estable` is False when the winner changes anywhere
        in the range — that is, when the ranking rests on an unsourced number.

    Raises:
        ValueError: If fewer than two systems are given.
    """
    if len(sistemas) < 2:
        raise ValueError("se necesitan al menos dos sistemas para comparar")

    ganadores = []
    for d in desplazamientos:
        puntajes = {k: score_ep_medio(p, poly_df, d) for k, p in sistemas.items()}
        ganadores.append(max(puntajes, key=puntajes.get))

    central = max(
        {k: score_ep_medio(p, poly_df, 0.0) for k, p in sistemas.items()}.items(),
        key=lambda kv: kv[1],
    )[0]
    distintos = tuple(sorted({g for g in ganadores if g != central}))

    return Comparacion(
        bandas=tuple(banda(k, p, poly_df, desplazamientos) for k, p in sistemas.items()),
        estable=not distintos,
        ganador_central=central,
        otros_ganadores=distintos,
    )

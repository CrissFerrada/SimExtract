"""Shared display components.

The explained card replaces `prop_card`: a bare number in a coloured box told the
user what the value was, but never why it mattered nor who says so.
"""

from __future__ import annotations

import streamlit as st

from evidencia import EVIDENCIA, Nivel
from explicacion import Lectura

INSIGNIAS = {
    Nivel.MEDIDO: "🟩",
    Nivel.INFERIDO: "🟨",
    Nivel.SIN_FUENTE: "⬜",
}


def texto_ficha(lectura: Lectura) -> str:
    """Return the one-line headline for a reading."""
    unidad = f" {lectura.unidad}" if lectura.unidad else ""
    return f"{lectura.titulo}: {lectura.valor:g}{unidad} — {lectura.calificativo}"


def ficha_explicada(lectura: Lectura) -> None:
    """Render one reading with its value, its meaning and its source."""
    unidad = f" {lectura.unidad}" if lectura.unidad else ""
    st.metric(lectura.titulo, f"{lectura.valor:g}{unidad}", lectura.calificativo)
    with st.expander("¿Por qué importa?", expanded=False):
        st.write(lectura.por_que)
        fuente = EVIDENCIA[lectura.fuente_id]
        st.caption(f"{INSIGNIAS[lectura.nivel]} {fuente.cita}")
        st.caption(f"DOI: {fuente.doi}")


def nades_activo(props: dict, hba: str, hbd: str, ratio: str) -> str:
    """Return the one-line description of the mixture currently being shown."""
    return f"{hba} : {hbd} ({ratio}, {props['water_pct']:.0f}% H₂O, {props['temp_C']:.0f} °C)"

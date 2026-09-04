"""Sensitivity panel.

Shows the extraction score as a band rather than a single figure, and says
plainly whether a comparison survives the parameters that carry no source.
Rendering only; the reasoning lives in `sensibilidad.py`.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from evidencia import PARAMETROS_SIN_FUENTE
from sensibilidad import DESPLAZAMIENTOS, SIGMAS, Comparacion, comparar, score_ep_medio
from tema import PALETA


def _figura_banda(comparacion: Comparacion) -> go.Figure:
    """Horizontal band per system, with the current value marked."""
    fig = go.Figure()
    for b in comparacion.bandas:
        fig.add_trace(
            go.Scatter(
                x=[b.minimo, b.maximo],
                y=[b.etiqueta, b.etiqueta],
                mode="lines",
                line={"color": PALETA["acento"], "width": 14},
                opacity=0.45,
                showlegend=False,
                hovertemplate=f"{b.etiqueta}: %{{x:.3f}}<extra></extra>",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[b.central],
                y=[b.etiqueta],
                mode="markers",
                marker={"color": PALETA["primario"], "size": 14, "symbol": "diamond"},
                showlegend=False,
                hovertemplate=f"{b.etiqueta} · valor actual: %{{x:.3f}}<extra></extra>",
            )
        )
    fig.update_layout(
        xaxis_title="Índice EP promedio",
        height=90 + 52 * len(comparacion.bandas),
        margin={"l": 10, "r": 10, "t": 10, "b": 40},
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def render_sensibilidad(sistemas: dict[str, dict], poly_df: pd.DataFrame) -> None:
    """Render the sensitivity panel for a set of solvent systems.

    Args:
        sistemas: Label to properties dict. Needs at least two to compare.
        poly_df: Polyphenol table.
    """
    st.markdown("### 🎯 ¿Cuánto se puede afirmar esta comparación?")
    st.caption(
        "El término de polaridad pesa 35 % del índice EP y descansa en dos números "
        "sin respaldo publicado. Aquí se muestra cuánto depende el resultado de ellos."
    )

    if len(sistemas) < 2:
        st.info("Se necesitan al menos dos sistemas para comparar.")
        return

    comparacion = comparar(sistemas, poly_df)

    if comparacion.estable:
        st.success(comparacion.veredicto)
    else:
        st.warning(comparacion.veredicto)

    st.plotly_chart(_figura_banda(comparacion), use_container_width=True)
    st.caption(
        "El rombo es el valor con los parámetros actuales; la barra es el rango al "
        "mover la polaridad óptima ±0,10 en unidades ETN. Bandas que se solapan "
        "significan que el orden entre esos sistemas no está determinado."
    )

    with st.expander("Ver el detalle por desplazamiento", expanded=False):
        filas = []
        for d in DESPLAZAMIENTOS:
            fila = {"Desplazamiento": f"{d:+.2f}"}
            for etiqueta, props in sistemas.items():
                fila[etiqueta] = round(score_ep_medio(props, poly_df, d), 3)
            filas.append(fila)
        st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)

        st.markdown("**Y según el ancho de la gaussiana:**")
        filas_s = []
        for s in SIGMAS:
            fila = {"σ": s}
            for etiqueta, props in sistemas.items():
                fila[etiqueta] = round(score_ep_medio(props, poly_df, 0.0, sigma=s), 3)
            filas_s.append(fila)
        st.dataframe(pd.DataFrame(filas_s), use_container_width=True, hide_index=True)

    st.markdown("#### Los parámetros que no tienen fuente")
    for p in PARAMETROS_SIN_FUENTE.values():
        with st.expander(f"⬜ {p.titulo} — {p.valor_actual}", expanded=False):
            st.markdown(f"**Dónde vive:** {p.donde}")
            st.markdown(f"**Qué afecta:** {p.afecta}")
            st.markdown(f"**Lo que encontró la auditoría:** {p.hallazgo}")
            st.info(f"**Cómo cerrarlo:** {p.como_cerrarlo}")

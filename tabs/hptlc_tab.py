"""HPTLC compatibility section.

Rendering only. All the reasoning lives in `hptlc.py`, which stays importable
without Streamlit.
"""

from __future__ import annotations

import streamlit as st

from evidencia import EVIDENCIA, Nivel
from hptlc import PLACAS, Estado, evaluar_placa, protocolo_candidato

_INSIGNIAS = {
    Nivel.MEDIDO: "🟩 MEDIDO",
    Nivel.INFERIDO: "🟨 INFERIDO",
    Nivel.SIN_FUENTE: "⬜ SIN FUENTE",
}

# SIN_EVIDENCIA es gris, no una gradación del verde: la incertidumbre no es una
# versión débil de "viable", es una categoría distinta.
_COLORES = {
    Estado.VIABLE: "green",
    Estado.REQUIERE_LIMPIEZA: "orange",
    Estado.NO_VIABLE: "red",
    Estado.SIN_EVIDENCIA: "gray",
}


def insignia(nivel: Nivel) -> str:
    """Return the badge label for an evidence level."""
    return _INSIGNIAS[nivel]


def color_estado(estado: Estado) -> str:
    """Return the Streamlit colour name for a verdict state."""
    return _COLORES[estado]


def render_hptlc(props: dict) -> None:
    """Render the HPTLC compatibility section for the active NADES."""
    st.markdown("### 🧫 Compatibilidad HPTLC")
    st.caption(
        "Ningún valor se emite sin fuente. Donde la literatura calla, el módulo "
        "declara el vacío en vez de rellenarlo."
    )

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        placa_id = st.selectbox(
            "Placa",
            options=list(PLACAS),
            format_func=lambda k: PLACAS[k].nombre,
            index=list(PLACAS).index("rp18-w-f254s"),
        )
    with col_b:
        volumen = st.number_input("Volumen por banda (µL)", 0.5, 20.0, 2.0, 0.5)
    with col_c:
        dilucion = st.number_input("Dilución (1 : n)", 1.0, 100.0, 10.0, 1.0)

    placa = PLACAS[placa_id]
    veredicto = evaluar_placa(props, placa, volumen, dilucion)
    protocolo = protocolo_candidato(veredicto)

    st.markdown(f"#### Veredicto: :{color_estado(veredicto.estado)}[{veredicto.estado.value}]")
    st.caption(f"{placa.nombre} · cat. {placa.catalogo} · capa {placa.espesor_um:.0f} µm")

    for f in veredicto.factores:
        with st.expander(f"{insignia(f.nivel)} — {f.titulo}", expanded=False):
            st.write(f.texto)
            if f.fuente_id:
                fuente = EVIDENCIA[f.fuente_id]
                st.caption(f"Fuente: {fuente.cita}")
                st.caption(f"DOI: {fuente.doi}")

    st.markdown("#### Protocolo candidato")
    st.write(
        f"Volumen máximo por banda: **{protocolo.volumen_max_uL:.0f} µL** "
        f"(ensayo de aptitud Ph. Eur., grado {placa.grado})"
    )
    st.write(f"Limpieza previa: **{'sí' if protocolo.limpieza_previa else 'no'}**")
    st.info(protocolo.notas)

    st.markdown("#### Qué falta medir")
    st.caption("Esto es el diseño del próximo ensayo, no una carencia del módulo.")
    for f in veredicto.vacios:
        st.markdown(f"- **{f.titulo}** — {f.texto}")

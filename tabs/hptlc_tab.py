"""HPTLC compatibility section.

Rendering only. All the reasoning lives in `hptlc.py`, which stays importable
without Streamlit.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from aplicador import TEMP_APLICACION_C, lectura_aplicador
from data import HBA_COMPONENTS, HBD_COMPONENTS
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


def _render_aplicador(props: dict) -> None:
    """Show the viscosity the syringe sees, and how it drifts as water leaves.

    The properties panel reports viscosity at the extraction temperature; the
    applicator works at room temperature, where a NADES is roughly twice as thick.
    """
    st.markdown("#### 💉 Lo que ve el aplicador")

    hba = st.session_state.get("sel_hba")
    hbd = st.session_state.get("sel_hbd")
    ratio = st.session_state.get("sel_ratio", "1:1")
    if not hba or not hbd:
        st.caption("Sin NADES activo.")
        return

    partes = ratio.split(":")
    r_hba, r_hbd = (float(partes[0]), float(partes[1])) if len(partes) == 2 else (1.0, 1.0)

    temp_ap = st.number_input(
        "Temperatura en el aplicador (°C)",
        10.0,
        40.0,
        TEMP_APLICACION_C,
        1.0,
        help="La sala donde está el equipo, no la de extracción.",
    )

    lec = lectura_aplicador(
        hba,
        hbd,
        r_hba,
        r_hbd,
        float(props["water_pct"]),
        float(props["temp_C"]),
        HBA_COMPONENTS,
        HBD_COMPONENTS,
        temp_aplicacion=temp_ap,
    )

    c1, c2 = st.columns(2)
    c1.metric(
        f"En extracción · {lec.temp_extraccion:.0f} °C",
        f"{lec.visc_extraccion:.0f} cP",
    )
    c2.metric(
        f"En el aplicador · {lec.temp_aplicacion:.0f} °C",
        f"{lec.visc_aplicacion:.0f} cP",
        f"×{lec.factor_temperatura:.1f}",
        delta_color="inverse",
    )

    hr = st.slider(
        "Humedad relativa de la sala (%)",
        10,
        95,
        60,
        5,
        help=(
            "Decide la dirección del intercambio de agua. Un NADES es higroscópico: "
            "su actividad de agua ronda 0,4, así que por encima de ~40 % de humedad "
            "absorbe en vez de secarse."
        ),
    )
    rama = lec.rama_probable(hr)

    if rama == "hidratacion":
        st.info(
            f"**Con {hr} % de humedad el depósito absorbe agua, no se seca.** La "
            f"viscosidad baja hasta ×{lec.factor_humedo:.2f} — dosificar se vuelve más "
            "fácil, no más difícil. El riesgo no es que se tape la aguja: es que **el "
            "origen no llegue a secarse nunca** en la placa, y la banda se ensanche. "
            "Explica por qué a la referencia publicada no le sirvió diluir 1/10: el "
            "depósito se reequilibra con la sala sin importar la dilución."
        )
        st.dataframe(
            pd.DataFrame(
                [
                    {"Agua (%)": a, f"Viscosidad a {temp_ap:.0f} °C (cP)": round(v)}
                    for a, v in ((float(props["water_pct"]), lec.visc_aplicacion), *lec.hidratacion)
                ]
            ),
            use_container_width=True,
            hide_index=True,
        )
    elif rama == "secado":
        st.warning(
            f"**Con {hr} % de humedad el depósito pierde agua.** La viscosidad sube "
            f"hasta ×{lec.factor_secado:.0f}, y la mezcla se aleja del eutéctico "
            "hidratado hacia el anhidro — el cloruro de colina puro funde a 302 °C. "
            "Aquí sí conviene la prueba en frío antes de cargar el equipo."
        )
        st.dataframe(
            pd.DataFrame(
                [
                    {"Agua (%)": a, f"Viscosidad a {temp_ap:.0f} °C (cP)": round(v)}
                    for a, v in lec.deriva
                ]
            ),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.caption(
            f"Con {hr} % de humedad el depósito está cerca del equilibrio con la sala: "
            "poco intercambio en cualquier dirección."
        )

    st.caption(
        "⬜ Sin fuente para este sistema. La actividad de agua de 0,4 está medida en un "
        "NADES de betaína a 14–22 % de agua; el tuyo tiene más agua, así que su "
        "actividad es mayor y el punto de cruce se desplaza. El signo del argumento no "
        "cambia, pero el umbral exacto hay que medirlo."
    )


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

    _render_aplicador(props)

    st.markdown("#### Qué falta medir")
    st.caption("Esto es el diseño del próximo ensayo, no una carencia del módulo.")
    for f in veredicto.vacios:
        st.markdown(f"- **{f.titulo}** — {f.texto}")

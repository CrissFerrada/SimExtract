"""Experiment plan panel.

Lists what the program cannot know and the assay that would settle each gap.
It deliberately shows the open questions rather than the answers: the simulator's
useful output at this stage is a bench plan, not another coefficient.
"""

from __future__ import annotations

import streamlit as st

from evidencia import PARAMETROS_SIN_FUENTE
from experimentos import cargar_bitacora
from plan_experimental import ENSAYOS, sin_ensayo


def _estado_bitacora() -> tuple[int, bool]:
    """Return how many assays are recorded and whether the log has anything at all."""
    bitacora = cargar_bitacora()
    return len(bitacora), not bitacora.empty


def render_plan() -> None:
    """Render the experiment plan."""
    st.markdown("### 🧾 Qué medir para dejar de suponer")
    st.caption(
        "El programa carga hoy más modelo que dato. Esto no añade otro modelo: dice "
        "qué ensayo cierra cada hueco declarado."
    )

    registrados, hay_datos = _estado_bitacora()
    if hay_datos:
        st.success(f"Bitácora: {registrados} ensayos registrados.")
    else:
        st.warning(
            "La bitácora está vacía. Todos los números que ves salen de literatura ajena "
            "o de supuestos, ninguno de tus mediciones."
        )

    calibrados = [p for p in PARAMETROS_SIN_FUENTE.values() if p.circular]
    if calibrados:
        st.error(
            f"**{len(calibrados)} parámetros están calibrados, no medidos.** Reproducen "
            "por construcción los rangos que reporta la literatura, así que el programa "
            "no puede usarlos como evidencia de esos mismos rangos: repetirlos es citar, "
            "no medir."
        )

    huerfanos = sin_ensayo()
    if huerfanos:
        st.warning(f"Huecos sin ensayo planificado: {', '.join(huerfanos)}")

    st.divider()

    for i, e in enumerate(ENSAYOS, start=1):
        with st.container():
            st.markdown(f"#### {i}. {e.titulo}")
            st.markdown(f"> {e.pregunta}")

            col_a, col_b = st.columns([3, 2])
            with col_a:
                st.markdown("**Condiciones**")
                for c in e.condiciones:
                    st.markdown(f"- {c}")
                st.markdown(f"**Qué medir.** {e.que_medir}")
            with col_b:
                st.markdown(f"**Esfuerzo.** {e.esfuerzo}")
                st.markdown("**Qué desbloquea**")
                for clave in e.cierra:
                    p = PARAMETROS_SIN_FUENTE.get(clave)
                    if p is not None:
                        marca = "🔁 calibrado" if p.circular else "⬜ sin fuente"
                        st.markdown(f"- {marca} · {p.titulo}")
                    else:
                        st.markdown(f"- ⬜ vacío HPTLC · `{clave.split(':', 1)[1]}`")

            st.info(f"**Por qué ahora.** {e.porque_ahora}")
            st.caption(f"Cómo entra al programa: {e.como_entra}")
            if i < len(ENSAYOS):
                st.divider()

"""Visual theme.

Palette taken from the product's own identity — the calafate purple and the solvent
teal of `assets/simnades.ico` — rather than from a generic dashboard blue.

Every transition and keyframe lives inside a `prefers-reduced-motion: no-preference`
query, so a user who asked their system for less movement gets none: motion is an
enhancement here, never a carrier of information.
"""

from __future__ import annotations

import streamlit as st

PALETA: dict[str, str] = {
    "primario": "#4A2A7A",
    "primario_claro": "#8A5CBA",
    "acento": "#60CDD6",
    "llamada": "#F59E0B",
    "fondo": "#F8FAFC",
    "superficie": "#FFFFFF",
    "texto": "#1E1633",
    "texto_tenue": "#475569",
    "borde": "#E2E8F0",
}
"""Calafate purple over a near-white ground, teal for accents, amber for actions."""

_DURACION_MS = 180


def css() -> str:
    """Return the stylesheet injected into the app."""
    p = PALETA
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Sans:wght@300;400;500;600;700&family=Fira+Code:wght@400;500&display=swap');

:root {{
    --sn-primario: {p["primario"]};
    --sn-primario-claro: {p["primario_claro"]};
    --sn-acento: {p["acento"]};
    --sn-llamada: {p["llamada"]};
    --sn-superficie: {p["superficie"]};
    --sn-texto: {p["texto"]};
    --sn-texto-tenue: {p["texto_tenue"]};
    --sn-borde: {p["borde"]};
}}

html, body, [class*="css"] {{
    font-family: 'Fira Sans', system-ui, -apple-system, sans-serif;
    color: var(--sn-texto);
}}

h1, h2, h3, h4 {{
    font-family: 'Fira Sans', system-ui, sans-serif;
    font-weight: 600;
    letter-spacing: -0.01em;
    color: var(--sn-primario);
}}

/* Monoespaciada solo para cifras: alinea columnas y digitos entre filas. */
[data-testid="stMetricValue"] {{
    font-family: 'Fira Code', ui-monospace, monospace;
    font-variant-numeric: tabular-nums;
    color: var(--sn-primario);
}}

[data-testid="stMetric"] {{
    background: var(--sn-superficie);
    border: 1px solid var(--sn-borde);
    border-left: 3px solid var(--sn-acento);
    border-radius: 8px;
    padding: 0.75rem 1rem;
}}

.stTabs [data-baseweb="tab"] {{
    font-weight: 500;
}}

.stTabs [aria-selected="true"] {{
    color: var(--sn-primario);
    border-bottom-color: var(--sn-primario);
}}

.stButton > button {{
    border-radius: 8px;
    font-weight: 500;
}}

/* El cursor debe decir que algo se puede pulsar. */
.stButton > button,
.stTabs [data-baseweb="tab"],
[data-testid="stExpander"] summary {{
    cursor: pointer;
}}

/* Foco visible: la navegacion por teclado no puede quedarse a ciegas. */
.stButton > button:focus-visible,
[data-testid="stExpander"] summary:focus-visible {{
    outline: 2px solid var(--sn-acento);
    outline-offset: 2px;
}}

@media (prefers-reduced-motion: no-preference) {{
    [data-testid="stMetric"] {{
        transition: border-left-color {_DURACION_MS}ms ease,
                    box-shadow {_DURACION_MS}ms ease;
    }}
    [data-testid="stMetric"]:hover {{
        border-left-color: var(--sn-primario);
        box-shadow: 0 2px 12px rgba(74, 42, 122, 0.12);
    }}

    .stButton > button {{
        transition: background-color {_DURACION_MS}ms ease,
                    transform {_DURACION_MS}ms ease;
    }}
    /* Se mueve con transform, no con width/height: no reflow, no salto de layout. */
    .stButton > button:hover {{
        transform: translateY(-1px);
    }}

    .stTabs [data-baseweb="tab"] {{
        transition: color {_DURACION_MS}ms ease;
    }}

    [data-testid="stDataFrame"] tbody tr {{
        transition: background-color {_DURACION_MS}ms ease;
    }}
    [data-testid="stDataFrame"] tbody tr:hover {{
        background-color: rgba(96, 205, 214, 0.10);
    }}

    @keyframes sn-entrada {{
        from {{ opacity: 0; transform: translateY(6px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
    [data-testid="stMetric"],
    [data-testid="stAlert"] {{
        animation: sn-entrada {_DURACION_MS}ms ease-out;
    }}
}}
</style>
"""


def inyectar_tema() -> None:
    """Inject the stylesheet. Call once, right after `st.set_page_config`."""
    st.markdown(css(), unsafe_allow_html=True)

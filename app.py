"""
SimExtract — simulador de extracción de polifenoles — Beta 0.6
© 2026 Cristofher Ferrada — Pontificia Universidad Católica de Valparaíso (PUCV).
Licenciado bajo Apache License 2.0. Ver LICENSE.

Berberis microphylla G. Forst — Fruto / Hojas / Tallo
EP: Ruiz et al. 2024 Horticulturae 10, 458 (HPLC-DAD-ESI-MS/MS)
NEP: Modelo teórico original (Ferrada 2026)
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import numpy as np

from data import (
    HBA_COMPONENTS,
    HBD_COMPONENTS,
    RATIOS_DISPONIBLES,
    THESIS_NADES,
    get_polyphenol_database,
)
from model import (
    calculate_nades_properties,
    ep_extraction_score,
    nep_extraction_score,
    stability_score,
    run_full_simulation,
    compare_thesis_nades,
    sweep_all_nades,
    is_same_compound,
    par_inmiscible,
    ultrasound_boost,
    economic_analysis,
    extraction_kinetics,
    sl_curve,
    nep_monte_carlo,
    nades_reuse_cycles,
    generate_experimental_design,
    thermal_degradation,
    simulate_3step_process,
    ep_monte_carlo,
)

LICENSE_NOTICE = (
    "© 2026 Cristofher Ferrada — Pontificia Universidad Católica de Valparaíso (PUCV). "
    "Licenciado bajo Apache License 2.0. Ver LICENSE."
)

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SimExtract — CFERRADA 2026 · Beta 0.6",
    page_icon="🫐",
    layout="wide",
    initial_sidebar_state="expanded",
)

from tema import inyectar_tema

inyectar_tema()

st.markdown(
    """
<style>
    /* Títulos */
    .main-title  {font-size:2rem;font-weight:800;color:#0d1f35;margin-bottom:0}
    .sub-title   {font-size:.92rem;color:#344a5e;margin-top:2px;font-style:italic;font-weight:500}
    .author-line {font-size:.80rem;color:#344a5e;margin-top:4px;font-weight:600;letter-spacing:.03em}

    /* Tarjetas de propiedades en sidebar */
    .prop-card   {background:#ddeeff;border-left:4px solid #1a6fa0;
                  border-radius:6px;padding:.65rem 1rem;margin-bottom:.45rem}
    .prop-label  {font-size:.72rem;color:#1a3a52;text-transform:uppercase;
                  letter-spacing:.06em;font-weight:700}
    .prop-value  {font-size:1.30rem;font-weight:800;color:#0d1f35}
    .prop-unit   {font-size:.78rem;color:#1a3a52;font-weight:600}

    /* Badges de aviso */
    .novel-badge {background:#fff0b0;border:2px solid #d4a000;border-radius:5px;
                  padding:.35rem .8rem;font-size:.83rem;color:#5a3800;font-weight:600}
    .comb-badge  {background:#c8f0d0;border:2px solid #1a8a40;border-radius:5px;
                  padding:.35rem .8rem;font-size:.83rem;color:#0a3d1a;font-weight:600}
    .ref-badge   {background:#e8ecf8;border:1px solid #6080c0;border-radius:4px;
                  padding:.25rem .6rem;font-size:.76rem;color:#1a2860;font-weight:600}

    /* Texto general de sección */
    .section-h   {font-size:1.1rem;font-weight:700;color:#0d1f35;margin-bottom:.3rem}

    /* Mejora contraste en tablas Streamlit */
    [data-testid="stDataFrame"] td {color: #0d1f35 !important; font-weight:500}

    /* Tarjeta de parte de planta */
    .part-card {border-radius:8px;padding:.75rem 1.1rem;margin-bottom:.6rem;
                border-left:5px solid #888}
    .part-card b {font-size:1.0rem}
    .part-card small {font-size:.78rem;line-height:1.5}
</style>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# DETECCIÓN DE IDIOMA DEL BROWSER
# ─────────────────────────────────────────────
# Idioma activo: viene del parámetro ?lang= en la URL (persistente).
# Default: español. El selector en el sidebar permite cambiar en cualquier momento.
LANG = st.query_params.get("lang", "es")
if LANG not in ("es", "en"):
    LANG = "es"

# ─────────────────────────────────────────────
# TRADUCCIONES (UI + descripciones principales)
# ─────────────────────────────────────────────
TR = {
    # ── Sidebar ──
    "sidebar_title": {"es": "## 🫐 SimExtract", "en": "## 🫐 SimExtract"},
    "sidebar_subtitle": {
        "es": "**para extraer polifenoles · Beta 0.6**",
        "en": "**for polyphenol extraction · Beta 0.6**",
    },
    "lang_label": {"es": "Idioma / Language", "en": "Language / Idioma"},
    "plant_header": {"es": "### 🌿 Parte de la planta", "en": "### 🌿 Plant Part"},
    "plant_radio": {"es": "Seleccionar parte a simular", "en": "Select plant part to simulate"},
    "plant_radio_help": {
        "es": "Cambia la base de datos de polifenoles según la parte de la planta.",
        "en": "Changes the polyphenol database according to the plant part.",
    },
    "plant_fruit": {"es": "🫐 Fruto (Baya)", "en": "🫐 Fruit (Berry)"},
    "plant_leaves": {"es": "🌿 Hojas", "en": "🌿 Leaves"},
    "plant_stem": {"es": "🪵 Tallo / Corteza", "en": "🪵 Stem / Bark"},
    "nades_header": {"es": "### ⚗️ Diseña tu NADES", "en": "### ⚗️ Design your NADES"},
    "hba_label": {"es": "HBA (Aceptor H-Bond)", "en": "HBA (H-Bond Acceptor)"},
    "hbd_label": {"es": "HBD (Donador H-Bond)", "en": "HBD (H-Bond Donor)"},
    "ratio_label": {"es": "Razón HBA : HBD", "en": "HBA : HBD Ratio"},
    "water_label": {"es": "Agua añadida (%)", "en": "Added Water (%)"},
    "temp_label": {"es": "Temperatura (°C)", "en": "Temperature (°C)"},
    "weights_header": {
        "es": "### ⚖️ Pesos de extracción simultánea",
        "en": "### ⚖️ Simultaneous Extraction Weights",
    },
    "ep_weight_label": {"es": "Peso EP en score combinado", "en": "EP weight in combined score"},
    "ep_weight_help": {
        "es": "0.55 = 55% EP · 45% NEP. Ajusta según el objetivo de tu extracción.",
        "en": "0.55 = 55% EP · 45% NEP. Adjust according to your extraction goal.",
    },
    "uae_header": {"es": "### 🔊 Ultrasonido (UAE)", "en": "### 🔊 Ultrasound (UAE)"},
    "freq_label": {"es": "Frecuencia (kHz)", "en": "Frequency (kHz)"},
    "freq_help": {
        "es": "0 kHz = extracción convencional sin ultrasonido. Óptimo ~20-25 kHz para máxima cavitación.",
        "en": "0 kHz = conventional extraction without ultrasound. Optimal ~20-25 kHz for maximum cavitation.",
    },
    "no_us": {"es": "Sin ultrasonido (convencional)", "en": "No ultrasound (conventional)"},
    "low_freq_warn": {
        "es": "⚠️ Baja frecuencia: alta energía — revisar estabilidad de antocianinas",
        "en": "⚠️ Low frequency: high energy — check anthocyanin stability",
    },
    "proc_header": {"es": "### 🌡️ Condiciones del Proceso", "en": "### 🌡️ Process Conditions"},
    "proc_temp_label": {"es": "Temperatura extracción (°C)", "en": "Extraction Temperature (°C)"},
    "proc_temp_help": {
        "es": "Rango óptimo 50-60°C (Paso 1 UAE). Afecta degradación térmica.",
        "en": "Optimal range 50-60°C (Step 1 UAE). Affects thermal degradation.",
    },
    "proc_time_label": {"es": "Tiempo extracción (min)", "en": "Extraction Time (min)"},
    "proc_time_help": {
        "es": "Rango óptimo 9-30 min (Paso 1 UAE).",
        "en": "Optimal range 9-30 min (Step 1 UAE).",
    },
    "filter_header": {"es": "### 🔬 Filtro de compuestos", "en": "### 🔬 Compound Filter"},
    "major_only": {"es": "Solo compuestos principales", "en": "Major compounds only"},
    "major_help": {
        "es": "Filtrar por is_major (concentración relativa > 10% del máximo)",
        "en": "Filter by is_major (relative concentration > 10% of maximum)",
    },
    "calc_props": {"es": "### 📐 Propiedades calculadas", "en": "### 📐 Calculated Properties"},
    "prop_pol": {"es": "Polaridad (ETN)", "en": "Polarity (ETN)"},
    "prop_visc": {"es": "Viscosidad", "en": "Viscosity"},
    "prop_pH": {"es": "pH efectivo", "en": "Effective pH"},
    "prop_hbd": {"es": "Cap. HBD efectiva", "en": "Effective HBD Cap."},
    "prop_antioxid": {"es": "Antioxid. NADES", "en": "NADES Antioxid."},
    # ── Pestañas principales ──
    "tab1": {"es": "⚡ Resultados", "en": "⚡ Results"},
    "tab2": {"es": "🔬 Análisis", "en": "🔬 Analysis"},
    "tab3": {"es": "🔊 Proceso UAE · 3 Pasos", "en": "🔊 UAE Process · 3 Steps"},
    "tab4": {"es": "📐 Optimización", "en": "📐 Optimization"},
    "tab5": {"es": "💰 Economía", "en": "💰 Economics"},
    "tab6": {"es": "📊 Mis Datos", "en": "📊 My Data"},
    "tab7": {"es": "🎯 Recomendador", "en": "🎯 Recommender"},
    "tab8": {"es": "📚 Metodología", "en": "📚 Methodology"},
    "tab9": {"es": "🧫 HPTLC", "en": "🧫 HPTLC"},
    # ── Navegación de primer nivel ──
    "nav_disenar": {"es": "🧪 Diseñar", "en": "🧪 Design"},
    "nav_lab": {"es": "🔬 Laboratorio", "en": "🔬 Laboratory"},
    # ── Sub-tabs tab2 ──
    "atab_ep": {"es": "🟦 Extracción EP", "en": "🟦 EP Extraction"},
    "atab_nep": {"es": "🟥 Extracción NEP", "en": "🟥 NEP Extraction"},
    "atab_stab": {"es": "🟩 Estabilidad", "en": "🟩 Stability"},
    "atab_int": {"es": "⚛️ Interacción", "en": "⚛️ Interaction"},
    # ── Sub-tabs tab4 ──
    "otab_kin": {"es": "📈 Cinética + S:L", "en": "📈 Kinetics + S:L"},
    "otab_dex": {"es": "🧪 Diseño Experimental", "en": "🧪 Experimental Design"},
    # ── Sub-tabs tab7 ──
    "rtab_rec": {"es": "🎯 Recomendador Global", "en": "🎯 Global Recommender"},
    "rtab_comp": {"es": "⚖️ Comparador NADES", "en": "⚖️ NADES Comparator"},
    "rtab_th": {"es": "🧪 Cribado Tesis", "en": "🧪 Thesis Screening"},
    # ── Modo Tesis ──
    "modo_tesis_lbl": {"es": "🎓 Modo Tesis", "en": "🎓 Thesis Mode"},
    "modo_tesis_help": {
        "es": "Activa numeración de figuras (F1.1, F1.2…) y leyendas formales para la tesis doctoral.",
        "en": "Enables figure numbering (F1.1, F1.2…) and formal captions for the doctoral thesis.",
    },
    # ── Informe HTML (F3) ──
    "t1_report_btn": {
        "es": "📄 Generar Informe HTML completo",
        "en": "📄 Generate full HTML Report",
    },
    "t1_report_dl": {"es": "💾 Descargar Informe HTML", "en": "💾 Download HTML Report"},
    "t1_report_ok": {
        "es": "Informe generado — descarga disponible abajo.",
        "en": "Report generated — download available below.",
    },
    # ── Comparador F1 ──
    "comp_title": {
        "es": "### ⚖️ Comparador de NADES — Análisis Lado a Lado",
        "en": "### ⚖️ NADES Comparator — Side-by-Side Analysis",
    },
    "comp_desc": {
        "es": "Configura dos NADES y compara directamente EP, NEP, Estabilidad y Score combinado.",
        "en": "Configure two NADES and directly compare EP, NEP, Stability and Combined Score.",
    },
    "comp_nades_a": {"es": "### NADES A", "en": "### NADES A"},
    "comp_nades_b": {"es": "### NADES B", "en": "### NADES B"},
    "comp_run": {"es": "⚖️ Comparar NADES A vs B", "en": "⚖️ Compare NADES A vs B"},
    # ── Header principal ──
    "main_title": {
        "es": "SimExtract — simulador de extracción de polifenoles",
        "en": "SimExtract for Polyphenol Extraction",
    },
    "author_line": {
        "es": (
            "© 2026 Cristofher Ferrada · PUCV · Beta 0.6 · "
            "Licenciado bajo Apache License 2.0 · "
            "Modelos basados en literatura científica indexada (ver pestaña Metodología)"
        ),
        "en": (
            "© 2026 Cristofher Ferrada · PUCV · Beta 0.6 · "
            "Licensed under Apache License 2.0 · "
            "Models based on indexed scientific literature (see Methodology tab)"
        ),
    },
    "nades_active": {"es": "NADES activo", "en": "Active NADES"},
    "part_lbl": {"es": "Parte", "en": "Part"},
    # ── Tab 1 ──
    "t1_profile": {"es": "#### Perfil del NADES", "en": "#### NADES Profile"},
    "t1_indices": {"es": "#### Índices por polifenol", "en": "#### Indices by polyphenol"},
    "t1_global": {"es": "#### Vista comparativa global", "en": "#### Global comparative view"},
    "t1_water": {
        "es": "#### Efecto del % de agua en los índices (a ratio y T fijos)",
        "en": "#### Effect of water % on indices (fixed ratio and T)",
    },
    "t1_export": {"es": "#### 📥 Exportar resultados", "en": "#### 📥 Export results"},
    "t1_excel_btn": {
        "es": "📊 Generar Excel con todos los resultados",
        "en": "📊 Generate Excel with all results",
    },
    "t1_excel_dl": {"es": "💾 Descargar Excel", "en": "💾 Download Excel"},
    "t1_excel_ok": {
        "es": "Excel generado con 5 hojas: Propiedades NADES · Simulación · Cinética · Curva S:L · Resumen",
        "en": "Excel generated with 5 sheets: NADES Properties · Simulation · Kinetics · S:L Curve · Summary",
    },
    "gauge_ep": {"es": "Índice EP promedio", "en": "Average EP Index"},
    "gauge_nep": {"es": "Índice NEP promedio", "en": "Average NEP Index"},
    "gauge_stab": {"es": "Estabilidad promedio", "en": "Average Stability"},
    "gauge_comb": {"es": "EP+NEP combinado", "en": "Combined EP+NEP"},
    "radar_pol": {"es": "Polaridad", "en": "Polarity"},
    "radar_flu": {"es": "Fluidez", "en": "Fluidity"},
    "radar_hbd": {"es": "Cap. HBD", "en": "HBD Cap."},
    "radar_hba": {"es": "Cap. HBA", "en": "HBA Cap."},
    "radar_acid": {"es": "Acidez", "en": "Acidity"},
    "radar_antx": {"es": "Antioxidante", "en": "Antioxidant"},
    "col_compound": {"es": "Compuesto", "en": "Compound"},
    "col_class": {"es": "Clase", "en": "Class"},
    "col_type": {"es": "Tipo", "en": "Type"},
    # ── Tab 2 ──
    "t2_ep_title": {
        "es": "### Extracción de Polifenoles Extraíbles (EP)",
        "en": "### Extractable Polyphenol (EP) Extraction",
    },
    "t2_ep_ranking": {"es": "#### Ranking EP", "en": "#### EP Ranking"},
    "t2_ep_factors": {
        "es": "#### Desglose de factores por polifenol",
        "en": "#### Factor breakdown by polyphenol",
    },
    "t2_ep_filter": {"es": "Filtrar por clase de polifenol", "en": "Filter by polyphenol class"},
    "filter_all": {"es": "Todas", "en": "All"},
    "t2_nep_title": {
        "es": "### Extracción de Polifenoles No Extraíbles (NEP)",
        "en": "### Non-Extractable Polyphenol (NEP) Extraction",
    },
    "t2_nep_desc": {
        "es": (
            "Los **NEP** (Polifenoles No Extraíbles) están asociados a la matriz "
            "vegetal — principalmente pared celular y proteínas — y no se liberan con "
            "solventes convencionales. El NADES actúa como agente **disruptivo de matriz** "
            "mediante su alta viscosidad, capacidad HBD/HBA y efecto de pH, en combinación "
            "con UAE para romper los enlaces covalentes y no covalentes que los retienen. "
            "Techo sin UAE: **85%** · Con UAE: hasta **95%**"
        ),
        "en": (
            "**NEP** (Non-Extractable Polyphenols) are associated with the plant "
            "matrix — primarily cell wall and proteins — and are not released by "
            "conventional solvents. NADES acts as a **matrix-disrupting agent** "
            "through its high viscosity, HBD/HBA capacity and pH effect, combined "
            "with UAE to break the covalent and non-covalent bonds retaining them. "
            "Ceiling without UAE: **85%** · With UAE: up to **95%**"
        ),
    },
    "t2_stab_title": {
        "es": "### Estabilidad de Polifenoles en Presencia del NADES",
        "en": "### Polyphenol Stability in the Presence of NADES",
    },
    "t2_stab_desc": {
        "es": (
            "**Mecanismo principal:** Los NADES forman redes de puentes de hidrógeno "
            "con los grupos **–OH fenólicos**, bloqueándolos físicamente del O₂ y "
            "radicales libres. Además, componentes como el ácido cítrico o málico "
            "**quelan Fe³⁺**, previniendo la oxidación catalítica de Fenton."
        ),
        "en": (
            "**Main mechanism:** NADES form hydrogen-bond networks "
            "with **phenolic –OH groups**, physically blocking them from O₂ and "
            "free radicals. Additionally, components such as citric or malic acid "
            "**chelate Fe³⁺**, preventing Fenton catalytic oxidation."
        ),
    },
    "t2_int_title": {
        "es": "### Interacción NADES–Polifenol",
        "en": "### NADES–Polyphenol Interaction",
    },
    # ── Tab 3 ──
    "t3_uae_title": {
        "es": "### Extracción Asistida por Ultrasonido (UAE)",
        "en": "### Ultrasound-Assisted Extraction (UAE)",
    },
    "t3_uae_desc": {
        "es": (
            "El ultrasonido genera **cavitación acústica**: burbujas microscópicas que "
            "colapsan y producen microjet y ondas de choque que **rompen la pared celular**, "
            "aumentan la transferencia de masa del NADES y liberan polifenoles unidos (NEP). "
            "La frecuencia óptima para máxima cavitación es **~20-25 kHz**."
        ),
        "en": (
            "Ultrasound generates **acoustic cavitation**: microscopic bubbles that "
            "collapse and produce microjets and shock waves that **break the cell wall**, "
            "increase NADES mass transfer and release bound polyphenols (NEP). "
            "The optimal frequency for maximum cavitation is **~20-25 kHz**."
        ),
    },
    "t3_freq_h": {
        "es": "#### Realce de extracción según frecuencia (kHz)",
        "en": "#### Extraction enhancement by frequency (kHz)",
    },
    "t3_total_khz": {
        "es": "##### Índice total de extracción vs kHz",
        "en": "##### Total extraction index vs kHz",
    },
    "t3_increment": {
        "es": "##### Incremento % respecto a extracción sin US",
        "en": "##### Increment % relative to extraction without US",
    },
    "t3_3step": {
        "es": "### Simulación del Proceso de 3 Pasos",
        "en": "### 3-Step Process Simulation",
    },
    "t3_arrhenius": {
        "es": "### Degradación Térmica — Modelo Arrhenius",
        "en": "### Thermal Degradation — Arrhenius Model",
    },
    # ── Tab 4 ──
    "t4_kin_title": {"es": "### 📐 Cinética de Extracción", "en": "### 📐 Extraction Kinetics"},
    "t4_kin_desc": {
        "es": (
            "Modelo de **primer orden** para la evolución de la extracción EP y NEP con el tiempo. "
            "La constante de velocidad *k* depende de la viscosidad, temperatura y el UAE. "
            "El tiempo óptimo *t₉₀* es cuando se alcanza el 90% del rendimiento de equilibrio."
        ),
        "en": (
            "**First-order model** for the time evolution of EP and NEP extraction. "
            "The rate constant *k* depends on viscosity, temperature and UAE. "
            "The optimal time *t₉₀* is when 90% of the equilibrium yield is reached."
        ),
    },
    "t4_dex_title": {
        "es": "### 🧪 Generador de Diseño Experimental",
        "en": "### 🧪 Experimental Design Generator",
    },
    "t4_dex_desc": {
        "es": (
            "Genera la **matriz de ensayos** para optimizar la extracción con NADES. "
            "Elige el tipo de diseño y define los niveles de cada factor. "
            "Descarga la tabla como CSV para ejecutar los experimentos."
        ),
        "en": (
            "Generates the **trial matrix** to optimize NADES extraction. "
            "Choose the design type and define the factor levels. "
            "Download the table as CSV to run the experiments."
        ),
    },
    "t4_design_type": {"es": "Tipo de diseño", "en": "Design type"},
    # ── Tab 5 ──
    "t5_title": {
        "es": "### 💰 Análisis Económico de la Extracción con NADES",
        "en": "### 💰 Economic Analysis of NADES Extraction",
    },
    "t5_desc": {
        "es": (
            "Estimación de costos para fabricar el NADES diseñado y realizar extracciones "
            "de polifenoles de *Berberis microphylla*. Precios USD grado laboratorio (reactivos analíticos)."
        ),
        "en": (
            "Cost estimation for preparing the designed NADES and performing polyphenol "
            "extractions from *Berberis microphylla*. USD laboratory-grade prices (analytical reagents)."
        ),
    },
    "t5_sample": {
        "es": "Masa de muestra (g peso seco liofilizado)",
        "en": "Sample mass (g freeze-dried dry weight)",
    },
    "t5_sl_ratio": {"es": "Razón sólido:líquido (mL/g)", "en": "Solid:liquid ratio (mL/g)"},
    "t5_reps": {"es": "N° de repeticiones/réplicas", "en": "N° of repetitions/replicates"},
    "t5_summary": {"es": "#### Resumen de una extracción", "en": "#### Single extraction summary"},
    "t5_breakdown": {"es": "#### Desglose de componentes", "en": "#### Component breakdown"},
    # ── Tab 6 ──
    "t6_title": {
        "es": "### 📊 Mis Datos — Importar y Comparar con el Modelo",
        "en": "### 📊 My Data — Import and Compare with Model",
    },
    "t6_desc": {
        "es": (
            "Carga tus resultados experimentales en formato CSV y compáralos "
            "con la predicción del simulador. El programa calcula el R² y muestra "
            "dónde el modelo se acerca o se aleja de la realidad."
        ),
        "en": (
            "Upload your experimental results in CSV format and compare them "
            "with the simulator's prediction. The program calculates R² and shows "
            "where the model is close to or diverges from reality."
        ),
    },
    "t6_format": {"es": "📄 Formato del CSV esperado", "en": "📄 Expected CSV format"},
    "t6_upload": {"es": "Sube tu CSV experimental", "en": "Upload your experimental CSV"},
    # ── Tab 7 ──
    "t7_rec_title": {
        "es": "### 🎯 Recomendador Global de NADES",
        "en": "### 🎯 Global NADES Recommender",
    },
    "t7_th_title": {
        "es": "### Cribado Comparativo — 6 NADES de la Tesis",
        "en": "### Comparative Screening — 6 Thesis NADES",
    },
    "t7_th_desc": {
        "es": (
            "Simulación de los 6 sistemas NADES del diseño experimental de **Etapa 1**. "
            "Criterios experimentales: **TPC** (Folin-Ciocalteu) · **TAC** (pH diferencial) "
            "· **DPPH** · **FRAP**"
        ),
        "en": (
            "Simulation of the 6 NADES systems from the **Stage 1** experimental design. "
            "Experimental criteria: **TPC** (Folin-Ciocalteu) · **TAC** (pH differential) "
            "· **DPPH** · **FRAP**"
        ),
    },
    # ── Tab 8 ──
    "t8_title": {
        "es": "### Fundamento Científico de los Modelos",
        "en": "### Scientific Foundation of the Models",
    },
    # ── Común ──
    "run_btn": {"es": "▶ Ejecutar", "en": "▶ Run"},
    "export_csv": {"es": "📥 Exportar CSV", "en": "📥 Export CSV"},
    "no_data": {"es": "No hay datos disponibles.", "en": "No data available."},
}


def t(key: str) -> str:
    """Return translated UI string for the active LANG."""
    entry = TR.get(key)
    if entry is None:
        return key
    return entry.get(LANG, entry.get("es", key))


# ── Contador de figuras para Modo Tesis ──
_fig_counter: dict = {}


def fig_caption(tab_n: int, desc: str) -> None:
    """Show a formal figure caption when Thesis Mode is active.

    Call AFTER st.plotly_chart() to place the caption below the figure.
    Only renders when modo_tesis is True (evaluated at call-time from session_state).
    """
    if not st.session_state.get("modo_tesis_toggle", False):
        return
    key = f"tab{tab_n}"
    _fig_counter[key] = _fig_counter.get(key, 0) + 1
    st.markdown(
        f'<p style="font-size:.75rem;color:#344a5e;text-align:center;'
        f'margin-top:-12px;margin-bottom:8px">'
        f"<i>Figura {tab_n}.{_fig_counter[key]} — {desc}</i></p>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# DATOS (cacheados)
# ─────────────────────────────────────────────
@st.cache_data
def load_poly():
    """Base de polifenoles de FRUTO de B. microphylla (Ruiz et al. 2024, Tabla 2)."""
    return get_polyphenol_database()


# ─────────────────────────────────────────────
# PALETA DE COLORES
# ─────────────────────────────────────────────
COLORS_EP = px.colors.sequential.Blues[3:]
COLORS_NEP = px.colors.sequential.Reds[3:]
COLORS_STAB = px.colors.sequential.Greens[3:]
THESIS_COLORS = [n["color"] for n in THESIS_NADES]

# ─────────────────────────────────────────────
# SIDEBAR — CONSTRUCTOR DE NADES EN TIEMPO REAL
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(t("sidebar_title"))
    st.markdown(t("sidebar_subtitle"))
    st.markdown(
        '<span style="font-size:.75rem;color:#344a5e;font-weight:600">' f"{LICENSE_NOTICE}</span>",
        unsafe_allow_html=True,
    )

    # ── Selector de idioma ──
    _lang_opts = {"es": "🇨🇱 Español", "en": "🇬🇧 English"}
    _lang_sel = st.selectbox(
        t("lang_label"),
        options=list(_lang_opts.keys()),
        format_func=lambda x: _lang_opts[x],
        index=0 if LANG == "es" else 1,
        key="lang_selector",
    )
    if _lang_sel != LANG:
        st.query_params["lang"] = _lang_sel
        st.rerun()

    st.divider()

    st.markdown(t("nades_header"))

    hba_sel = st.selectbox(t("hba_label"), list(HBA_COMPONENTS.keys()), index=0, key="sel_hba")
    hbd_sel = st.selectbox(t("hbd_label"), list(HBD_COMPONENTS.keys()), index=0, key="sel_hbd")
    ratio_sel = st.select_slider(
        t("ratio_label"),
        options=list(RATIOS_DISPONIBLES.keys()),
        value="1:1",
        key="sel_ratio",
    )
    water_pct = st.slider(t("water_label"), 0, 50, 30, step=5, key="sel_water")
    temp_C = st.slider(t("temp_label"), 20, 80, 40, step=5)

    st.divider()
    st.markdown(t("weights_header"))
    peso_ep = st.slider(
        t("ep_weight_label"),
        min_value=0.30,
        max_value=0.80,
        value=0.55,
        step=0.05,
        help=t("ep_weight_help"),
    )
    peso_nep = round(1.0 - peso_ep, 2)
    st.caption(f"EP: {peso_ep:.0%}  ·  NEP: {peso_nep:.0%}")

    st.divider()
    st.markdown(t("uae_header"))
    freq_us = st.slider(
        t("freq_label"),
        min_value=0,
        max_value=100,
        value=0,
        step=5,
        help=t("freq_help"),
    )
    if freq_us > 0:
        peak = 22.0
        if freq_us < 5:
            _cav = (freq_us / 5.0) * np.exp(-((5.0 - peak) ** 2) / (2 * 12.0**2))
        elif freq_us <= peak:
            _cav = np.exp(-((freq_us - peak) ** 2) / (2 * 12.0**2))
        else:
            _cav = np.exp(-((freq_us - peak) ** 2) / (2 * 28.0**2))
        _cav = float(min(1.0, max(0.0, _cav)))
        _ep_b = round(0.18 * _cav * 100, 1)
        _nep_b = round(0.28 * _cav * 100, 1)
        st.caption(f"Cavitación: {_cav*100:.0f}% · +EP: {_ep_b}% · +NEP: {_nep_b}%")
        if freq_us <= 30:
            st.caption(t("low_freq_warn"))
    else:
        st.caption(t("no_us"))

    st.divider()
    st.markdown(t("proc_header"))
    proc_temp = st.slider(
        t("proc_temp_label"),
        20,
        80,
        55,
        step=5,
        help=t("proc_temp_help"),
    )
    proc_time = st.slider(
        t("proc_time_label"),
        5,
        60,
        20,
        step=5,
        help=t("proc_time_help"),
    )
    st.caption(
        f"T={proc_temp}°C · t={proc_time} min · "
        "Ref: Ferrada, C. Tesis Doctoral 2026 — Etapa 2, Paso 1"
    )

    st.divider()
    st.markdown(t("filter_header"))
    solo_principales = st.toggle(
        t("major_only"),
        value=False,
        help=t("major_help"),
    )

    st.divider()
    modo_tesis = st.toggle(
        t("modo_tesis_lbl"),
        value=False,
        help=t("modo_tesis_help"),
        key="modo_tesis_toggle",
    )
    if modo_tesis:
        st.caption("🎓 Numeración de figuras activa (F1.1, F2.1…)")

    ratio_hba, ratio_hbd = RATIOS_DISPONIBLES[ratio_sel]

    # Calcular propiedades en tiempo real
    props = calculate_nades_properties(
        hba_sel,
        hbd_sel,
        ratio_hba,
        ratio_hbd,
        water_pct,
        temp_C,
        HBA_COMPONENTS,
        HBD_COMPONENTS,
    )

    if is_same_compound(hba_sel, hbd_sel):
        st.warning(
            "⚠️ HBA y HBD son el mismo compuesto — esto **no** es un NADES sino un "
            "compuesto puro. Selecciona componentes diferentes para formar una mezcla eutéctica."
            if LANG == "es"
            else "⚠️ HBA and HBD are the same compound — this is **not** a NADES but a "
            "pure compound. Select different components to form a eutectic mixture."
        )

    if par_inmiscible(hba_sel, hbd_sel, HBA_COMPONENTS, HBD_COMPONENTS):
        st.error(
            "⛔ Par **inmiscible**: un componente terpenoide/graso (timol, mentol, alcanfor, "
            "ác. decanoico) no forma eutéctico único con azúcares, polioles ni ácidos "
            "polihidroxilados. Combínalo con otro hidrofóbico o con ác. láctico/acético/levulínico."
            if LANG == "es"
            else "⛔ **Immiscible** pair: a terpenoid/fatty component (thymol, menthol, camphor, "
            "decanoic acid) does not form a single eutectic with sugars, polyols or "
            "polyhydroxy acids. Pair it with another hydrophobic one or with "
            "lactic/acetic/levulinic acid."
        )
    elif props["bifasico"]:
        st.warning(
            f"💧 Sistema **hidrofóbico (HDES)**: sólo ~{props['water_pct_efectivo']:.1f}% del "
            f"{water_pct}% de agua se incorpora a la fase eutéctica; el resto forma una "
            "segunda fase acuosa. La simulación usa el agua efectiva."
            if LANG == "es"
            else f"💧 **Hydrophobic (HDES)** system: only ~{props['water_pct_efectivo']:.1f}% of "
            f"the {water_pct}% water dissolves in the eutectic phase; the rest forms a "
            "second aqueous phase. The simulation uses the effective water."
        )

    st.divider()
    st.markdown(t("calc_props"))

    # Cada propiedad viene con su lectura en lenguaje llano y su fuente: la ficha
    # anterior mostraba el número pero nunca por qué importaba ni quién lo respalda.
    from explicacion import explicar_propiedades
    from tabs.componentes import ficha_explicada

    for _lectura in explicar_propiedades(props):
        ficha_explicada(_lectura)

    st.divider()
    st.caption(f"HBA: {HBA_COMPONENTS[hba_sel]['descripcion'][:60]}…")
    st.caption(f"HBD: {HBD_COMPONENTS[hbd_sel]['descripcion'][:60]}…")


def seccion(_titulo: str = ""):
    """Return a container preceded by a rule.

    Replaces a nested `st.tabs` level: the content flows as one scrolling page
    instead of hiding behind a third row of tabs. Because it returns a container,
    the existing `with <name>:` blocks keep working untouched.

    No heading is emitted: every block already opens with its own title, so one
    here would only duplicate it. The argument is kept so call sites read as the
    section they open.
    """
    st.divider()
    return st.container()


# ─────────────────────────────────────────────
# CARGA DE BASE DE DATOS (según parte de planta)
# ─────────────────────────────────────────────
poly_df = load_poly()

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown(f'<p class="main-title">{t("main_title")}</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-title">Simulación interactiva de NADES para extracción de polifenoles '
    "de <em>Berberis microphylla</em> G. Forst · Fruto (baya) · "
    "EP: Ruiz et al. (2024) Horticulturae 10, 458 · NEP: modelo teórico novel · "
    "Estabilidad oxidativa · Extracción Simultánea EP+NEP · UAE</p>",
    unsafe_allow_html=True,
)
st.markdown(
    f'<p class="author-line">{t("author_line")}</p>',
    unsafe_allow_html=True,
)

from tabs.componentes import nades_activo

nades_label = f"**{nades_activo(props, hba_sel.split('(')[0].strip(), hbd_sel, ratio_sel)}**"
st.info(
    f"{t('nades_active')}: {nades_label}  ·  Fruto (baya)  ·  "
    f"{(poly_df['tipo'] == 'EP').sum()} EP + {(poly_df['tipo'] == 'NEP').sum()} NEP"
)

# ─────────────────────────────────────────────
# SIMULACIÓN DEL NADES ACTUAL
# ─────────────────────────────────────────────
sim = run_full_simulation(props, poly_df, peso_ep=peso_ep, freq_us=freq_us)

# Aplicar filtro de compuestos principales si está activo
if solo_principales:
    sim_display = sim[sim["is_major"]].copy()
else:
    sim_display = sim.copy()

ep_poly = sim_display[sim_display["tipo"] == "EP"]
nep_poly = sim_display[sim_display["tipo"] == "NEP"]

avg_ep = ep_poly["EP (%)"].mean() if len(ep_poly) > 0 else 0.0
avg_nep = nep_poly["NEP (%)"].mean() if len(nep_poly) > 0 else 0.0
avg_stab = sim_display["Estab. (%)"].mean() if len(sim_display) > 0 else 0.0
avg_comb = sim_display["Combinado (%)"].mean() if len(sim_display) > 0 else 0.0

# ─────────────────────────────────────────────
# PESTAÑAS
# ─────────────────────────────────────────────
# Dos pestañas, un solo nivel de sub-pestañas. Agrupar en etapas habría creado
# etapa → pestaña → sub-pestaña: tres niveles, y un clic más para llegar a todo.
nav_disenar, nav_lab = st.tabs([t("nav_disenar"), t("nav_lab")])

with nav_disenar:
    tab7, tab1, tab2, tab4, tab5 = st.tabs([t("tab7"), t("tab1"), t("tab2"), t("tab4"), t("tab5")])

with nav_lab:
    tab3, tab9, tab6, tab8 = st.tabs([t("tab3"), t("tab9"), t("tab6"), t("tab8")])


# ══════════════════════════════════════════════════════════
# TAB 1 — TIEMPO REAL
# ══════════════════════════════════════════════════════════
with tab1:
    # ── Gauges principales ──
    def gauge(value, title, color, max_val=100):
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=value,
                title={"text": title, "font": {"size": 13}},
                number={"suffix": "%", "font": {"size": 26}},
                gauge={
                    "axis": {"range": [0, max_val]},
                    "bar": {"color": color},
                    "steps": [
                        {"range": [0, 40], "color": "#ffeaea"},
                        {"range": [40, 70], "color": "#fff3cd"},
                        {"range": [70, 100], "color": "#d4edda"},
                    ],
                    "threshold": {"line": {"color": "#333", "width": 2}, "value": 70},
                },
            )
        )
        fig.update_layout(height=210, margin=dict(l=15, r=15, t=40, b=10))
        return fig

    g1, g2, g3, g4 = st.columns(4)
    with g1:
        st.plotly_chart(gauge(avg_ep, t("gauge_ep"), "#2e86ab"), use_container_width=True)
    with g2:
        st.plotly_chart(gauge(avg_nep, t("gauge_nep"), "#c44536"), use_container_width=True)
    with g3:
        st.plotly_chart(gauge(avg_stab, t("gauge_stab"), "#048a81"), use_container_width=True)
    with g4:
        st.plotly_chart(
            gauge(avg_comb, t("gauge_comb"), "#6b4226", max_val=100), use_container_width=True
        )

    st.markdown(
        f'<div class="comb-badge">🎯 Score combinado EP+NEP: <b>{avg_comb:.1f}%</b> '
        f"(peso EP={peso_ep:.0%} · NEP={peso_nep:.0%}) — "
        f"incluye penalización por asimetría entre fracciones</div>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    col_left, col_right = st.columns([2, 3])

    # ── Radar del NADES ──
    with col_left:
        st.markdown(t("t1_profile"))
        visc_norm = 1 - np.log10(max(props["viscosidad"], 1)) / np.log10(10000)
        radar_vals = {
            t("radar_pol"): props["polaridad"],
            t("radar_flu"): max(0, visc_norm),
            t("radar_hbd"): props["cap_hbd"] / 10,
            t("radar_hba"): props["cap_hba"] / 10,
            t("radar_acid"): max(0, (5 - props["pH"]) / 5),
            t("radar_antx"): props["antioxidant_nades"],
        }
        cats = list(radar_vals.keys()) + [list(radar_vals.keys())[0]]
        vals = list(radar_vals.values()) + [list(radar_vals.values())[0]]

        fig_rad = go.Figure(
            go.Scatterpolar(
                r=vals,
                theta=cats,
                fill="toself",
                name="NADES actual",
                fillcolor="rgba(46,134,171,0.2)",
                line=dict(color="#2e86ab", width=2),
            )
        )
        fig_rad.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            height=320,
            margin=dict(l=30, r=30, t=30, b=30),
        )
        st.plotly_chart(fig_rad, use_container_width=True)
        fig_caption(1, f"Perfil fisicoquímico del NADES activo — {nades_label}")

    # ── Tabla resumen de todos los polifenoles ──
    with col_right:
        st.markdown(t("t1_indices"))
        tbl = sim_display[
            ["abrev", "clase", "tipo", "EP (%)", "NEP (%)", "Estab. (%)", "Combinado (%)"]
        ].copy()
        tbl = tbl.rename(
            columns={"abrev": t("col_compound"), "clase": t("col_class"), "tipo": t("col_type")}
        )

        st.dataframe(
            tbl.style.background_gradient(subset=["EP (%)"], cmap="Blues", vmin=0, vmax=100)
            .background_gradient(subset=["NEP (%)"], cmap="Reds", vmin=0, vmax=80)
            .background_gradient(subset=["Estab. (%)"], cmap="Greens", vmin=0, vmax=100)
            .background_gradient(subset=["Combinado (%)"], cmap="YlOrBr", vmin=0, vmax=100)
            .format(
                {
                    "EP (%)": "{:.1f}",
                    "NEP (%)": "{:.1f}",
                    "Estab. (%)": "{:.1f}",
                    "Combinado (%)": "{:.1f}",
                }
            ),
            use_container_width=True,
            hide_index=True,
            height=310,
        )

    # ── Gráfico de barras comparativo EP vs NEP vs Combinado ──
    st.markdown(t("t1_global"))
    melt = sim_display[["abrev", "EP (%)", "NEP (%)", "Combinado (%)"]].melt(
        id_vars="abrev", var_name="Índice", value_name="Valor (%)"
    )
    color_map = {"EP (%)": "#2e86ab", "NEP (%)": "#c44536", "Combinado (%)": "#6b4226"}
    fig_cmp = px.bar(
        melt,
        x="abrev",
        y="Valor (%)",
        color="Índice",
        barmode="group",
        color_discrete_map=color_map,
        labels={"abrev": "Polifenol", "Valor (%)": "Índice (%)"},
    )
    fig_cmp.update_layout(
        height=400,
        xaxis_tickangle=-40,
        legend=dict(orientation="h", y=-0.35),
    )
    st.plotly_chart(fig_cmp, use_container_width=True)
    fig_caption(
        1,
        "Índices EP · NEP · Score combinado por polifenol. EP: Ruiz et al. (2024). NEP: Ferrada (2026).",
    )
    st.caption(
        "Ref EP: Ruiz et al. (2024) Horticulturae 10, 458 — 28 compuestos HPLC-DAD-ESI-MS/MS · "
        "Modelo EP: Espino et al. (2016) Talanta 162, 412 (polaridad, HBD, pH) · "
        "Modelo NEP: Ferrada, C. Tesis Doctoral 2026 (contribución novel) · "
        "Score combinado: Ferrada, C. Tesis Doctoral 2026"
    )

    # ── Efecto del agua — curva de respuesta ──
    st.markdown(t("t1_water"))
    water_range = range(0, 55, 5)
    water_curve = []
    for w in water_range:
        p_w = calculate_nades_properties(
            hba_sel,
            hbd_sel,
            ratio_hba,
            ratio_hbd,
            w,
            temp_C,
            HBA_COMPONENTS,
            HBD_COMPONENTS,
        )
        s_w = run_full_simulation(p_w, poly_df, peso_ep=peso_ep, freq_us=freq_us)
        ep_w = s_w[s_w["tipo"] == "EP"]["EP (%)"].mean()
        nep_w = s_w[s_w["tipo"] == "NEP"]["NEP (%)"].mean()
        stab_w = s_w["Estab. (%)"].mean()
        comb_w = s_w["Combinado (%)"].mean()
        water_curve.append(
            {"Agua (%)": w, "EP": ep_w, "NEP": nep_w, "Estab.": stab_w, "Combinado": comb_w}
        )
    wc_df = pd.DataFrame(water_curve)
    fig_water = go.Figure()
    fig_water.add_trace(
        go.Scatter(
            x=wc_df["Agua (%)"], y=wc_df["EP"], name="EP", line=dict(color="#2e86ab", width=2)
        )
    )
    fig_water.add_trace(
        go.Scatter(
            x=wc_df["Agua (%)"], y=wc_df["NEP"], name="NEP", line=dict(color="#c44536", width=2)
        )
    )
    fig_water.add_trace(
        go.Scatter(
            x=wc_df["Agua (%)"],
            y=wc_df["Estab."],
            name="Estab.",
            line=dict(color="#048a81", width=2),
        )
    )
    fig_water.add_trace(
        go.Scatter(
            x=wc_df["Agua (%)"],
            y=wc_df["Combinado"],
            name="Combinado",
            line=dict(color="#6b4226", width=2, dash="dash"),
        )
    )
    fig_water.add_vline(
        x=water_pct, line_dash="dot", line_color="#888", annotation_text=f"Actual: {water_pct}%"
    )
    fig_water.update_layout(
        height=320,
        xaxis_title="Agua añadida (%)",
        yaxis_title="Índice promedio (%)",
        yaxis_range=[0, 100],
        legend=dict(orientation="h", y=-0.25),
    )
    st.plotly_chart(fig_water, use_container_width=True)
    fig_caption(
        1,
        f"Efecto del % agua en índices de extracción (ratio={ratio_sel}, T={temp_C}°C). Ref: Dai et al. (2013).",
    )
    st.caption(
        "Los índices se recalculan automáticamente al cambiar los parámetros del sidebar. "
        "Ref curva agua: Dai et al. (2013) Anal. Chim. Acta 766, 61 (efecto dilución en propiedades DES) · "
        "Chanioti & Tzia (2017) Food Bioprocess Technol. 10, 1999 (óptimo ~25-35% H₂O para extracción)"
    )

    # ── Exportar resultados a Excel ──
    st.markdown("---")
    st.markdown(t("t1_export"))
    if st.button(t("t1_excel_btn"), key="export_excel"):
        import io

        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            # Hoja 1: Resumen NADES
            props_df = pd.DataFrame(
                [
                    {"Parámetro": k, "Valor": round(v, 4) if isinstance(v, float) else v}
                    for k, v in props.items()
                    if not isinstance(v, dict)
                ]
            )
            props_df.to_excel(writer, sheet_name="Propiedades NADES", index=False)

            # Hoja 2: Simulación completa
            sim_export = sim_display[
                ["abrev", "clase", "tipo", "EP (%)", "NEP (%)", "Estab. (%)", "Combinado (%)"]
            ].copy()
            sim_export.to_excel(writer, sheet_name="Simulación", index=False)

            # Hoja 3: Cinética
            try:
                kin_export = extraction_kinetics(
                    props, poly_df, time_max=90, n_points=19, freq_us=freq_us, peso_ep=peso_ep
                )
                kin_export.to_excel(writer, sheet_name="Cinética", index=False)
            except Exception:
                pass

            # Hoja 4: Curva S:L
            try:
                sl_export = sl_curve(props, poly_df, peso_ep=peso_ep)
                sl_export.to_excel(writer, sheet_name="Curva S-L", index=False)
            except Exception:
                pass

            # Hoja 5: Resumen métricas
            summary_df = pd.DataFrame(
                [
                    {
                        "NADES": f"{hba_sel.split('(')[0].strip()} : {hbd_sel}",
                        "Ratio": ratio_sel,
                        "Agua (%)": water_pct,
                        "Temp (°C)": temp_C,
                        "EP promedio (%)": round(avg_ep, 1),
                        "NEP promedio (%)": round(avg_nep, 1),
                        "Estab. promedio (%)": round(avg_stab, 1),
                        "Combinado (%)": round(avg_comb, 1),
                    }
                ]
            )
            summary_df.to_excel(writer, sheet_name="Resumen", index=False)

        buf.seek(0)
        st.download_button(
            label=t("t1_excel_dl"),
            data=buf,
            file_name=f"NADES_{hba_sel.split('(')[0].strip()[:15]}_{hbd_sel[:15]}_fruto.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        st.success(t("t1_excel_ok"))

    # ── F3: Generar Informe HTML completo ──
    st.markdown("---")
    st.markdown("#### 📄 Exportar Informe HTML")
    st.caption(
        "Genera un informe HTML completo con figuras interactivas (Plotly), "
        "tablas de resultados y propiedades del NADES. Listo para imprimir como PDF desde el navegador."
    )
    if st.button(t("t1_report_btn"), key="btn_gen_report"):
        # ── Construir el HTML ──
        _tpc_ref = "Ruiz et al. (2024) Horticulturae 10, 458"
        _nades_name = f"{hba_sel.split('(')[0].strip()} : {hbd_sel} ({ratio_sel})"
        _include_plotly = "cdn"  # primer figura carga Plotly CDN

        # 1) Reconstruir figuras para el informe
        _rep_fig_rad = go.Figure(
            go.Scatterpolar(
                r=vals,
                theta=cats,
                fill="toself",
                name=_nades_name,
                fillcolor="rgba(46,134,171,0.2)",
                line=dict(color="#2e86ab", width=2),
            )
        )
        _rep_fig_rad.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            height=300,
            margin=dict(l=30, r=30, t=30, b=30),
            title=f"Perfil fisicoquímico — {_nades_name}",
        )

        _rep_fig_cmp = px.bar(
            melt,
            x="abrev",
            y="Valor (%)",
            color="Índice",
            barmode="group",
            color_discrete_map=color_map,
            labels={"abrev": "Polifenol", "Valor (%)": "Índice (%)"},
            title=f"Índices EP · NEP · Combinado — {_nades_name}",
        )
        _rep_fig_cmp.update_layout(height=350, xaxis_tickangle=-40)

        _rep_fig_water = go.Figure()
        _rep_fig_water.add_trace(
            go.Scatter(x=wc_df["Agua (%)"], y=wc_df["EP"], name="EP", line=dict(color="#2e86ab"))
        )
        _rep_fig_water.add_trace(
            go.Scatter(x=wc_df["Agua (%)"], y=wc_df["NEP"], name="NEP", line=dict(color="#c44536"))
        )
        _rep_fig_water.add_trace(
            go.Scatter(
                x=wc_df["Agua (%)"], y=wc_df["Estab."], name="Estab.", line=dict(color="#048a81")
            )
        )
        _rep_fig_water.add_trace(
            go.Scatter(
                x=wc_df["Agua (%)"],
                y=wc_df["Combinado"],
                name="Combinado",
                line=dict(color="#6b4226", dash="dash"),
            )
        )
        _rep_fig_water.add_vline(
            x=water_pct, line_dash="dot", annotation_text=f"Actual {water_pct}%"
        )
        _rep_fig_water.update_layout(
            height=300,
            xaxis_title="Agua (%)",
            yaxis_title="Índice (%)",
            yaxis_range=[0, 100],
            title="Efecto del % agua en los índices de extracción",
        )

        # 2) Tabla de propiedades
        _props_html = pd.DataFrame(
            [
                {"Propiedad": "HBA", "Valor": hba_sel},
                {"Propiedad": "HBD", "Valor": hbd_sel},
                {"Propiedad": "Ratio HBA:HBD", "Valor": ratio_sel},
                {"Propiedad": "Agua añadida (%)", "Valor": f"{water_pct}%"},
                {"Propiedad": "Temperatura", "Valor": f"{temp_C} °C"},
                {"Propiedad": "UAE (kHz)", "Valor": f"{freq_us} kHz"},
                {"Propiedad": "Polaridad (ETN)", "Valor": f"{props['polaridad']:.3f}"},
                {"Propiedad": "Viscosidad (cP)", "Valor": f"{props['viscosidad']:.0f}"},
                {"Propiedad": "pH efectivo", "Valor": f"{props['pH']:.2f}"},
                {"Propiedad": "Cap. HBD", "Valor": f"{props['cap_hbd']:.2f}"},
                {"Propiedad": "EP promedio (%)", "Valor": f"{avg_ep:.1f}"},
                {"Propiedad": "NEP promedio (%)", "Valor": f"{avg_nep:.1f}"},
                {"Propiedad": "Estabilidad promedio (%)", "Valor": f"{avg_stab:.1f}"},
                {"Propiedad": "Score combinado (%)", "Valor": f"{avg_comb:.1f}"},
            ]
        ).to_html(index=False, border=0, classes="rep-table")

        # 3) Tabla de simulación
        _sim_html = tbl.to_html(index=False, border=0, classes="rep-table", float_format="%.1f")

        # 4) Figuras como HTML
        _fig_html_rad = pio.to_html(_rep_fig_rad, full_html=False, include_plotlyjs=_include_plotly)
        _fig_html_cmp = pio.to_html(_rep_fig_cmp, full_html=False, include_plotlyjs=False)
        _fig_html_water = pio.to_html(_rep_fig_water, full_html=False, include_plotlyjs=False)

        # 5) Numeración de figuras si modo_tesis
        _fig_prefix = ""
        if st.session_state.get("modo_tesis_toggle", False):
            _fig_prefix = "<p><i>Figura 1.1</i></p>"
            _fig2_prefix = "<p><i>Figura 1.2</i></p>"
            _fig3_prefix = "<p><i>Figura 1.3</i></p>"
        else:
            _fig_prefix = _fig2_prefix = _fig3_prefix = ""

        # 6) Ensamblar HTML
        _html_report = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Informe NADES — {_nades_name}</title>
  <style>
    body {{font-family:Arial,sans-serif;max-width:1100px;margin:auto;padding:2rem;color:#0d1f35}}
    h1   {{color:#0d3b6e;border-bottom:3px solid #0d3b6e;padding-bottom:.4rem}}
    h2   {{color:#1a6fa0;margin-top:2rem}}
    h3   {{color:#344a5e}}
    .rep-table {{border-collapse:collapse;width:100%;margin-bottom:1.5rem}}
    .rep-table td,.rep-table th {{border:1px solid #ccc;padding:.45rem .8rem;font-size:.88rem}}
    .rep-table th {{background:#0d3b6e;color:white;font-weight:700}}
    .rep-table tr:nth-child(even) {{background:#f0f4f8}}
    .badge {{display:inline-block;background:#c8f0d0;border:1px solid #1a8a40;
             border-radius:4px;padding:.2rem .6rem;font-size:.82rem;color:#0a3d1a;font-weight:600}}
    .fig-caption {{font-size:.77rem;color:#344a5e;text-align:center;margin-top:-10px;font-style:italic}}
    footer {{margin-top:3rem;font-size:.75rem;color:#888;border-top:1px solid #ddd;padding-top:1rem}}
  </style>
</head>
<body>
  <h1>🫐 Informe de Extracción con NADES</h1>
  <p><b>NADES activo:</b> {_nades_name} &nbsp;&nbsp;
     <b>Fecha:</b> 2026-05-26</p>
  <p><b>Autor:</b> Cristofher Ferrada &nbsp;&nbsp;
     <b>Versión:</b> SimExtract Beta 0.6 &nbsp;&nbsp;
     <b>Tesis Doctoral PUCV 2026</b></p>
  <p class="badge">Score combinado EP+NEP: {avg_comb:.1f}%
     (peso EP={peso_ep:.0%} · NEP={1-peso_ep:.0%})</p>

  <h2>1. Propiedades del NADES y Resultados Globales</h2>
  {_props_html}

  <h2>2. Perfil Fisicoquímico del NADES</h2>
  {_fig_prefix}
  {_fig_html_rad}
  <p class="fig-caption">Perfil normalizado (0–1) de las propiedades clave del NADES.
  Ref: Espino et al. (2016) Talanta 162, 412.</p>

  <h2>3. Índices EP · NEP · Combinado por Polifenol</h2>
  {_sim_html}
  {_fig2_prefix}
  {_fig_html_cmp}
  <p class="fig-caption">EP: Ruiz et al. (2024) Horticulturae 10, 458 · NEP: Ferrada (2026) novel · Score combinado: Ferrada (2026)</p>

  <h2>4. Efecto del % Agua en los Índices de Extracción</h2>
  {_fig3_prefix}
  {_fig_html_water}
  <p class="fig-caption">Curva calculada con ratio={ratio_sel}, T={temp_C}°C, UAE={freq_us} kHz.
  Ref: Dai et al. (2013) Anal. Chim. Acta 766, 61 · Chanioti &amp; Tzia (2017)</p>

  <h2>5. Contexto de la Planta</h2>
  <p><b>Fruto (baya) de <i>Berberis microphylla</i></b><br>
  Referencia principal: Ruiz et al. (2024) Horticulturae 10, 458</p>
  <p>Base de datos de polifenoles: {_tpc_ref}</p>

  <footer>
    Generado por: SimExtract — simulador de extracción de polifenoles — Beta 0.6<br>
    © 2026 Cristofher Ferrada — Pontificia Universidad Católica de Valparaíso (PUCV). Licenciado bajo Apache License 2.0. Ver LICENSE.<br>
    Modelos basados en literatura científica indexada (ver pestaña Metodología en la app)
  </footer>
</body>
</html>"""

        st.session_state["html_report"] = _html_report
        st.success(t("t1_report_ok"))

    if "html_report" in st.session_state:
        st.download_button(
            label=t("t1_report_dl"),
            data=st.session_state["html_report"].encode("utf-8"),
            file_name=f"Informe_NADES_{hba_sel.split('(')[0].strip()[:12]}_{hbd_sel[:12]}_fruto.html",
            mime="text/html",
        )


# ══════════════════════════════════════════════════════════
# TAB 2 — ANÁLISIS  (EP · NEP · Estabilidad · Interacción)
# ══════════════════════════════════════════════════════════
with tab2:
    atab_ep = seccion(t("atab_ep"))
    atab_nep = seccion(t("atab_nep"))
    atab_stab = seccion(t("atab_stab"))
    atab_int = seccion(t("atab_int"))
    atab_sens = seccion("sensibilidad")


# ══════════════════════════════════════════════════════════
# TAB 3 — PROCESO UAE · 3 PASOS
# ══════════════════════════════════════════════════════════
with tab3:
    st.markdown(t("t3_uae_title"))
    st.markdown(t("t3_uae_desc"))

    # ── Curva EP y NEP vs kHz ──
    st.markdown(t("t3_freq_h"))

    freq_range = list(range(0, 105, 5))
    poly_ep_rep = poly_df[(poly_df["tipo"] == "EP") & poly_df["is_major"]].iloc[0]
    poly_nep_rep = poly_df[(poly_df["tipo"] == "NEP")].iloc[0]

    # Curva base (sin US) para comparación
    ep_base_val = ep_extraction_score(props, poly_ep_rep)["total"] * 100
    nep_base_val = nep_extraction_score(props, poly_nep_rep)["total"] * 100

    curve_data = []
    for f in freq_range:
        us_ep = ultrasound_boost(f, poly_ep_rep, props)
        us_nep = ultrasound_boost(f, poly_nep_rep, props)
        ep_v = min(100.0, ep_base_val + us_ep["ep_boost"] * 100)
        nep_v = min(92.0, nep_base_val + us_nep["nep_boost"] * 100)
        ep_inc = round(min(100.0, ep_base_val + us_ep["ep_boost"] * 100) - ep_base_val, 1)
        nep_inc = round(min(92.0, nep_base_val + us_nep["nep_boost"] * 100) - nep_base_val, 1)
        curve_data.append(
            {
                "kHz": f,
                "EP total (%)": round(ep_v, 1),
                "NEP total (%)": round(nep_v, 1),
                "EP +%": ep_inc,
                "NEP +%": nep_inc,
                "Cavitación": round(us_ep["cavitation"] * 100, 1),
            }
        )
    curve_df = pd.DataFrame(curve_data)

    col_u1, col_u2 = st.columns(2)

    with col_u1:
        st.markdown(t("t3_total_khz"))
        fig_us_total = go.Figure()
        fig_us_total.add_hline(
            y=ep_base_val,
            line_dash="dot",
            line_color="#2e86ab",
            annotation_text=f"EP sin US: {ep_base_val:.1f}%",
            annotation_position="bottom right",
        )
        fig_us_total.add_hline(
            y=nep_base_val,
            line_dash="dot",
            line_color="#c44536",
            annotation_text=f"NEP sin US: {nep_base_val:.1f}%",
            annotation_position="top right",
        )
        fig_us_total.add_trace(
            go.Scatter(
                x=curve_df["kHz"],
                y=curve_df["EP total (%)"],
                name="EP con US",
                line=dict(color="#2e86ab", width=3),
                fill="tozeroy",
                fillcolor="rgba(46,134,171,0.10)",
            )
        )
        fig_us_total.add_trace(
            go.Scatter(
                x=curve_df["kHz"],
                y=curve_df["NEP total (%)"],
                name="NEP con US",
                line=dict(color="#c44536", width=3),
                fill="tozeroy",
                fillcolor="rgba(196,69,54,0.10)",
            )
        )
        if freq_us > 0:
            fig_us_total.add_vline(
                x=freq_us,
                line_dash="solid",
                line_color="#6b4226",
                annotation_text=f"Actual: {freq_us} kHz",
                annotation_position="top left",
            )
        fig_us_total.update_layout(
            height=360,
            xaxis_title="Frecuencia (kHz)",
            yaxis_title="Índice de extracción (%)",
            yaxis_range=[0, 100],
            legend=dict(orientation="h", y=-0.25),
        )
        st.plotly_chart(fig_us_total, use_container_width=True)
        fig_caption(
            3, "Índice total de extracción vs frecuencia UAE (kHz). Ref: Tiwari et al. (2010)."
        )

    with col_u2:
        st.markdown(t("t3_increment"))
        fig_us_boost = go.Figure()
        fig_us_boost.add_trace(
            go.Scatter(
                x=curve_df["kHz"],
                y=curve_df["EP +%"],
                name="Realce EP",
                line=dict(color="#2e86ab", width=3),
                fill="tozeroy",
                fillcolor="rgba(46,134,171,0.15)",
            )
        )
        fig_us_boost.add_trace(
            go.Scatter(
                x=curve_df["kHz"],
                y=curve_df["NEP +%"],
                name="Realce NEP",
                line=dict(color="#c44536", width=3),
                fill="tozeroy",
                fillcolor="rgba(196,69,54,0.15)",
            )
        )
        fig_us_boost.add_trace(
            go.Scatter(
                x=curve_df["kHz"],
                y=curve_df["Cavitación"] * 0.30,
                name="Intensidad cavitación (norm.)",
                line=dict(color="#f18f01", width=2, dash="dash"),
            )
        )
        if freq_us > 0:
            row_f = curve_df[curve_df["kHz"] == freq_us]
            if not row_f.empty:
                fig_us_boost.add_vline(
                    x=freq_us,
                    line_dash="solid",
                    line_color="#6b4226",
                    annotation_text=f"{freq_us} kHz",
                    annotation_position="top left",
                )
                ep_inc_now = row_f["EP +%"].values[0]
                nep_inc_now = row_f["NEP +%"].values[0]
                fig_us_boost.add_annotation(
                    x=freq_us,
                    y=max(ep_inc_now, nep_inc_now) + 1.5,
                    text=f"+EP {ep_inc_now}% / +NEP {nep_inc_now}%",
                    showarrow=False,
                    font=dict(size=11, color="#6b4226"),
                )
        fig_us_boost.update_layout(
            height=360,
            xaxis_title="Frecuencia (kHz)",
            yaxis_title="Incremento en extracción (%)",
            yaxis_range=[0, 32],
            legend=dict(orientation="h", y=-0.25),
        )
        st.plotly_chart(fig_us_boost, use_container_width=True)
        fig_caption(3, "Incremento en extracción (%) vs frecuencia UAE. Ref: Vilkhu et al. (2008).")

    st.caption(
        "Modelo UAE: Tiwari et al. (2010) Food Res. Int. 43, 1956 — cavitación acústica y extracción de polifenoles · "
        "Vilkhu et al. (2008) Innov. Food Sci. Emerg. 9, 161 — efecto frecuencia en transferencia de masa · "
        "Pico gaussiano a 22 kHz: Mason et al. (2011) Ultrason. Sonochem. 18, 847 · "
        "Modelo: Ferrada, C. Tesis Doctoral 2026"
    )

    # ── Tabla de referencia ──
    st.markdown("#### Tabla de referencia — Realce por frecuencia")
    ref_freqs = [0, 5, 10, 20, 25, 30, 40, 50, 60, 80, 100]
    ref_rows = curve_df[curve_df["kHz"].isin(ref_freqs)].copy()
    ref_rows["Régimen"] = ref_rows["kHz"].apply(
        lambda f: (
            "—"
            if f == 0
            else (
                "⚡ Máxima cavitación"
                if f <= 25
                else "✅ Alta" if f <= 40 else "🔵 Moderada" if f <= 60 else "🔹 Baja"
            )
        )
    )
    st.dataframe(
        ref_rows[
            ["kHz", "Régimen", "EP +%", "NEP +%", "EP total (%)", "NEP total (%)", "Cavitación"]
        ]
        .rename(columns={"Cavitación": "Cavitación (%)"})
        .style.background_gradient(subset=["EP +%", "NEP +%"], cmap="YlOrBr", vmin=0, vmax=20)
        .background_gradient(subset=["EP total (%)"], cmap="Blues", vmin=0, vmax=100)
        .background_gradient(subset=["NEP total (%)"], cmap="Reds", vmin=0, vmax=92)
        .format(
            {
                "EP +%": "+{:.1f}",
                "NEP +%": "+{:.1f}",
                "EP total (%)": "{:.1f}",
                "NEP total (%)": "{:.1f}",
                "Cavitación (%)": "{:.0f}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    # ── Todos los compuestos con US activo ──
    st.markdown("#### Efecto del ultrasonido por compuesto")
    st.caption(f"Configuración actual: NADES activo + {freq_us} kHz")

    us_detail = []
    for _, poly in poly_df.iterrows():
        us = ultrasound_boost(freq_us, poly, props)
        ep_b = round(us["ep_boost"] * 100, 1)
        nep_b = round(us["nep_boost"] * 100, 1)
        us_detail.append(
            {
                "Abrev": poly.get("abrev", poly["nombre"][:10]),
                "Clase": poly["clase"],
                "Tipo": poly["tipo"],
                "+EP (%)": ep_b,
                "+NEP (%)": nep_b,
                "Cavitación": round(us["cavitation"] * 100, 1),
            }
        )
    us_df = pd.DataFrame(us_detail)
    st.dataframe(
        us_df.style.background_gradient(subset=["+EP (%)"], cmap="Blues", vmin=0, vmax=20)
        .background_gradient(subset=["+NEP (%)"], cmap="Reds", vmin=0, vmax=30)
        .format({"+EP (%)": "+{:.1f}", "+NEP (%)": "+{:.1f}", "Cavitación": "{:.0f}%"}),
        use_container_width=True,
        hide_index=True,
        height=350,
    )

    st.markdown("---")
    st.markdown("#### Fundamento científico del modelo UAE")
    col_ua, col_ub = st.columns(2)
    with col_ua:
        st.markdown("""
        | Rango kHz | Régimen | Efecto principal |
        |---|---|---|
        | 0 kHz | Sin US | Extracción convencional |
        | 5–25 kHz | **Cavitación intensa** | Máxima ruptura de pared celular |
        | 25–40 kHz | Alta energía | Muy buena transferencia de masa |
        | 40–60 kHz | Moderado | Balance energía/estabilidad |
        | 60–100 kHz | Suave | Mínima degradación térmica |

        **Techo NEP con ultrasonido: 95%** (vs 85% convencional)
        El ultrasonido físicamente rompe algunos enlaces C–C interflavánicos
        que la química del NADES sola no puede hidrolizar.
        """)
    with col_ub:
        st.latex(r"I_{EP}^{US} = \min(1.0,\; I_{EP} + 0.18 \cdot C_{acust})")
        st.latex(r"I_{NEP}^{US} = \min(0.92,\; I_{NEP} + 0.28 \cdot C_{acust} \cdot f_{uni})")
        st.latex(r"C_{acust} = e^{-\frac{(f-22)^2}{2\sigma^2}},\quad f_{opt}=22\,\text{kHz}")
        st.markdown("donde **f_uni** = factor de sitios de unión del compuesto (PAC > flavonol)")

    # ════════════════════════════════════════════════════════
    # Sección 2: Proceso de 3 Pasos (Ferrada 2026)
    # ════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown(t("t3_3step"))
    st.markdown(
        f'<div class="novel-badge">'
        f"T={proc_temp}°C · t={proc_time} min · UAE={freq_us} kHz · "
        f"Paso 1: UAE+degradación · Paso 2: Centrifugación · Paso 3: Dilución+Filtración 0.22 μm"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.markdown("")

    with st.spinner("Calculando proceso de 3 pasos…"):
        df_3step = simulate_3step_process(
            props,
            poly_df,
            freq_us=freq_us,
            temp_C=proc_temp,
            time_min=proc_time,
            peso_ep=peso_ep,
        )

    if len(df_3step) > 0:
        avg_ep_3s = df_3step["EP final (%)"].mean()
        avg_nep_3s = df_3step["NEP final (%)"].mean()
        avg_deg_3s = df_3step["Degrad. T (%)"].mean()
        avg_comb_3s = df_3step["Combinado final (%)"].mean()

        ms1, ms2, ms3, ms4 = st.columns(4)
        ms1.metric(
            "EP final promedio",
            f"{avg_ep_3s:.1f}%",
            help="Tras los 3 pasos: UAE + centrifugación + filtración",
        )
        ms2.metric("NEP final promedio", f"{avg_nep_3s:.1f}%")
        ms3.metric(
            "Degrad. T promedio",
            f"{avg_deg_3s:.1f}%",
            help="Pérdida por temperatura (Arrhenius). NADES reduce un 25% vs EtOH.",
        )
        ms4.metric("EP+NEP combinado", f"{avg_comb_3s:.1f}%")

        col_3s1, col_3s2 = st.columns(2)
        with col_3s1:
            st.markdown("#### Pérdida por paso")
            avg_ep_p1 = df_3step["EP Paso1 (%)"].mean()
            avg_ep_p2 = df_3step["EP Paso2 (%)"].mean()
            avg_ep_p3 = df_3step["EP final (%)"].mean()
            avg_nep_p1 = df_3step["NEP Paso1 (%)"].mean()
            avg_nep_p2 = df_3step["NEP Paso2 (%)"].mean()
            avg_nep_p3 = df_3step["NEP final (%)"].mean()
            pasos_df = pd.DataFrame(
                {
                    "Paso": [
                        "Bruto (sin proc.)",
                        "Paso 1 (UAE+T)",
                        "Paso 2 (Centrf.)",
                        "Paso 3 (Filtrac.)",
                    ],
                    "EP (%)": [df_3step["EP bruto (%)"].mean(), avg_ep_p1, avg_ep_p2, avg_ep_p3],
                    "NEP (%)": [
                        df_3step["NEP bruto (%)"].mean(),
                        avg_nep_p1,
                        avg_nep_p2,
                        avg_nep_p3,
                    ],
                }
            )
            fig_pasos3 = go.Figure()
            fig_pasos3.add_trace(
                go.Scatter(
                    x=pasos_df["Paso"],
                    y=pasos_df["EP (%)"],
                    name="EP",
                    mode="lines+markers",
                    line=dict(color="#2e86ab", width=3),
                    marker=dict(size=10),
                )
            )
            fig_pasos3.add_trace(
                go.Scatter(
                    x=pasos_df["Paso"],
                    y=pasos_df["NEP (%)"],
                    name="NEP",
                    mode="lines+markers",
                    line=dict(color="#c44536", width=3),
                    marker=dict(size=10),
                )
            )
            fig_pasos3.update_layout(
                height=300,
                yaxis_range=[0, 105],
                yaxis_title="Rendimiento promedio (%)",
                legend=dict(orientation="h", y=-0.25),
            )
            st.plotly_chart(fig_pasos3, use_container_width=True)
            fig_caption(
                3,
                "Rendimiento EP+NEP por paso del proceso 3-etapas (UAE → centrifugación → filtración).",
            )

        with col_3s2:
            st.markdown("#### EP y NEP finales por compuesto")
            fig_3sc = go.Figure()
            ep_data = df_3step[df_3step["tipo"] == "EP"]
            nep_data = df_3step[df_3step["tipo"] == "NEP"]
            fig_3sc.add_trace(
                go.Bar(
                    x=ep_data["abrev"],
                    y=ep_data["EP final (%)"],
                    name="EP final",
                    marker_color="#2e86ab",
                )
            )
            fig_3sc.add_trace(
                go.Bar(
                    x=nep_data["abrev"],
                    y=nep_data["NEP final (%)"],
                    name="NEP final",
                    marker_color="#c44536",
                )
            )
            fig_3sc.update_layout(
                barmode="group",
                height=300,
                xaxis_tickangle=-40,
                yaxis_range=[0, 105],
                legend=dict(orientation="h", y=-0.35),
            )
            st.plotly_chart(fig_3sc, use_container_width=True)
            fig_caption(3, "EP y NEP finales por compuesto tras el proceso de 3 pasos.")

        st.markdown("#### Tabla detallada — 3 pasos por compuesto")
        st.dataframe(
            df_3step[
                [
                    "abrev",
                    "clase",
                    "tipo",
                    "EP bruto (%)",
                    "Degrad. T (%)",
                    "EP Paso1 (%)",
                    "EP Paso2 (%)",
                    "EP final (%)",
                    "NEP final (%)",
                    "Combinado final (%)",
                ]
            ]
            .style.background_gradient(subset=["EP final (%)"], cmap="Blues", vmin=0, vmax=100)
            .background_gradient(subset=["NEP final (%)"], cmap="Reds", vmin=0, vmax=100)
            .background_gradient(subset=["Degrad. T (%)"], cmap="Oranges", vmin=0, vmax=25)
            .background_gradient(subset=["Combinado final (%)"], cmap="YlOrBr", vmin=0, vmax=100)
            .format(
                {
                    c: "{:.1f}"
                    for c in [
                        "EP bruto (%)",
                        "Degrad. T (%)",
                        "EP Paso1 (%)",
                        "EP Paso2 (%)",
                        "EP final (%)",
                        "NEP final (%)",
                        "Combinado final (%)",
                    ]
                }
            ),
            use_container_width=True,
            hide_index=True,
            height=360,
        )
        st.caption(
            "Paso 1: UAE + degradación térmica por Arrhenius (factor protección NADES 0.75) · "
            "Paso 2: centrifugación 3000-4000 rpm, 10 min, 4°C → pérdida <4% (Saura-Calixto 2010) · "
            "Paso 3: dilución H₂O 1:2–1:5 + filtración 0.22 μm → sin pérdida para PM <2000 Da · "
            "Ref: Ferrada, C. Tesis Doctoral 2026 · Benvenutti et al. (2019) Food Res. Int. 119, 710"
        )

    # ════════════════════════════════════════════════════════
    # Sección 3: Degradación Térmica por Clase (Arrhenius)
    # ════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown(t("t3_arrhenius"))
    st.caption(
        f"Temperatura de proceso: **{proc_temp}°C** · Tiempo: **{proc_time} min** · "
        "Factor protección NADES: k × 0.75 (Chanioti & Tzia 2017)"
    )

    _clases_arr = [
        "Antocianina",
        "Flavonol",
        "Flavan-3-ol",
        "Ác. Hidroxicinámico",
        "Tanino Condensado",
        "Tanino Hidrolizable",
    ]
    arr_rows = []
    for _cl in _clases_arr:
        _r = thermal_degradation(proc_temp, proc_time, _cl)
        arr_rows.append(
            {
                "Clase": _cl,
                "k(T) (1/min)": _r["k_T"],
                "Degradación (%)": _r["degradacion_pct"],
                "Retención (%)": round(_r["retencion"] * 100, 2),
            }
        )
    arr_df = pd.DataFrame(arr_rows)

    col_arr1, col_arr2 = st.columns(2)
    with col_arr1:
        st.dataframe(
            arr_df.style.background_gradient(
                subset=["Degradación (%)"], cmap="Oranges", vmin=0, vmax=30
            )
            .background_gradient(subset=["Retención (%)"], cmap="Greens", vmin=70, vmax=100)
            .format(
                {"k(T) (1/min)": "{:.6f}", "Degradación (%)": "{:.2f}", "Retención (%)": "{:.2f}"}
            ),
            use_container_width=True,
            hide_index=True,
        )

    with col_arr2:
        fig_arr_bar = px.bar(
            arr_df,
            x="Clase",
            y="Retención (%)",
            color="Retención (%)",
            color_continuous_scale="RdYlGn",
            range_color=[70, 100],
        )
        fig_arr_bar.add_hline(
            y=90,
            line_dash="dot",
            line_color="#333",
            annotation_text="90% umbral (pérdida ≤10%)",
        )
        fig_arr_bar.update_layout(
            height=300,
            xaxis_tickangle=-25,
            showlegend=False,
            yaxis_range=[0, 101],
        )
        st.plotly_chart(fig_arr_bar, use_container_width=True)
        fig_caption(
            3, "Retención de polifenoles por clase (%) a T y tiempo del proceso. Modelo Arrhenius."
        )

    st.markdown("#### Curva retención vs temperatura por clase (tiempo fijo)")
    _t_sweep = range(20, 82, 2)
    arr_temp_rows = []
    for _t in _t_sweep:
        for _cl in _clases_arr:
            _r2 = thermal_degradation(_t, proc_time, _cl)
            arr_temp_rows.append(
                {"T (°C)": _t, "Clase": _cl, "Retención (%)": round(_r2["retencion"] * 100, 2)}
            )
    arr_temp_df = pd.DataFrame(arr_temp_rows)
    fig_arr_t = px.line(
        arr_temp_df,
        x="T (°C)",
        y="Retención (%)",
        color="Clase",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_arr_t.add_vline(
        x=proc_temp,
        line_dash="dot",
        line_color="#333",
        annotation_text=f"T={proc_temp}°C",
    )
    fig_arr_t.add_hline(
        y=90,
        line_dash="dash",
        line_color="#c44536",
        annotation_text="90% umbral",
    )
    fig_arr_t.update_layout(
        height=320,
        yaxis_range=[50, 101],
        legend=dict(orientation="h", y=-0.35),
    )
    st.plotly_chart(fig_arr_t, use_container_width=True)
    fig_caption(
        3,
        "Curva de retención vs temperatura (°C) por clase de polifenol. Modelo Arrhenius. Ref: Wang & Xu (2007).",
    )
    st.caption(
        "Arrhenius: k(T) = k_ref × exp(−Ea/R × (1/T_ref − 1/T)) · "
        "Ea (kJ/mol): Antocianinas 75 · Flavonoles 55 · Flavan-3-oles 60 · "
        "Ác. Hidroxicinámicos 50 · Taninos Condensados 45 · Taninos Hidrolizables 42 · "
        "Ref: Wang & Xu (2007) Food Chem. 101, 1338 · Fang (2011) Food Chem. 129, 267 · "
        "Chanioti & Tzia (2017) Food Bioprocess Technol. 10, 1999 · Ferrada, C. Tesis Doctoral 2026"
    )


# ── Sub-tab: Interacción NADES-Polifenol (dentro de tab2) ──
with atab_int:
    st.markdown(t("t2_int_title"))
    st.markdown(
        "Visualización de la compatibilidad fisicoquímica entre el NADES diseñado "
        "y cada polifenol del calafate. El NADES no solo **extrae** — también **protege** "
        "los grupos –OH de la oxidación formando una red supramolecular."
    )

    # ── Diagrama esquemático NADES-Polifenol ──
    st.markdown("#### Diagrama de Interacción NADES–Polifenol")
    st.markdown(
        "Representación esquemática de cómo el NADES rodea y protege la molécula del polifenol. "
        "Los grupos **–OH** del polifenol son cubiertos por los **HBD** del NADES mediante puentes de "
        "hidrógeno (líneas punteadas azules), y la red **HBA–HBD** forma una barrera que bloquea "
        "el acceso del **O₂** (símbolo ✕ gris)."
    )

    poly_sel_diagram = st.selectbox(
        "Seleccionar polifenol para el diagrama",
        options=poly_df["abrev"].tolist(),
        index=0,
        key="diag_poly_sel",
        help="El diagrama ajusta la cobertura de –OH según los grupos OH del compuesto seleccionado",
    )
    poly_diag = poly_df[poly_df["abrev"] == poly_sel_diagram].iloc[0]
    oh_total = max(1, int(poly_diag.get("oh_groups", 5)))
    cap_hbd_diag = props["cap_hbd"]
    oh_covered_int = min(oh_total, round(cap_hbd_diag))

    # Coordenadas del hexágono central (anillo aromático)
    _ring_r = 1.0
    _hex_angles = [np.pi / 2 + i * 2 * np.pi / 6 for i in range(6)]
    _hex_x = [_ring_r * np.cos(a) for a in _hex_angles] + [_ring_r * np.cos(_hex_angles[0])]
    _hex_y = [_ring_r * np.sin(a) for a in _hex_angles] + [_ring_r * np.sin(_hex_angles[0])]

    # Grupos –OH alrededor del anillo (radio 1.75)
    _oh_r = 1.78
    _oh_ang = [2 * np.pi * i / oh_total + np.pi / 2 for i in range(oh_total)]
    _oh_x = [_oh_r * np.cos(a) for a in _oh_ang]
    _oh_y = [_oh_r * np.sin(a) for a in _oh_ang]

    # Moléculas HBD (radio 2.65) — una por OH cubierto (máx 6)
    _hbd_r = 2.65
    _n_hbd = min(oh_covered_int, 6)
    _hbd_x = [_hbd_r * np.cos(_oh_ang[i]) for i in range(_n_hbd)]
    _hbd_y = [_hbd_r * np.sin(_oh_ang[i]) for i in range(_n_hbd)]

    # Moléculas HBA (radio 3.6) — distribuidas uniformemente
    _hba_r = 3.6
    _n_hba = min(4, max(2, _n_hbd))
    _hba_ang = [np.pi / 2 + i * 2 * np.pi / _n_hba for i in range(_n_hba)]
    _hba_x = [_hba_r * np.cos(a) for a in _hba_ang]
    _hba_y = [_hba_r * np.sin(a) for a in _hba_ang]

    # Moléculas H₂O (radio 4.4)
    _w_r = 4.45
    _w_ang = [i * 2 * np.pi / 6 + np.pi / 6 for i in range(6)]
    _w_x = [_w_r * np.cos(a) for a in _w_ang]
    _w_y = [_w_r * np.sin(a) for a in _w_ang]

    # Moléculas O₂ bloqueadas (radio 5.3)
    _o2_r = 5.3
    _o2_ang = [i * 2 * np.pi / 8 for i in range(8)]
    _o2_x = [_o2_r * np.cos(a) for a in _o2_ang]
    _o2_y = [_o2_r * np.sin(a) for a in _o2_ang]

    fig_diag = go.Figure()

    # Anillo hexagonal (polifenol)
    fig_diag.add_trace(
        go.Scatter(
            x=_hex_x,
            y=_hex_y,
            mode="lines",
            line=dict(color="#5a2d8a", width=3),
            fill="toself",
            fillcolor="rgba(90,45,138,0.10)",
            name="Anillo aromático",
        )
    )
    fig_diag.add_annotation(
        x=0,
        y=0,
        text=f"<b>{poly_sel_diagram[:8]}</b>",
        showarrow=False,
        font=dict(size=9, color="#5a2d8a"),
    )

    # Líneas H-bond: OH → HBD (azul punteado)
    for i in range(_n_hbd):
        fig_diag.add_shape(
            type="line",
            x0=_oh_x[i],
            y0=_oh_y[i],
            x1=_hbd_x[i],
            y1=_hbd_y[i],
            line=dict(color="#2e86ab", width=1.5, dash="dot"),
        )
    # Líneas H-bond: HBD → HBA (naranja punteado)
    for i in range(_n_hbd):
        j = i % _n_hba
        fig_diag.add_shape(
            type="line",
            x0=_hbd_x[i],
            y0=_hbd_y[i],
            x1=_hba_x[j],
            y1=_hba_y[j],
            line=dict(color="#f18f01", width=1.2, dash="dot"),
        )

    # Grupos –OH cubiertos (verde)
    if oh_covered_int > 0:
        fig_diag.add_trace(
            go.Scatter(
                x=_oh_x[:oh_covered_int],
                y=_oh_y[:oh_covered_int],
                mode="markers+text",
                marker=dict(
                    size=20, color="#1a8a40", symbol="circle", line=dict(color="white", width=1.5)
                ),
                text=["–OH"] * oh_covered_int,
                textfont=dict(size=7, color="white"),
                textposition="middle center",
                name=f"–OH cubiertos ({oh_covered_int})",
            )
        )

    # Grupos –OH libres (rojo)
    _n_free = oh_total - oh_covered_int
    if _n_free > 0:
        fig_diag.add_trace(
            go.Scatter(
                x=_oh_x[oh_covered_int:],
                y=_oh_y[oh_covered_int:],
                mode="markers+text",
                marker=dict(
                    size=20, color="#c44536", symbol="circle", line=dict(color="white", width=1.5)
                ),
                text=["–OH"] * _n_free,
                textfont=dict(size=7, color="white"),
                textposition="middle center",
                name=f"–OH libres ({_n_free}, expuesto)",
            )
        )

    # Moléculas HBD
    if _n_hbd > 0:
        _hbd_lbl = hbd_sel.split()[0][:10]
        fig_diag.add_trace(
            go.Scatter(
                x=_hbd_x,
                y=_hbd_y,
                mode="markers+text",
                marker=dict(
                    size=24, color="#2e86ab", symbol="circle", line=dict(color="white", width=1.5)
                ),
                text=["HBD"] * _n_hbd,
                textfont=dict(size=8, color="white"),
                textposition="middle center",
                name=f"HBD ({_hbd_lbl})",
            )
        )

    # Moléculas HBA
    _hba_lbl = hba_sel.split("(")[0].strip()[:10]
    fig_diag.add_trace(
        go.Scatter(
            x=_hba_x,
            y=_hba_y,
            mode="markers+text",
            marker=dict(
                size=24, color="#f18f01", symbol="diamond", line=dict(color="white", width=1.5)
            ),
            text=["HBA"] * _n_hba,
            textfont=dict(size=8, color="white"),
            textposition="middle center",
            name=f"HBA ({_hba_lbl})",
        )
    )

    # Moléculas H₂O
    fig_diag.add_trace(
        go.Scatter(
            x=_w_x,
            y=_w_y,
            mode="markers+text",
            marker=dict(
                size=16, color="#87CEEB", symbol="circle", line=dict(color="#1a6fa0", width=1)
            ),
            text=["H₂O"] * 6,
            textfont=dict(size=7, color="#0d1f35"),
            textposition="middle center",
            name="H₂O (capa de hidratación)",
        )
    )

    # Moléculas O₂ bloqueadas
    fig_diag.add_trace(
        go.Scatter(
            x=_o2_x,
            y=_o2_y,
            mode="markers+text",
            marker=dict(size=14, color="#cccccc", symbol="x", line=dict(color="#888888", width=2)),
            text=["O₂"] * 8,
            textfont=dict(size=7, color="#666666"),
            textposition="top center",
            name="O₂ (bloqueado por la red DES)",
        )
    )

    _cov_pct = round(oh_covered_int / oh_total * 100)
    fig_diag.add_annotation(
        x=0,
        y=-6.2,
        text=(
            f"<b>NADES activo:</b> {hba_sel.split('(')[0].strip()} : {hbd_sel} "
            f"({ratio_sel}, {water_pct}% H₂O) · "
            f"<b>Cobertura –OH:</b> {oh_covered_int}/{oh_total} = {_cov_pct}% · "
            f"Cap. HBD: {cap_hbd_diag:.1f}"
        ),
        showarrow=False,
        font=dict(size=10, color="#0d1f35"),
        xanchor="center",
    )

    fig_diag.update_layout(
        height=560,
        xaxis=dict(range=[-6.3, 6.3], visible=False, scaleanchor="y"),
        yaxis=dict(range=[-7.0, 6.3], visible=False),
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(
            orientation="h",
            y=-0.12,
            x=0.5,
            xanchor="center",
            font_size=10,
            bgcolor="rgba(255,255,255,0.8)",
        ),
        margin=dict(l=10, r=10, t=30, b=120),
        title=dict(
            text=f"Red supramolecular NADES ↔ {poly_sel_diagram}",
            font=dict(size=13, color="#0d1f35"),
            x=0.5,
        ),
    )
    st.plotly_chart(fig_diag, use_container_width=True)
    fig_caption(
        2,
        "Diagrama esquemático de interacción NADES–polifenol (red de H-bonds). Modelo conceptual.",
    )
    st.caption(
        "Diagrama esquemático conceptual — no es una estructura molecular a escala. "
        "🟢 –OH cubiertos = protegidos por puentes H del HBD · "
        "🔴 –OH libres = expuestos a oxidación · "
        "🔵 HBD = donador H-bond · 🟠 HBA = aceptor H-bond (red externa) · "
        "🩵 H₂O = capa de hidratación · ✕ O₂ = bloqueado por la red supramolecular DES · "
        "Ref: Dai & Verpoorte (2014) Anal. Chim. Acta 766, 61 · "
        "Benvenutti et al. (2019) Food Res. Int. 119, 710 · "
        "Modelo visual: Cristofher Ferrada, Tesis Doctoral 2026"
    )
    st.markdown("---")

    # ── Heatmap de compatibilidad ──
    st.markdown("#### Mapa de compatibilidad NADES × Polifenol")
    st.caption(
        "Cada celda muestra qué tan bien encaja el NADES con cada compuesto en ese factor (0-100%)"
    )

    # Usar poly_df directamente (sim_display no contiene las columnas del polifenol)
    poly_interact = poly_df[poly_df["is_major"]] if solo_principales else poly_df
    compat_rows = []
    for _, poly in poly_interact.iterrows():
        ep_r = ep_extraction_score(props, poly)
        nep_r = nep_extraction_score(props, poly)
        st_r = stability_score(props, poly, temp_C)
        compat_rows.append(
            {
                "Compuesto": poly["abrev"],
                "Tipo": poly["tipo"],
                "Polaridad": round(ep_r["Polaridad"] * 100),
                "pH": round(ep_r["pH"] * 100),
                "HBD (extrac.)": round(ep_r["Cap. HBD"] * 100),
                "Prot.OH": round(st_r["Protección OH"] * 100),
                "Antioxid.": round(st_r["Antioxidante NADES"] * 100),
                "Barrera O₂": round(st_r["Barrera O₂"] * 100),
            }
        )
    compat_df = pd.DataFrame(compat_rows)

    hm_cols = ["Polaridad", "pH", "HBD (extrac.)", "Prot.OH", "Antioxid.", "Barrera O₂"]
    hm_data = compat_df.set_index("Compuesto")[hm_cols].T

    fig_hm = go.Figure(
        go.Heatmap(
            z=hm_data.values,
            x=hm_data.columns.tolist(),
            y=hm_data.index.tolist(),
            colorscale="RdYlGn",
            zmin=0,
            zmax=100,
            text=[[f"{v:.0f}%" for v in row] for row in hm_data.values],
            texttemplate="%{text}",
            textfont={"size": 9},
            colorbar=dict(title="Score %"),
        )
    )
    fig_hm.update_layout(
        height=300,
        xaxis=dict(tickangle=-40, tickfont=dict(size=9)),
        yaxis=dict(tickfont=dict(size=10)),
        margin=dict(l=120, r=20, t=20, b=100),
    )
    st.plotly_chart(fig_hm, use_container_width=True)
    fig_caption(
        2,
        "Heatmap de compatibilidad NADES–polifenol por factores (polaridad, pH, HBD). Ref: Dai & Verpoorte (2014).",
    )
    st.caption(
        "Ref: Dai & Verpoorte (2014) Anal. Chim. Acta 766, 61 — factores de compatibilidad NADES-polifenol · "
        "Espino et al. (2016) Talanta 162, 412 — modelo de polaridad y HBD para extracción fenólica"
    )

    # ── H-bond coverage ──
    st.markdown("#### Cobertura de grupos –OH por el NADES")
    st.caption(
        f"Cap. HBD efectiva del NADES: **{props['cap_hbd']:.1f}** · "
        f"Un NADES cubre los OH del compuesto cuando cap_HBD ≥ oh_groups"
    )

    hb_rows = []
    for _, poly in poly_df.iterrows():
        oh = poly.get("oh_groups", 5)
        covered = min(oh, props["cap_hbd"])
        pct = round(covered / oh * 100, 1)
        hb_rows.append(
            {
                "Compuesto": poly.get("abrev", poly["nombre"][:10]),
                "OH totales": oh,
                "OH cubiertos": round(covered, 1),
                "OH libres (riesgo)": round(oh - covered, 1),
                "Cobertura (%)": pct,
                "Tipo": poly["tipo"],
            }
        )
    hb_df = pd.DataFrame(hb_rows).sort_values("Cobertura (%)", ascending=True)

    fig_hb = go.Figure()
    fig_hb.add_trace(
        go.Bar(
            name="OH cubiertos",
            y=hb_df["Compuesto"],
            x=hb_df["OH cubiertos"],
            orientation="h",
            marker_color="#048a81",
        )
    )
    fig_hb.add_trace(
        go.Bar(
            name="OH libres (riesgo oxidación)",
            y=hb_df["Compuesto"],
            x=hb_df["OH libres (riesgo)"],
            orientation="h",
            marker_color="#c44536",
        )
    )
    fig_hb.update_layout(
        barmode="stack",
        height=max(350, len(hb_df) * 22),
        xaxis_title="Grupos –OH",
        legend=dict(orientation="h", y=-0.15),
        margin=dict(l=100),
    )
    st.plotly_chart(fig_hb, use_container_width=True)
    fig_caption(
        2,
        "Cobertura de grupos –OH por el NADES: OH cubiertos vs OH libres por compuesto. Ref: Benvenutti et al. (2019).",
    )
    st.caption(
        "🟢 Verde = OH protegidos por H-bonds del NADES (no accesibles al O₂) · "
        "🔴 Rojo = OH aún expuestos (riesgo de oxidación) · "
        "Ref: Benvenutti et al. (2019) Food Res. Int. 119, 710 — protección de grupos fenólicos por DES · "
        "Dai & Verpoorte (2014) Anal. Chim. Acta 766, 61 — capacidad HBD del solvente DES"
    )

    # ── Scatter: compatibilidad EP vs Estabilidad ──
    st.markdown("#### Mapa EP vs Estabilidad — ¿Extrae bien Y protege bien?")
    scatter_data = []
    for _, poly in poly_df.iterrows():
        ep_v = ep_extraction_score(props, poly)["total"] * 100
        st_v = stability_score(props, poly, temp_C)["total"] * 100
        nep_v = nep_extraction_score(props, poly)["total"] * 100
        scatter_data.append(
            {
                "Compuesto": poly.get("abrev", poly["nombre"][:10]),
                "EP (%)": round(ep_v, 1),
                "Estab. (%)": round(st_v, 1),
                "NEP (%)": round(nep_v, 1),
                "Clase": poly["clase"],
                "Tipo": poly["tipo"],
                "OH": poly.get("oh_groups", 5),
            }
        )
    sc_df = pd.DataFrame(scatter_data)
    fig_sc = px.scatter(
        sc_df,
        x="EP (%)",
        y="Estab. (%)",
        color="Clase",
        size="OH",
        symbol="Tipo",
        hover_data=["Compuesto", "NEP (%)", "OH"],
        color_discrete_sequence=px.colors.qualitative.Set2,
        labels={"EP (%)": "Índice EP (%)", "Estab. (%)": "Índice Estabilidad (%)"},
    )
    fig_sc.add_vrect(
        x0=70, x1=100, fillcolor="blue", opacity=0.04, annotation_text="Alta extracción"
    )
    fig_sc.add_hrect(
        y0=75, y1=100, fillcolor="green", opacity=0.04, annotation_text="Alta estabilidad"
    )
    fig_sc.update_layout(height=400, legend=dict(orientation="h", y=-0.25, font_size=10))
    st.plotly_chart(fig_sc, use_container_width=True)
    st.caption(
        "Zona ideal: esquina superior derecha (alta extracción + alta estabilidad). "
        "Tamaño del punto = número de grupos –OH. Símbolo = EP (círculo) o NEP (estrella). "
        "Ref EP: Ruiz et al. (2024) Horticulturae 10, 458 · "
        "Ref estabilidad: Benvenutti et al. (2019) Food Res. Int. 119, 710 · "
        "Modelo NEP: Ferrada, C. Tesis Doctoral 2026"
    )


# ── Sub-tab: Extracción EP (dentro de tab2) ──
with atab_ep:
    st.markdown(t("t2_ep_title"))
    st.caption(
        "Compuestos identificados por HPLC-DAD-ESI-MS/MS · "
        "Ruiz et al. (2024) Horticulturae 10, 458, Tabla 2"
    )

    poly_ep_base = poly_df[poly_df["tipo"] == "EP"]
    if solo_principales:
        poly_ep_base = poly_ep_base[poly_ep_base["is_major"]]

    ep_detail = []
    for _, poly in poly_ep_base.iterrows():
        r = ep_extraction_score(props, poly)
        ep_detail.append(
            {
                "Polifenol": poly["nombre"],
                "Abrev": poly["abrev"],
                "Clase": poly["clase"],
                "Conc. rel.": round(poly.get("concentracion_rel", 0), 2),
                "Principal": "✓" if poly.get("is_major", False) else "",
                "Total EP (%)": round(r["total"] * 100, 1),
                "Polaridad": round(r["Polaridad"] * 100, 1),
                "pH": round(r["pH"] * 100, 1),
                "Cap. HBD": round(r["Cap. HBD"] * 100, 1),
                "Viscosidad": round(r["Viscosidad"] * 100, 1),
                "Bonus Agua": round(r["Bonus Agua"] * 100, 1),
            }
        )
    ep_det_df = pd.DataFrame(ep_detail).sort_values("Total EP (%)", ascending=False)

    # ── Filtro por clase ──
    clases_ep = [t("filter_all")] + sorted(poly_ep_base["clase"].unique().tolist())
    clase_sel = st.selectbox(t("t2_ep_filter"), clases_ep, key="ep_clase")
    if clase_sel != t("filter_all"):
        ep_det_df = ep_det_df[ep_det_df["Clase"] == clase_sel]

    col_ep1, col_ep2 = st.columns([2, 3])

    with col_ep1:
        st.markdown(t("t2_ep_ranking"))
        st.dataframe(
            ep_det_df[["Abrev", "Clase", "Conc. rel.", "Principal", "Total EP (%)"]]
            .style.background_gradient(subset=["Total EP (%)"], cmap="Blues", vmin=0, vmax=100)
            .background_gradient(subset=["Conc. rel."], cmap="Purples", vmin=0, vmax=1)
            .format({"Total EP (%)": "{:.1f}", "Conc. rel.": "{:.2f}"}),
            use_container_width=True,
            hide_index=True,
            height=420,
        )

    with col_ep2:
        st.markdown(t("t2_ep_factors"))
        factores = ["Polaridad", "pH", "Cap. HBD", "Viscosidad", "Bonus Agua"]
        fig_ep_stack = go.Figure()
        colors_f = ["#2e86ab", "#f18f01", "#048a81", "#a23b72", "#c44536"]
        for i, f in enumerate(factores):
            fig_ep_stack.add_trace(
                go.Bar(
                    name=f,
                    x=ep_det_df["Abrev"],
                    y=ep_det_df[f],
                    marker_color=colors_f[i],
                )
            )
        fig_ep_stack.update_layout(
            barmode="stack",
            height=420,
            xaxis_tickangle=-40,
            yaxis_title="Contribución al índice (%)",
            legend=dict(orientation="h", y=-0.45, font_size=10),
        )
        st.plotly_chart(fig_ep_stack, use_container_width=True)
        st.caption(
            "Ref: Espino et al. (2016) Talanta 162, 412 — pesos de factores polaridad, pH y HBD en extracción fenólica con DES · "
            "Chanioti & Tzia (2017) — bonus agua a ~25% H₂O"
        )

    # ── EP por clase (box plot) ──
    st.markdown("#### Distribución de EP por clase de polifenol")
    all_ep_detail = []
    for _, poly in poly_df[poly_df["tipo"] == "EP"].iterrows():
        r = ep_extraction_score(props, poly)
        all_ep_detail.append({"Clase": poly["clase"], "EP (%)": round(r["total"] * 100, 1)})
    all_ep_df = pd.DataFrame(all_ep_detail)
    fig_ep_box = px.box(
        all_ep_df,
        x="Clase",
        y="EP (%)",
        color="Clase",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_ep_box.update_layout(height=320, showlegend=False, xaxis_tickangle=-15)
    st.plotly_chart(fig_ep_box, use_container_width=True)
    st.caption(
        "Distribución del índice EP por clase de polifenol. "
        "Ref: Ruiz et al. (2024) Horticulturae 10, 458 — identificación de 28 compuestos EP en calafate · "
        "Castro-López et al. (2016) J. Funct. Foods 24, 455 — perfil polifenólico de Berberis microphylla"
    )

    # Efecto de pH en antocianinas
    st.markdown("#### Efecto del pH en la extracción de antocianinas")
    st.caption("Varía el pH cambiando el HBD o el % de agua en el sidebar")

    ph_range = np.arange(1.0, 8.5, 0.2)
    ph_data = []
    antos = poly_df[(poly_df["tipo"] == "EP") & (poly_df["clase"] == "Antocianina")]
    for ph_val in ph_range:
        fake_props = {**props, "pH": ph_val}
        for _, poly in antos.iterrows():
            r = ep_extraction_score(fake_props, poly)
            ph_data.append({"pH": ph_val, "Abrev": poly["abrev"], "EP (%)": r["total"] * 100})
    ph_df = pd.DataFrame(ph_data)
    fig_ph = px.line(
        ph_df,
        x="pH",
        y="EP (%)",
        color="Abrev",
        color_discrete_sequence=px.colors.qualitative.Vivid,
    )
    fig_ph.add_vline(
        x=props["pH"],
        line_dash="dot",
        line_color="#333",
        annotation_text=f"pH actual: {props['pH']:.2f}",
    )
    fig_ph.update_layout(
        height=320, yaxis_range=[0, 100], legend=dict(orientation="h", y=-0.40, font_size=9)
    )
    st.plotly_chart(fig_ph, use_container_width=True)
    st.caption(
        "Estabilidad de antocianinas altamente dependiente del pH: máxima en pH < 3 (forma flavilio) · "
        "Ref: Torskangerpoll & Andersen (2005) Food Chem. 89, 427 — equilibrio estructural de antocianinas vs pH · "
        "Ruiz et al. (2024) Horticulturae 10, 458 — antocianinas principales en calafate"
    )


# ── Sub-tab: Extracción NEP (dentro de tab2) ──
with atab_nep:
    st.markdown(t("t2_nep_title"))
    _nep_badge = (
        "⚠️ Modelo teórico original · Sin literatura previa para "
        "<em>Berberis microphylla</em> + NADES · Contribución novel de la tesis"
    )
    st.markdown(
        f'<div class="novel-badge">{_nep_badge}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("")

    nep_detail = []
    for _, poly in poly_df[poly_df["tipo"] == "NEP"].iterrows():
        r = nep_extraction_score(props, poly)
        nep_detail.append(
            {
                "Polifenol": poly["nombre"],
                "Clase": poly["clase"],
                "Total NEP (%)": round(r["total"] * 100, 1),
                "CWP (Penetración)": round(r["CWP (Penetración)"] * 100, 1),
                "HBD (Disrupción)": round(r["HBD (Disrupción)"] * 100, 1),
                "HP (Hidrólisis)": round(r["HP (Hidrólisis)"] * 100, 1),
                "MS (Hinchamiento)": round(r["MS (Hinchamiento)"] * 100, 1),
                "SP (Solubilización)": round(r["SP (Solubilización)"] * 100, 1),
            }
        )
    nep_det_df = pd.DataFrame(nep_detail).sort_values("Total NEP (%)", ascending=False)

    col_n1, col_n2 = st.columns([2, 3])

    with col_n1:
        st.markdown("#### Ranking NEP")
        st.dataframe(
            nep_det_df[["Polifenol", "Clase", "Total NEP (%)"]]
            .style.background_gradient(subset=["Total NEP (%)"], cmap="Reds", vmin=0, vmax=80)
            .format({"Total NEP (%)": "{:.1f}"}),
            use_container_width=True,
            hide_index=True,
        )
        st.markdown("---")
        st.markdown("##### ¿Por qué techo al 85% (convencional) / 95% (con UAE)?")
        st.markdown(
            "Incluso el NADES ideal no puede liberar el 100% de los NEP: "
            "parte de los taninos condensados tienen enlaces C–C interflavánicos "
            "que no son hidrolizables sin UAE ni hidrólisis alcalina. "
            "El UAE (20-25 kHz) rompe físicamente algunos de estos enlaces mediante cavitación "
            "acústica, elevando el techo práctico al 95%. "
            "Ref: Tiwari et al. (2010) Food Res. Int. 43, 1956."
        )

    with col_n2:
        st.markdown("#### Desglose mecanístico de factores NEP")
        factores_nep = [
            "CWP (Penetración)",
            "HBD (Disrupción)",
            "HP (Hidrólisis)",
            "MS (Hinchamiento)",
            "SP (Solubilización)",
        ]
        colors_nep = ["#c44536", "#a23b72", "#f18f01", "#2e86ab", "#048a81"]
        fig_nep_stack = go.Figure()
        for i, f in enumerate(factores_nep):
            fig_nep_stack.add_trace(
                go.Bar(
                    name=f,
                    x=nep_det_df["Polifenol"],
                    y=nep_det_df[f],
                    marker_color=colors_nep[i],
                )
            )
        fig_nep_stack.update_layout(
            barmode="stack",
            height=340,
            xaxis_tickangle=-20,
            yaxis_title="Contribución al índice (%)",
            legend=dict(orientation="h", y=-0.45, font_size=9),
        )
        st.plotly_chart(fig_nep_stack, use_container_width=True)
        st.caption(
            "Modelo mecanístico novel para NEP de Berberis microphylla con NADES — sin precedente en literatura · "
            "Factores extrapolados de: Saura-Calixto et al. (2010) J. Agric. Food Chem. 58, 11932 (fracción NEP) · "
            "Benvenutti et al. (2019) Food Res. Int. 119, 710 (penetración NADES en matriz) · "
            "Ferrada, C. Tesis Doctoral 2026 (modelo teórico original)"
        )

    # ── Monte Carlo — Incertidumbre del modelo NEP ──
    st.markdown("---")
    with st.expander(
        "🎲 Análisis de Incertidumbre — Monte Carlo (±20% en parámetros NADES)", expanded=False
    ):
        st.markdown(
            "Perturba aleatoriamente los parámetros del NADES (cap_HBD, cap_HBA, pH, viscosidad, "
            "polaridad, antioxidante) en ±20% y calcula cómo varía el índice NEP. "
            "Permite estimar la **robustez del modelo** ante incertidumbre en las propiedades del NADES."
        )
        if st.button("▶ Ejecutar Monte Carlo (400 iteraciones)", key="mc_run"):
            with st.spinner("Simulando 400 perturbaciones del NADES…"):
                mc = nep_monte_carlo(props, poly_df, n_iter=400, uncertainty=0.20)
            st.session_state["mc_result"] = mc

        if "mc_result" in st.session_state:
            mc = st.session_state["mc_result"]
            if mc["samples"]:
                mc1, mc2, mc3, mc4 = st.columns(4)
                mc1.metric("NEP promedio", f"{mc['mean']:.1f}%")
                mc2.metric("Desv. estándar", f"±{mc['std']:.1f}%")
                mc3.metric("IC 90%", f"[{mc['p5']:.1f}–{mc['p95']:.1f}]%")
                mc4.metric("CV (%)", f"{mc['cv']:.1f}%")

                fig_mc = go.Figure()
                fig_mc.add_trace(
                    go.Histogram(
                        x=mc["samples"],
                        nbinsx=30,
                        marker_color="#c44536",
                        opacity=0.75,
                        name="Distribución NEP (%)",
                    )
                )
                fig_mc.add_vline(
                    x=mc["mean"],
                    line_dash="solid",
                    line_color="#333",
                    annotation_text=f"Media: {mc['mean']:.1f}%",
                )
                fig_mc.add_vrect(
                    x0=mc["p5"],
                    x1=mc["p95"],
                    fillcolor="rgba(196,69,54,0.12)",
                    annotation_text="IC 90%",
                    annotation_position="top left",
                )
                fig_mc.update_layout(
                    height=300,
                    xaxis_title="Índice NEP (%)",
                    yaxis_title="Frecuencia",
                    showlegend=False,
                )
                st.plotly_chart(fig_mc, use_container_width=True)
                st.caption(
                    "N = 400 iteraciones · Perturbación: ±20% en cap_HBD, cap_HBA, pH, viscosidad, polaridad, antioxidante · "
                    "Semilla aleatoria fija (reproducible) · "
                    "Ref: Saltelli et al. (2004) Sensitivity Analysis in Practice · "
                    "Modelo NEP: Ferrada, C. Tesis Doctoral 2026"
                )
            else:
                st.info(
                    "No hay compuestos NEP en la base de datos activa para esta parte de la planta."
                )

    # Curva de respuesta: pH vs NEP (hidrólisis)
    st.markdown("#### Efecto del pH en la liberación de taninos")
    ph_nep_data = []
    for ph_val in np.arange(1.0, 8.0, 0.2):
        fake = {**props, "pH": ph_val}
        for _, poly in poly_df[poly_df["tipo"] == "NEP"].iterrows():
            r = nep_extraction_score(fake, poly)
            ph_nep_data.append(
                {"pH": ph_val, "Polifenol": poly["nombre"], "NEP (%)": r["total"] * 100}
            )
    ph_nep_df = pd.DataFrame(ph_nep_data)
    fig_phnep = px.line(
        ph_nep_df,
        x="pH",
        y="NEP (%)",
        color="Polifenol",
        color_discrete_sequence=["#8B0000", "#DC143C", "#FF4500", "#FF6347"],
    )
    fig_phnep.add_vline(
        x=props["pH"],
        line_dash="dot",
        line_color="#333",
        annotation_text=f"pH actual: {props['pH']:.2f}",
    )
    fig_phnep.update_layout(height=300, yaxis_range=[0, 80], legend=dict(orientation="h", y=-0.35))
    st.plotly_chart(fig_phnep, use_container_width=True)
    st.caption(
        "Hidrólisis ácida de taninos hidrolizables (ésteres de ác. gálico/elágico) favorecida a pH < 3 · "
        "Ref: Saura-Calixto et al. (2010) J. Agric. Food Chem. 58, 11932 (fracción NEP y extracción ácida) · "
        "Modelo pH-hidrólisis: Ferrada, C. Tesis Doctoral 2026"
    )

    # Curva agua vs NEP
    st.markdown("#### Efecto del % de agua en la extracción NEP (hinchamiento de matriz)")
    wa_nep = []
    for w in range(0, 55, 5):
        pw = calculate_nades_properties(
            hba_sel,
            hbd_sel,
            ratio_hba,
            ratio_hbd,
            w,
            temp_C,
            HBA_COMPONENTS,
            HBD_COMPONENTS,
        )
        for _, poly in poly_df[poly_df["tipo"] == "NEP"].iterrows():
            r = nep_extraction_score(pw, poly)
            wa_nep.append({"Agua (%)": w, "Polifenol": poly["nombre"], "NEP (%)": r["total"] * 100})
    wa_nep_df = pd.DataFrame(wa_nep)
    fig_wa_nep = px.line(
        wa_nep_df,
        x="Agua (%)",
        y="NEP (%)",
        color="Polifenol",
        color_discrete_sequence=["#8B0000", "#DC143C", "#FF4500", "#FF6347"],
    )
    fig_wa_nep.add_vline(
        x=water_pct, line_dash="dot", line_color="#333", annotation_text=f"Actual: {water_pct}%"
    )
    fig_wa_nep.update_layout(height=280, yaxis_range=[0, 80], legend=dict(orientation="h", y=-0.35))
    st.plotly_chart(fig_wa_nep, use_container_width=True)
    st.caption(
        "El agua facilita el hinchamiento (swelling) de la matriz celular permitiendo mejor acceso del NADES a los NEP · "
        "Ref: Benvenutti et al. (2019) Food Res. Int. 119, 710 — efecto H₂O en penetración DES · "
        "Modelo hinchamiento: Ferrada, C. Tesis Doctoral 2026"
    )

    st.markdown("---")
    st.markdown("#### ⚗️ Protocolo NADES: de 8 pasos a 3 pasos")
    st.markdown(
        '<div class="novel-badge">Modelo teórico novel · <em>Berberis microphylla</em> + NADES sin precedente en literatura · '
        "Cristofher Ferrada, Tesis Doctoral 2026</div>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Ref. protocolo convencional: Saura-Calixto et al. (2010) J. Agric. Food Chem. 58, 11932 · "
        "Protocolo NADES extrapolado de: Benvenutti et al. (2019) Food Res. Int. 119, 710"
    )
    st.markdown("")

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown(
            '<div style="border:2px solid #c44536;border-radius:8px;padding:1rem;background:#fff5f5">'
            '<b style="color:#c44536;font-size:1.05rem">❌ Método Convencional — 8 Pasos</b><br><br>'
            '<b style="color:#6b0000">1.</b> Pesar muestra liofilizada (100 mg)<br>'
            '<b style="color:#6b0000">2.</b> Extracción EP: EtOH 70%, 60 min agitación<br>'
            '<b style="color:#6b0000">3.</b> Centrifugar 5000 rpm × 15 min<br>'
            '<b style="color:#6b0000">4.</b> Filtrar residuo (papel filtro)<br>'
            '<b style="color:#6b0000">5.</b> Evaporar EtOH (rotavapor, 40°C)<br>'
            '<b style="color:#6b0000">6.</b> Hidrólisis del residuo (NaOH 2M, 60°C, 1h)<br>'
            '<b style="color:#6b0000">7.</b> Neutralizar + filtrar nuevamente<br>'
            '<b style="color:#6b0000">8.</b> Redisolver + análisis HPLC<br><br>'
            '<span style="color:#8b0000;font-size:.85rem">⚠️ Cada paso = pérdida de analito · '
            "Hidrólisis alcalina puede isomerizar polifenoles · "
            "Largo tiempo total: 4-6 h</span>"
            "</div>",
            unsafe_allow_html=True,
        )
    with col_p2:
        st.markdown(
            '<div style="border:2px solid #048a81;border-radius:8px;padding:1rem;background:#f0fff8">'
            '<b style="color:#048a81;font-size:1.05rem">✅ Protocolo NADES — 3 Pasos</b><br><br>'
            '<b style="color:#006050">1.</b> Mezclar muestra liofilizada (100 mg) + NADES óptimo<br>'
            '<span style="font-size:.82rem;color:#004040;padding-left:1rem">'
            "pH ácido del NADES hidroliza NEP simultáneamente</span><br><br>"
            '<b style="color:#006050">2.</b> Ultrasonido 20–25 kHz, 30 min<br>'
            '<span style="font-size:.82rem;color:#004040;padding-left:1rem">'
            "Cavitación rompe pared celular + extrae EP y NEP en simultáneo</span><br><br>"
            '<b style="color:#006050">3.</b> Centrifugar + filtrar → análisis directo<br>'
            '<span style="font-size:.82rem;color:#004040;padding-left:1rem">'
            "NADES compatible con inyección directa en HPLC (sin evaporar)</span><br><br>"
            '<span style="color:#004a40;font-size:.85rem">✅ Menos pasos = menos pérdida · '
            "Sin hidrólisis alcalina = sin isomerización · "
            "Tiempo total: 45 min · EP+NEP en una sola extracción</span>"
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("")
    # Gráfico comparativo de pérdida acumulada de analito
    pasos_conv = list(range(1, 9))
    # Pérdida acumulada estimada (cada paso pierde ~5-15% del analito residual)
    rendimiento_conv = [100]
    for p in [0.92, 0.88, 0.93, 0.85, 0.90, 0.87, 0.92]:  # factor retención por paso
        rendimiento_conv.append(rendimiento_conv[-1] * p)
    rendimiento_conv = rendimiento_conv[1:]

    rendimiento_nades = [100]
    for p in [0.97, 0.95, 0.98]:  # NADES: muy poca pérdida
        rendimiento_nades.append(rendimiento_nades[-1] * p)
    rendimiento_nades = rendimiento_nades[1:]

    fig_pasos = go.Figure()
    fig_pasos.add_trace(
        go.Scatter(
            x=list(range(1, 9)),
            y=rendimiento_conv,
            name="Convencional (8 pasos)",
            mode="lines+markers+text",
            line=dict(color="#c44536", width=2.5),
            marker=dict(size=10, color="#c44536"),
            text=[f"{v:.0f}%" for v in rendimiento_conv],
            textposition="top right",
            textfont=dict(size=9, color="#c44536"),
        )
    )
    fig_pasos.add_trace(
        go.Scatter(
            x=[1, 2, 3],
            y=rendimiento_nades,
            name="NADES + US (3 pasos)",
            mode="lines+markers+text",
            line=dict(color="#048a81", width=2.5),
            marker=dict(size=12, color="#048a81", symbol="star"),
            text=[f"{v:.0f}%" for v in rendimiento_nades],
            textposition="top right",
            textfont=dict(size=9, color="#048a81"),
        )
    )
    fig_pasos.add_annotation(
        x=8,
        y=rendimiento_conv[-1],
        text=f"Rendimiento final\nconvencional: {rendimiento_conv[-1]:.0f}%",
        showarrow=True,
        arrowcolor="#c44536",
        font=dict(color="#c44536", size=10),
        ax=-80,
        ay=-30,
    )
    fig_pasos.add_annotation(
        x=3,
        y=rendimiento_nades[-1],
        text=f"Rendimiento NADES: {rendimiento_nades[-1]:.0f}%",
        showarrow=True,
        arrowcolor="#048a81",
        font=dict(color="#048a81", size=10),
        ax=60,
        ay=-30,
    )
    fig_pasos.update_layout(
        height=320,
        xaxis=dict(
            title="Paso del proceso",
            tickmode="linear",
            dtick=1,
            tickvals=[1, 2, 3, 4, 5, 6, 7, 8],
            ticktext=[
                "Pesar",
                "Extrac.",
                "Centrf.",
                "Filtrar",
                "Evapo.",
                "Hidról.",
                "Neutral.",
                "Anális.",
            ],
        ),
        yaxis=dict(title="Rendimiento de analito (%)", range=[50, 108]),
        legend=dict(orientation="h", y=-0.25),
    )
    st.plotly_chart(fig_pasos, use_container_width=True)
    st.caption(
        "Pérdida acumulada estimada por paso. Ref: Saura-Calixto et al. (2010) J. Agric. Food Chem. 58, 11932 · "
        "Rendimiento NADES extrapolado de Benvenutti et al. (2019) Food Res. Int. 119, 710 · "
        "Modelo teórico: Cristofher Ferrada, Tesis Doctoral 2026"
    )


# ── Sub-tab: Estabilidad (dentro de tab2) ──
with atab_stab:
    st.markdown(t("t2_stab_title"))
    st.markdown(t("t2_stab_desc"))

    poly_stab_base = poly_df if not solo_principales else poly_df[poly_df["is_major"]]

    stab_detail = []
    for _, poly in poly_stab_base.iterrows():
        r = stability_score(props, poly, temp_C)
        stab_detail.append(
            {
                "Abrev": poly.get("abrev", poly["nombre"][:12]),
                "Clase": poly["clase"],
                "Tipo": poly["tipo"],
                "Estab. total (%)": round(r["total"] * 100, 1),
                "Prot. OH": round(r["Protección OH"] * 100, 1),
                "Barrera O₂": round(r["Barrera O₂"] * 100, 1),
                "Antioxid. NADES": round(r["Antioxidante NADES"] * 100, 1),
                "Estab. pH": round(r["Estab. pH"] * 100, 1),
                "Estab. Térmica": round(r["Estab. Térmica"] * 100, 1),
            }
        )
    stab_df = pd.DataFrame(stab_detail).sort_values("Estab. total (%)", ascending=False)

    col_s1, col_s2 = st.columns([2, 3])

    with col_s1:
        st.markdown("#### Ranking de Estabilidad")
        st.dataframe(
            stab_df[["Abrev", "Clase", "Tipo", "Estab. total (%)"]]
            .style.background_gradient(subset=["Estab. total (%)"], cmap="Greens", vmin=0, vmax=100)
            .format({"Estab. total (%)": "{:.1f}"}),
            use_container_width=True,
            hide_index=True,
            height=420,
        )

    with col_s2:
        st.markdown("#### Factores de estabilidad")
        factores_st = ["Prot. OH", "Barrera O₂", "Antioxid. NADES", "Estab. pH", "Estab. Térmica"]
        colors_st = ["#048a81", "#2e86ab", "#f18f01", "#a23b72", "#c44536"]
        fig_st = go.Figure()
        for i, f in enumerate(factores_st):
            fig_st.add_trace(
                go.Bar(
                    name=f,
                    x=stab_df["Abrev"],
                    y=stab_df[f],
                    marker_color=colors_st[i],
                )
            )
        fig_st.update_layout(
            barmode="stack",
            height=420,
            xaxis_tickangle=-40,
            yaxis_title="Contribución (%)",
            legend=dict(orientation="h", y=-0.40, font_size=9),
        )
        st.plotly_chart(fig_st, use_container_width=True)
        st.caption(
            "Ref: Benvenutti et al. (2019) Food Res. Int. 119, 710 — retención 80-95% de antocianinas con NADES · "
            "Chanioti & Tzia (2017) Food Bioprocess Technol. 10, 1999 — 92% retención con ChCl:Ác. Cítrico · "
            "Dai & Verpoorte (2014) Anal. Chim. Acta 766, 61 — red supramolecular DES como barrera oxidativa"
        )

    # Curva de temperatura vs estabilidad (énfasis en antocianinas)
    st.markdown("#### Efecto de la temperatura en la estabilidad de antocianinas")
    temp_stab = []
    antos_stab = poly_df[
        (poly_df["tipo"] == "EP") & (poly_df["clase"] == "Antocianina") & poly_df["is_major"]
    ]
    for t_val in range(20, 82, 2):
        for _, poly in antos_stab.iterrows():
            r = stability_score(props, poly, t_val)
            temp_stab.append(
                {
                    "T (°C)": t_val,
                    "Polifenol": poly.get("abrev", poly["nombre"]),
                    "Estab. (%)": r["total"] * 100,
                }
            )
    t_df = pd.DataFrame(temp_stab)
    fig_temp = px.line(
        t_df,
        x="T (°C)",
        y="Estab. (%)",
        color="Polifenol",
        color_discrete_sequence=px.colors.qualitative.Vivid,
    )
    fig_temp.add_vline(
        x=temp_C, line_dash="dot", line_color="#333", annotation_text=f"T actual: {temp_C}°C"
    )
    fig_temp.add_hrect(y0=0, y1=50, fillcolor="red", opacity=0.04)
    fig_temp.add_hrect(y0=70, y1=100, fillcolor="green", opacity=0.04)
    fig_temp.update_layout(
        height=310, yaxis_range=[0, 100], legend=dict(orientation="h", y=-0.35, font_size=9)
    )
    st.plotly_chart(fig_temp, use_container_width=True)
    st.caption(
        "Zona roja = inestable (<50%) · Zona verde = estable (>70%) · Solo antocianinas principales · "
        "Ref: Torskangerpoll & Andersen (2005) Food Chem. 89, 427 — degradación térmica de antocianinas · "
        "Benvenutti et al. (2019) Food Res. Int. 119, 710 — estabilidad térmica en NADES vs EtOH · "
        "Modelo: Ferrada, C. Tesis Doctoral 2026"
    )


# ══════════════════════════════════════════════════════════
# TAB 5 — ECONOMÍA
# ══════════════════════════════════════════════════════════
with tab5:
    st.markdown(t("t5_title"))
    st.markdown(t("t5_desc"))

    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        masa_muestra = st.number_input(
            t("t5_sample"), min_value=0.1, max_value=50.0, value=1.0, step=0.5
        )
    with col_e2:
        ratio_sl_eco = st.number_input(
            t("t5_sl_ratio"), min_value=2.0, max_value=50.0, value=10.0, step=1.0
        )
    with col_e3:
        n_repeticiones = st.number_input(t("t5_reps"), min_value=1, max_value=20, value=3, step=1)

    eco = economic_analysis(
        hba_sel,
        hbd_sel,
        ratio_hba,
        ratio_hbd,
        water_pct,
        HBA_COMPONENTS,
        HBD_COMPONENTS,
        masa_muestra_g=masa_muestra,
        ratio_sl=ratio_sl_eco,
    )

    st.markdown("---")
    st.markdown(t("t5_summary"))

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Volumen solvente", f"{eco['vol_total_ml']:.1f} mL")
    m2.metric("Costo NADES+agua", f"USD {eco['costo_total_usd']:.4f}")
    m3.metric(
        "Costo {n}×".format(n=int(n_repeticiones)),
        f"USD {eco['costo_total_usd']*n_repeticiones:.4f}",
    )
    m4.metric(
        "vs EtOH 70%",
        f"USD {eco['costo_etoh_ref_usd']:.4f}",
        delta=f"{eco['costo_total_usd']-eco['costo_etoh_ref_usd']:.4f}",
    )

    st.markdown(t("t5_breakdown"))
    col_d1, col_d2 = st.columns(2)

    with col_d1:
        desglose_data = {
            "Componente": [
                f"HBA: {hba_sel.split('(')[0].strip()[:25]}",
                f"HBD: {hbd_sel[:30]}",
                "Agua destilada",
            ],
            "Masa (g)": [eco["masa_hba_g"], eco["masa_hbd_g"], eco["masa_agua_g"]],
            "Precio (USD/kg)": [eco["precio_hba_kg"], eco["precio_hbd_kg"], 1],
            "Costo (USD)": [eco["costo_hba_usd"], eco["costo_hbd_usd"], eco["costo_agua_usd"]],
        }
        desglose_df = pd.DataFrame(desglose_data)
        st.dataframe(
            desglose_df.style.background_gradient(
                subset=["Costo (USD)"], cmap="YlOrBr", vmin=0
            ).format(
                {"Masa (g)": "{:.3f}", "Costo (USD)": "$ {:.5f}", "Precio (USD/kg)": "$ {:,.0f}"}
            ),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            f"Composición másica: HBA {eco['frac_masa_hba']}% · HBD {eco['frac_masa_hbd']}% · Agua {water_pct}%"
        )

    with col_d2:
        fig_eco_pie = go.Figure(
            go.Pie(
                labels=["HBA", "HBD", "Agua"],
                values=[eco["costo_hba_usd"], eco["costo_hbd_usd"], eco["costo_agua_usd"]],
                marker_colors=["#2e86ab", "#c44536", "#048a81"],
                textinfo="label+percent",
                hole=0.4,
            )
        )
        fig_eco_pie.update_layout(height=260, margin=dict(l=20, r=20, t=20, b=20), showlegend=False)
        st.plotly_chart(fig_eco_pie, use_container_width=True)

    st.markdown("---")
    st.markdown("#### Escala de experimento — ¿Cuánto necesito?")

    escalas = []
    for n_muestras in [1, 3, 6, 12, 24, 48]:
        eco_n = economic_analysis(
            hba_sel,
            hbd_sel,
            ratio_hba,
            ratio_hbd,
            water_pct,
            HBA_COMPONENTS,
            HBD_COMPONENTS,
            masa_muestra_g=masa_muestra,
            ratio_sl=ratio_sl_eco,
        )
        costo_n = eco_n["costo_total_usd"] * n_muestras
        escalas.append(
            {
                "N° extracciones": n_muestras,
                "Vol. total (mL)": round(eco_n["vol_total_ml"] * n_muestras, 1),
                "HBA necesario (g)": round(eco_n["masa_hba_g"] * n_muestras, 2),
                "HBD necesario (g)": round(eco_n["masa_hbd_g"] * n_muestras, 2),
                "Costo total (USD)": round(costo_n, 4),
            }
        )
    escala_df = pd.DataFrame(escalas)
    st.dataframe(
        escala_df.style.background_gradient(
            subset=["Costo total (USD)"], cmap="YlOrBr", vmin=0
        ).format({"Costo total (USD)": "$ {:.4f}"}),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")
    st.markdown("#### Comparación de costos: NADES vs solventes convencionales")
    vol_ref = eco["vol_total_ml"]
    comparacion = pd.DataFrame(
        [
            {
                "Solvente": f"NADES: {hba_sel.split('(')[0].strip()[:15]}:{hbd_sel[:15]}",
                "Costo (USD)": eco["costo_total_usd"],
                "Verde": "✅ Sí",
                "GRAS": "✅ Sí",
            },
            {
                "Solvente": "EtOH 70% (grado lab)",
                "Costo (USD)": eco["costo_etoh_ref_usd"],
                "Verde": "⚠️ Parcial",
                "GRAS": "✅ Sí",
            },
            {
                "Solvente": "MeOH 80%",
                "Costo (USD)": round(vol_ref * 1.05 * 0.030, 4),
                "Verde": "❌ No",
                "GRAS": "❌ No",
            },
            {
                "Solvente": "Acetona:H₂O 70%",
                "Costo (USD)": round(vol_ref * 1.02 * 0.022, 4),
                "Verde": "⚠️ Parcial",
                "GRAS": "❌ No",
            },
        ]
    )
    st.dataframe(
        comparacion.style.background_gradient(subset=["Costo (USD)"], cmap="Greens", vmin=0).format(
            {"Costo (USD)": "$ {:.4f}"}
        ),
        use_container_width=True,
        hide_index=True,
    )
    st.caption(
        f"Cálculo para {vol_ref:.1f} mL de solvente ({masa_muestra} g muestra liofilizada × {ratio_sl_eco:.0f} mL/g). "
        "Precios de referencia USD grado analítico. El NADES suele ser competitivo en costo y superior en perfil verde. "
        "Nota: concentraciones EP de Ruiz et al. (2024) en μmol/g FW; convertir con factor de liofilización (~5–8× según % humedad inicial). "
        "Ref: Ruiz et al. (2024) Horticulturae 10, 458 · Espino et al. (2016) Talanta 162, 412"
    )
    st.markdown(
        "> 💡 **Ventaja clave del NADES**: biodegradable, no volátil, no tóxico, reutilizable "
        "por evaporación y sin residuos peligrosos — ventajas que no se reflejan en el costo directo "
        "pero son críticas para escala industrial y certificación de extractos para consumo."
    )

    # ── Reutilización del NADES ──
    st.markdown("---")
    with st.expander("♻️ Reutilización del NADES — ¿Cuántos ciclos aguanta?", expanded=False):
        st.markdown(
            "Cada ciclo de extracción el NADES se **regenera por evaporación suave** (~60°C, vacío). "
            "Con cada ciclo se acumula una pequeña pérdida de capacidad HBD (~4.5%/ciclo) "
            "y de actividad antioxidante (~3%/ciclo), estimada a partir de Florindo et al. (2019)."
        )
        n_ciclos = st.slider("Número de ciclos de reutilización", 2, 10, 6, key="eco_ciclos")
        with st.spinner("Calculando ciclos de reutilización…"):
            reuse_df = nades_reuse_cycles(props, poly_df, n_cycles=n_ciclos, peso_ep=peso_ep)

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            fig_reuse = go.Figure()
            fig_reuse.add_trace(
                go.Scatter(
                    x=reuse_df["Ciclo"],
                    y=reuse_df["Retención EP (%)"],
                    name="Retención EP",
                    mode="lines+markers",
                    line=dict(color="#2e86ab", width=2.5),
                    marker=dict(size=9),
                )
            )
            fig_reuse.add_trace(
                go.Scatter(
                    x=reuse_df["Ciclo"],
                    y=reuse_df["Retención NEP (%)"],
                    name="Retención NEP",
                    mode="lines+markers",
                    line=dict(color="#c44536", width=2.5),
                    marker=dict(size=9),
                )
            )
            fig_reuse.add_trace(
                go.Scatter(
                    x=reuse_df["Ciclo"],
                    y=reuse_df["Cap. HBD (%)"],
                    name="Capacidad HBD",
                    mode="lines+markers",
                    line=dict(color="#f18f01", width=1.5, dash="dash"),
                    marker=dict(size=7),
                )
            )
            fig_reuse.add_hline(
                y=85,
                line_dash="dot",
                line_color="#048a81",
                annotation_text="85% retención (límite recomendado)",
                annotation_position="bottom right",
            )
            fig_reuse.update_layout(
                height=340,
                xaxis_title="Ciclo de reutilización",
                yaxis_title="Retención (%)",
                xaxis=dict(tickmode="linear", dtick=1),
                yaxis_range=[40, 102],
                legend=dict(orientation="h", y=-0.25),
            )
            st.plotly_chart(fig_reuse, use_container_width=True)

        with col_r2:
            st.dataframe(
                reuse_df[
                    [
                        "Ciclo",
                        "EP (%)",
                        "NEP (%)",
                        "Retención EP (%)",
                        "Retención NEP (%)",
                        "Costo relativo",
                    ]
                ]
                .style.background_gradient(
                    subset=["Retención EP (%)", "Retención NEP (%)"],
                    cmap="RdYlGn",
                    vmin=60,
                    vmax=100,
                )
                .format(
                    {
                        "EP (%)": "{:.1f}",
                        "NEP (%)": "{:.1f}",
                        "Retención EP (%)": "{:.1f}",
                        "Retención NEP (%)": "{:.1f}",
                        "Costo relativo": "1/{:.0f}",
                    }
                ),
                use_container_width=True,
                hide_index=True,
                height=280,
            )
            st.markdown(
                "**Costo relativo** = costo dividido entre el ciclo (Ciclo 1 = 1×, "
                "Ciclo 3 = 1/3 del costo, etc.)  \n"
                "Zona verde (>85%) = el NADES sigue siendo eficiente."
            )

        st.caption(
            "Ref: Florindo et al. (2019) ACS Sustain. Chem. Eng. 7, 3 — regeneración DES por evaporación · "
            "Ruesgas-Ramón et al. (2017) J. Agric. Food Chem. 65, 3591 — ciclos de reuso NADES · "
            "Degradación HBD: 4.5%/ciclo · Degradación antioxidante: 3.0%/ciclo · "
            "Ferrada, C. Tesis Doctoral 2026"
        )


# ══════════════════════════════════════════════════════════
# TAB 4 — OPTIMIZACIÓN  (Cinética · Diseño Experimental)
# ══════════════════════════════════════════════════════════
with tab4:
    otab_kin = seccion(t("otab_kin"))
    otab_dex = seccion(t("otab_dex"))


# ── Sub-tab: Cinética (dentro de tab4) ──
with otab_kin:
    st.markdown(t("t4_kin_title"))
    st.markdown(t("t4_kin_desc"))

    col_k1, col_k2, col_k3 = st.columns(3)
    with col_k1:
        kin_tmax = st.slider("Tiempo máximo (min)", 30, 180, 90, step=15, key="kin_tmax")
    with col_k2:
        kin_freq = st.slider(
            "Frecuencia UAE (kHz)",
            0,
            100,
            int(freq_us),
            step=5,
            key="kin_freq",
            help="0 = sin ultrasonido",
        )
    with col_k3:
        kin_peso = st.slider(
            "Peso EP en score", 0.30, 0.80, float(peso_ep), step=0.05, key="kin_peso"
        )

    with st.spinner("Calculando cinética…"):
        kin_df = extraction_kinetics(
            props, poly_df, time_max=kin_tmax, n_points=25, freq_us=kin_freq, peso_ep=kin_peso
        )

    t90_ep = kin_df.attrs.get("t90_ep", 0)
    t90_nep = kin_df.attrs.get("t90_nep", 0)
    k_ep = kin_df.attrs.get("k_ep", 0)
    k_nep = kin_df.attrs.get("k_nep", 0)
    ep_eq_v = kin_df.attrs.get("ep_eq", 0)
    nep_eq_v = kin_df.attrs.get("nep_eq", 0)

    # Métricas
    mk1, mk2, mk3, mk4 = st.columns(4)
    mk1.metric("k_EP (1/min)", f"{k_ep:.4f}")
    mk2.metric("k_NEP (1/min)", f"{k_nep:.4f}")
    mk3.metric("t₉₀ EP", f"{t90_ep:.1f} min")
    mk4.metric("t₉₀ NEP", f"{t90_nep:.1f} min")

    # Curva cinética
    fig_kin = go.Figure()
    fig_kin.add_trace(
        go.Scatter(
            x=kin_df["t (min)"],
            y=kin_df["EP (%)"],
            name="EP (%)",
            line=dict(color="#2e86ab", width=3),
            fill="tozeroy",
            fillcolor="rgba(46,134,171,0.08)",
        )
    )
    fig_kin.add_trace(
        go.Scatter(
            x=kin_df["t (min)"],
            y=kin_df["NEP (%)"],
            name="NEP (%)",
            line=dict(color="#c44536", width=3),
            fill="tozeroy",
            fillcolor="rgba(196,69,54,0.08)",
        )
    )
    fig_kin.add_trace(
        go.Scatter(
            x=kin_df["t (min)"],
            y=kin_df["Combinado (%)"],
            name="Combinado (%)",
            line=dict(color="#6b4226", width=2, dash="dash"),
        )
    )
    if t90_ep <= kin_tmax:
        fig_kin.add_vline(
            x=t90_ep,
            line_dash="dot",
            line_color="#2e86ab",
            annotation_text=f"t₉₀ EP: {t90_ep:.0f} min",
            annotation_position="top left",
        )
    if t90_nep <= kin_tmax:
        fig_kin.add_vline(
            x=t90_nep,
            line_dash="dot",
            line_color="#c44536",
            annotation_text=f"t₉₀ NEP: {t90_nep:.0f} min",
            annotation_position="top right",
        )
    # Líneas de equilibrio
    fig_kin.add_hline(
        y=ep_eq_v,
        line_dash="dot",
        line_color="rgba(46,134,171,0.4)",
        annotation_text=f"EP eq: {ep_eq_v:.1f}%",
        annotation_position="right",
    )
    fig_kin.add_hline(
        y=nep_eq_v,
        line_dash="dot",
        line_color="rgba(196,69,54,0.4)",
        annotation_text=f"NEP eq: {nep_eq_v:.1f}%",
        annotation_position="right",
    )
    fig_kin.update_layout(
        height=400,
        xaxis_title="Tiempo (min)",
        yaxis_title="Rendimiento (%)",
        yaxis_range=[0, 105],
        legend=dict(orientation="h", y=-0.20),
    )
    st.plotly_chart(fig_kin, use_container_width=True)
    st.caption(
        "Modelo: C(t) = C_eq × (1 − e^(−k·t))  ·  "
        "Ref: Cacace & Mazza (2003) J. Food Eng. 59, 379 · "
        "Torun et al. (2015) Sep. Purif. Technol. 156, 581 · "
        "k calculado con factores de viscosidad, temperatura y UAE · "
        "Modelo cinético: Ferrada, C. Tesis Doctoral 2026"
    )

    st.markdown("---")
    st.markdown("### ⚖️ Optimización de Razón Sólido:Líquido (S:L)")
    st.markdown(
        "El rendimiento aumenta con la razón S:L hasta alcanzar la **saturación del solvente** "
        "(modelo de Langmuir). Existe un punto óptimo donde se extrae ≥90% del máximo "
        "con el menor consumo de solvente."
    )

    with st.spinner("Calculando curva S:L…"):
        sl_df = sl_curve(props, poly_df, peso_ep=kin_peso)

    opt_ep = sl_df.attrs.get("opt_sl_ep", 20)
    opt_nep = sl_df.attrs.get("opt_sl_nep", 25)
    Ks_ep = sl_df.attrs.get("Ks_ep", 8.0)
    Ks_nep = sl_df.attrs.get("Ks_nep", 13.0)

    mk5, mk6 = st.columns(2)
    mk5.metric("S:L óptimo EP", f"{opt_ep} mL/g", help="Primer S:L con ≥90% del rendimiento máximo")
    mk6.metric(
        "S:L óptimo NEP", f"{opt_nep} mL/g", help="Primer S:L con ≥90% del rendimiento máximo"
    )

    fig_sl = go.Figure()
    fig_sl.add_trace(
        go.Scatter(
            x=sl_df["S:L (mL/g)"],
            y=sl_df["EP (%)"],
            name="EP (%)",
            mode="lines+markers",
            line=dict(color="#2e86ab", width=3),
            marker=dict(size=7),
        )
    )
    fig_sl.add_trace(
        go.Scatter(
            x=sl_df["S:L (mL/g)"],
            y=sl_df["NEP (%)"],
            name="NEP (%)",
            mode="lines+markers",
            line=dict(color="#c44536", width=3),
            marker=dict(size=7),
        )
    )
    fig_sl.add_trace(
        go.Scatter(
            x=sl_df["S:L (mL/g)"],
            y=sl_df["Combinado (%)"],
            name="Combinado (%)",
            mode="lines+markers",
            line=dict(color="#6b4226", width=2, dash="dash"),
            marker=dict(size=5),
        )
    )
    if opt_ep in sl_df["S:L (mL/g)"].values:
        fig_sl.add_vline(
            x=opt_ep,
            line_dash="dot",
            line_color="#2e86ab",
            annotation_text=f"Óptimo EP: {opt_ep} mL/g",
            annotation_position="top left",
        )
    if opt_nep in sl_df["S:L (mL/g)"].values:
        fig_sl.add_vline(
            x=opt_nep,
            line_dash="dot",
            line_color="#c44536",
            annotation_text=f"Óptimo NEP: {opt_nep} mL/g",
            annotation_position="top right",
        )
    fig_sl.update_layout(
        height=380,
        xaxis_title="Razón S:L (mL/g)",
        yaxis_title="Rendimiento (%)",
        yaxis_range=[0, 105],
        legend=dict(orientation="h", y=-0.20),
    )
    st.plotly_chart(fig_sl, use_container_width=True)
    st.caption(
        f"Modelo Langmuir: Y(S:L) = Y_eq × S:L / (Ks + S:L)  ·  "
        f"Ks_EP = {Ks_ep} mL/g · Ks_NEP = {Ks_nep} mL/g  ·  "
        "Ref: Liyana-Pathirana & Shahidi (2005) Food Chem. 93, 47 · "
        "Pinelo et al. (2006) J. Food Eng. 74, 395 · "
        "Adaptación: Ferrada, C. Tesis Doctoral 2026"
    )

    st.dataframe(
        sl_df.style.background_gradient(subset=["EP (%)"], cmap="Blues", vmin=0, vmax=100)
        .background_gradient(subset=["NEP (%)"], cmap="Reds", vmin=0, vmax=80)
        .background_gradient(subset=["Combinado (%)"], cmap="YlOrBr", vmin=0, vmax=100)
        .format({"EP (%)": "{:.1f}", "NEP (%)": "{:.1f}", "Combinado (%)": "{:.1f}"}),
        use_container_width=True,
        hide_index=True,
        height=300,
    )


# ── Sub-tab: Diseño Experimental (dentro de tab4) ──
with otab_dex:
    st.markdown(t("t4_dex_title"))
    st.markdown(t("t4_dex_desc"))

    col_dex1, col_dex2 = st.columns([1, 2])

    with col_dex1:
        design_type = st.selectbox(
            t("t4_design_type"),
            options=["box_behnken", "central_composite", "full_factorial"],
            format_func=lambda x: {
                "box_behnken": "Box-Behnken (3-4 factores)",
                "central_composite": "Compuesto Central / CCD (2-5 factores)",
                "full_factorial": "Factorial Completo 2ᵏ",
            }[x],
            key="dex_type",
            help="Box-Behnken: eficiente, sin puntos de esquina · CCD: incluye puntos estrella · Factorial: 2^k",
        )
        n_factors_dex = st.slider("Número de factores", 2, 4, 3, key="dex_nf")

    with col_dex2:
        st.markdown("#### Definir niveles de factores")
        factor_names_default = ["Razón HBA:HBD", "Agua (%)", "Temperatura (°C)", "Razón S:L (mL/g)"]
        factor_ranges_default = [
            (1.0, 2.0, 3.0),
            (10.0, 30.0, 50.0),
            (25.0, 40.0, 60.0),
            (5.0, 10.0, 20.0),
        ]
        factors_dex = []
        for i in range(n_factors_dex):
            name_d = factor_names_default[i]
            low_d, c_d, high_d = factor_ranges_default[i]
            with st.expander(f"Factor {i+1}: {name_d}", expanded=(i < 2)):
                c1f, c2f, c3f, c4f = st.columns(4)
                fname = c1f.text_input("Nombre", value=name_d, key=f"dex_fname_{i}")
                flow = c2f.number_input("Nivel bajo", value=low_d, key=f"dex_low_{i}")
                fcent = c3f.number_input("Centro", value=c_d, key=f"dex_cent_{i}")
                fhigh = c4f.number_input("Nivel alto", value=high_d, key=f"dex_high_{i}")
            factors_dex.append({"name": fname, "low": flow, "center": fcent, "high": fhigh})

    if st.button("📐 Generar matriz experimental", type="primary", key="dex_gen"):
        try:
            dex_df = generate_experimental_design(factors_dex, design_type=design_type)
            st.session_state["dex_df"] = dex_df
        except Exception as e:
            st.error(f"Error al generar diseño: {e}")

    if "dex_df" in st.session_state:
        dex_df = st.session_state["dex_df"]
        n_runs = len(dex_df)
        st.success(
            f"Diseño generado: **{n_runs} ensayos** ({design_type.replace('_', ' ').title()})"
        )

        # Columnas reales (sin las codificadas)
        real_cols = [c for c in dex_df.columns if "(cod)" not in c]
        cod_cols = [c for c in dex_df.columns if "(cod)" in c]

        st.markdown(f"#### Matriz de experimentos ({n_runs} ensayos)")
        st.dataframe(
            dex_df[real_cols]
            .style.background_gradient(cmap="Blues", axis=0)
            .format("{:.2f}", subset=real_cols[1:] if len(real_cols) > 1 else real_cols),
            use_container_width=True,
            hide_index=False,
            height=min(450, 30 + n_runs * 38),
        )

        col_dex_dl1, col_dex_dl2 = st.columns(2)
        with col_dex_dl1:
            csv_dex = dex_df.to_csv(index=True)
            st.download_button(
                "📥 Descargar CSV completo",
                data=csv_dex,
                file_name=f"diseño_{design_type}_{n_factors_dex}f.csv",
                mime="text/csv",
            )
        with col_dex_dl2:
            # Plantilla con columna respuesta vacía
            template_cols = real_cols + ["TPC (mg GAE/g)", "TAC (mg C3G/g)", "DPPH (%)"]
            template_df = dex_df[real_cols].copy()
            for col_r in ["TPC (mg GAE/g)", "TAC (mg C3G/g)", "DPPH (%)"]:
                template_df[col_r] = ""
            csv_tpl = template_df.to_csv(index=True)
            st.download_button(
                "📋 Plantilla con columnas de respuesta",
                data=csv_tpl,
                file_name=f"plantilla_{design_type}_{n_factors_dex}f.csv",
                mime="text/csv",
            )

        if cod_cols:
            with st.expander("Ver matriz codificada (−1 / 0 / +1 / ±α)"):
                st.dataframe(
                    dex_df[["Ensayo"] + cod_cols if "Ensayo" in dex_df.columns else cod_cols],
                    use_container_width=True,
                    hide_index=False,
                )

        st.caption(
            "Box-Behnken: Box & Behnken (1960) Technometrics 2, 455 · "
            "CCD: Myers & Montgomery (2002) Response Surface Methodology, 2nd ed. · "
            "Factorial 2ᵏ: Montgomery (2017) Design and Analysis of Experiments, 9th ed."
        )
    else:
        st.info("Presiona **Generar matriz experimental** para crear la tabla de ensayos.")
        st.markdown("""
        **¿Cuándo usar cada diseño?**

        | Diseño | Factores | Ensayos | Uso recomendado |
        |---|---|---|---|
        | **Box-Behnken** | 3–4 | 15–27 | Optimización sin puntos de esquina |
        | **CCD** | 2–5 | 9–27+ | Superficie de respuesta completa |
        | **Factorial 2ᵏ** | 2–4 | 4–16 | Screening inicial de factores |
        """)


# ══════════════════════════════════════════════════════════
# TAB 6 — MIS DATOS
# ══════════════════════════════════════════════════════════
with tab6:
    st.markdown(t("t6_title"))
    st.markdown(t("t6_desc"))

    # ── Formato esperado ──
    with st.expander(t("t6_format"), expanded=False):
        ejemplo_df = pd.DataFrame(
            {
                "NADES": ["ChCl:Ac.Cítrico", "ChCl:Glicerol", "Betaína:Glicerol"],
                "HBA": ["Cloruro de Colina (ChCl)", "Cloruro de Colina (ChCl)", "Betaína"],
                "HBD": ["Ácido Cítrico", "Glicerol", "Glicerol"],
                "Ratio": ["1:1", "1:2", "1:3"],
                "Agua (%)": [30, 30, 20],
                "Temp (°C)": [40, 40, 50],
                "TPC_exp": [85.2, 72.4, 68.1],
                "TAC_exp": [45.3, 38.7, 33.2],
            }
        )
        st.dataframe(ejemplo_df, use_container_width=True, hide_index=True)
        st.caption(
            "Las columnas HBA y HBD deben coincidir con los nombres del simulador. "
            "TPC_exp y TAC_exp en mg GAE/g DW y mg C3G/g DW respectivamente."
        )
        csv_ejemplo = ejemplo_df.to_csv(index=False)
        st.download_button(
            "📥 Descargar plantilla CSV de ejemplo",
            data=csv_ejemplo,
            file_name="plantilla_datos_experimentales.csv",
            mime="text/csv",
        )

    # ── Bitácora acumulada entre sesiones ──
    from experimentos import RUTA_BITACORA, cargar_bitacora

    _bitacora = cargar_bitacora()
    if not _bitacora.empty:
        st.markdown("#### 📒 Bitácora acumulada")
        st.caption(
            f"{len(_bitacora)} ensayos registrados · se conservan entre sesiones en "
            f"`{RUTA_BITACORA.name}`"
        )
        st.dataframe(_bitacora, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇️ Descargar bitácora completa",
            data=_bitacora.to_csv(index=False),
            file_name="bitacora_experimentos.csv",
            mime="text/csv",
        )
        st.divider()

    # ── Uploader ──
    uploaded = st.file_uploader(
        "Cargar CSV con resultados experimentales",
        type=["csv"],
        help="El CSV debe tener al menos columnas: HBA, HBD, Ratio, Agua (%), Temp (°C), TPC_exp",
    )

    if uploaded is not None:
        try:
            exp_df = pd.read_csv(uploaded)
            # F2 — Persistir en session_state para uso por Recomendador
            st.session_state["exp_df"] = exp_df
            st.success(f"Archivo cargado: {len(exp_df)} filas, {len(exp_df.columns)} columnas")
            st.dataframe(exp_df, use_container_width=True, hide_index=True)

            # La sesión muere al cerrar la app; la bitácora no. Aquí es donde el
            # resultado real de la placa se confronta con lo que el modelo predijo.
            from experimentos import anexar_experimentos

            if st.button("💾 Guardar en la bitácora", key="guardar_bitacora"):
                _total = anexar_experimentos(exp_df)
                st.success(f"Bitácora actualizada: {len(_total)} ensayos acumulados")

            required = {"HBA", "HBD", "Ratio", "Agua (%)", "Temp (°C)", "TPC_exp"}
            missing = required - set(exp_df.columns)
            if missing:
                st.error(f"Columnas faltantes: {', '.join(missing)}")
            else:
                st.markdown("---")
                st.markdown("#### Comparación predicción vs experimental")

                comp_rows = []
                for _, row in exp_df.iterrows():
                    hba_r = str(row["HBA"])
                    hbd_r = str(row["HBD"])
                    # buscar en los dict por nombre parcial
                    hba_match = next((k for k in HBA_COMPONENTS if hba_r in k or k in hba_r), None)
                    hbd_match = next((k for k in HBD_COMPONENTS if hbd_r in k or k in hbd_r), None)
                    if hba_match is None or hbd_match is None:
                        continue
                    ratio_str = str(row.get("Ratio", "1:1"))
                    from data import RATIOS_DISPONIBLES as _RATIOS

                    ratio_pair = _RATIOS.get(ratio_str, (1, 1))
                    p_exp = calculate_nades_properties(
                        hba_match,
                        hbd_match,
                        ratio_pair[0],
                        ratio_pair[1],
                        int(row["Agua (%)"]),
                        int(row["Temp (°C)"]),
                        HBA_COMPONENTS,
                        HBD_COMPONENTS,
                    )
                    s_exp = run_full_simulation(p_exp, poly_df, peso_ep=peso_ep, freq_us=0)
                    ep_pred = s_exp[s_exp["tipo"] == "EP"]["EP (%)"].mean()
                    nep_pred = s_exp[s_exp["tipo"] == "NEP"]["NEP (%)"].mean()
                    tpc_exp = float(row["TPC_exp"])
                    # normalizar TPC_exp a escala 0-100 asumiendo máx ~500 mg/g DW
                    tpc_norm = min(100.0, tpc_exp / 5.0)
                    comp_rows.append(
                        {
                            "NADES": row.get("NADES", f"{hba_r}:{hbd_r}"),
                            "EP predicho (%)": round(ep_pred, 1),
                            "TPC exp (norm. %)": round(tpc_norm, 1),
                            "NEP predicho (%)": round(nep_pred, 1),
                            "Error EP (pp)": round(ep_pred - tpc_norm, 1),
                        }
                    )

                if comp_rows:
                    comp_df = pd.DataFrame(comp_rows)
                    # R² EP
                    y_pred = comp_df["EP predicho (%)"].values
                    y_exp = comp_df["TPC exp (norm. %)"].values
                    ss_res = np.sum((y_exp - y_pred) ** 2)
                    ss_tot = np.sum((y_exp - np.mean(y_exp)) ** 2)
                    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")

                    st.metric(
                        "R² Modelo EP vs TPC experimental",
                        f"{r2:.3f}",
                        help="1.0 = predicción perfecta · <0.5 = modelo no ajusta a estos datos",
                    )

                    # Parity plot
                    fig_par = go.Figure()
                    fig_par.add_trace(
                        go.Scatter(
                            x=y_exp,
                            y=y_pred,
                            mode="markers+text",
                            text=comp_df["NADES"].str[:12],
                            textposition="top right",
                            textfont=dict(size=9),
                            marker=dict(
                                size=12, color="#2e86ab", line=dict(color="white", width=1.5)
                            ),
                            name="NADES",
                        )
                    )
                    lim = max(max(y_exp), max(y_pred)) * 1.1
                    fig_par.add_trace(
                        go.Scatter(
                            x=[0, lim],
                            y=[0, lim],
                            mode="lines",
                            name="Predicción perfecta",
                            line=dict(color="#888", dash="dash"),
                        )
                    )
                    fig_par.update_layout(
                        height=400,
                        xaxis_title="TPC experimental (normalizado %)",
                        yaxis_title="EP predicho (%)",
                        xaxis_range=[0, lim],
                        yaxis_range=[0, lim],
                    )
                    st.plotly_chart(fig_par, use_container_width=True)
                    st.caption(
                        "Parity plot: puntos sobre la diagonal = modelo sobreestima · "
                        "bajo la diagonal = modelo subestima · "
                        "Normalización TPC: valor exp / 5 (asume máx ~500 mg GAE/g DW)"
                    )

                    st.dataframe(
                        comp_df.style.background_gradient(
                            subset=["EP predicho (%)"], cmap="Blues", vmin=0, vmax=100
                        )
                        .background_gradient(
                            subset=["TPC exp (norm. %)"], cmap="Greens", vmin=0, vmax=100
                        )
                        .format(
                            {c: "{:.1f}" for c in comp_df.columns if "(%)" in c or "(pp)" in c}
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )

                    # ── F2: Calibración automática del peso EP ──
                    st.markdown("---")
                    st.markdown("#### 🔬 F2 — Calibrar peso EP con mis datos experimentales")
                    st.markdown(
                        "Encuentra el valor de **peso EP** que minimiza el error entre la predicción "
                        "del modelo y tus datos de **TPC experimental**. "
                        "Ejecuta un barrido en el rango 0.30–0.80."
                    )
                    if st.button("🔍 Calibrar peso EP automáticamente", key="btn_calibrate_ep"):
                        calib_rows = []
                        for p_test in np.arange(0.30, 0.85, 0.05):
                            p_test = round(float(p_test), 2)
                            err_sum = 0.0
                            n_rows = 0
                            for _, row_c in exp_df.iterrows():
                                hba_c = str(row_c["HBA"])
                                hbd_c = str(row_c["HBD"])
                                hba_mc = next(
                                    (k for k in HBA_COMPONENTS if hba_c in k or k in hba_c), None
                                )
                                hbd_mc = next(
                                    (k for k in HBD_COMPONENTS if hbd_c in k or k in hbd_c), None
                                )
                                if hba_mc is None or hbd_mc is None:
                                    continue
                                from data import RATIOS_DISPONIBLES as _R2

                                rp = _R2.get(str(row_c.get("Ratio", "1:1")), (1, 1))
                                p_c = calculate_nades_properties(
                                    hba_mc,
                                    hbd_mc,
                                    rp[0],
                                    rp[1],
                                    int(row_c["Agua (%)"]),
                                    int(row_c["Temp (°C)"]),
                                    HBA_COMPONENTS,
                                    HBD_COMPONENTS,
                                )
                                s_c = run_full_simulation(p_c, poly_df, peso_ep=p_test, freq_us=0)
                                ep_c = s_c[s_c["tipo"] == "EP"]["EP (%)"].mean()
                                tpc_c = min(100.0, float(row_c["TPC_exp"]) / 5.0)
                                err_sum += (ep_c - tpc_c) ** 2
                                n_rows += 1
                            rmse_c = np.sqrt(err_sum / n_rows) if n_rows > 0 else float("nan")
                            calib_rows.append({"Peso EP": p_test, "RMSE (pp)": round(rmse_c, 2)})

                        if calib_rows:
                            calib_df = pd.DataFrame(calib_rows)
                            best_peso_row = calib_df.loc[calib_df["RMSE (pp)"].idxmin()]
                            best_peso_val = best_peso_row["Peso EP"]

                            st.session_state["calib_peso_ep"] = best_peso_val
                            st.success(
                                f"✅ Peso EP óptimo encontrado: **{best_peso_val:.2f}** "
                                f"(RMSE mínimo: {best_peso_row['RMSE (pp)']:.2f} pp)"
                            )

                            fig_calib = go.Figure()
                            fig_calib.add_trace(
                                go.Scatter(
                                    x=calib_df["Peso EP"],
                                    y=calib_df["RMSE (pp)"],
                                    mode="lines+markers",
                                    name="RMSE",
                                    line=dict(color="#6b4226", width=2),
                                    marker=dict(size=8),
                                )
                            )
                            fig_calib.add_vline(
                                x=best_peso_val,
                                line_dash="dot",
                                line_color="#048a81",
                                annotation_text=f"Óptimo: {best_peso_val:.2f}",
                            )
                            fig_calib.update_layout(
                                height=280,
                                xaxis_title="Peso EP en score combinado",
                                yaxis_title="RMSE (pp)",
                                title="Calibración: RMSE vs peso EP",
                            )
                            st.plotly_chart(fig_calib, use_container_width=True)
                            st.info(
                                f"💡 Ajusta el deslizador **Peso EP en score combinado** del sidebar a "
                                f"**{best_peso_val:.2f}** para calibrar el simulador con tus datos."
                            )

                else:
                    st.warning(
                        "No se encontraron filas con HBA/HBD reconocidos por el simulador. "
                        "Verifica que los nombres coincidan con los del sidebar."
                    )

        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")
    else:
        st.info("Carga un archivo CSV para comparar tus resultados experimentales con el modelo.")
        st.markdown("""
        **¿Qué puedo comparar?**
        - **TPC experimental** (Folin-Ciocalteu) vs **EP predicho** por el simulador
        - El **Parity Plot** muestra visualmente qué NADES el modelo predice bien
        - El **R²** cuantifica el ajuste global del modelo teórico a tus datos
        """)


# ══════════════════════════════════════════════════════════
# TAB 7 — RECOMENDADOR  (Búsqueda global · Cribado Tesis)
# ══════════════════════════════════════════════════════════
with tab7:
    rtab_rec = seccion(t("rtab_rec"))
    rtab_comp = seccion(t("rtab_comp"))
    rtab_th = seccion(t("rtab_th"))


# ── Sub-tab: Comparador de NADES F1 (dentro de tab7) ──
with rtab_comp:
    st.markdown(t("comp_title"))
    st.markdown(t("comp_desc"))

    col_a_hdr, col_b_hdr = st.columns(2)
    with col_a_hdr:
        st.markdown(t("comp_nades_a"))
        comp_hba_a = st.selectbox(
            t("hba_label"), list(HBA_COMPONENTS.keys()), index=0, key="comp_hba_a"
        )
        comp_hbd_a = st.selectbox(
            t("hbd_label"), list(HBD_COMPONENTS.keys()), index=1, key="comp_hbd_a"
        )
        comp_ratio_a = st.select_slider(
            t("ratio_label"),
            options=list(RATIOS_DISPONIBLES.keys()),
            value="1:1",
            key="comp_ratio_a",
        )
        comp_water_a = st.slider(t("water_label"), 0, 50, 30, step=5, key="comp_water_a")
        comp_temp_a = st.slider(t("temp_label"), 20, 80, 40, step=5, key="comp_temp_a")
        comp_freq_a = st.slider("UAE A (kHz)", 0, 100, 0, step=5, key="comp_freq_a")

    with col_b_hdr:
        st.markdown(t("comp_nades_b"))
        comp_hba_b = st.selectbox(
            t("hba_label"), list(HBA_COMPONENTS.keys()), index=2, key="comp_hba_b"
        )
        comp_hbd_b = st.selectbox(
            t("hbd_label"), list(HBD_COMPONENTS.keys()), index=3, key="comp_hbd_b"
        )
        comp_ratio_b = st.select_slider(
            t("ratio_label"),
            options=list(RATIOS_DISPONIBLES.keys()),
            value="1:2",
            key="comp_ratio_b",
        )
        comp_water_b = st.slider(t("water_label"), 0, 50, 30, step=5, key="comp_water_b")
        comp_temp_b = st.slider(t("temp_label"), 20, 80, 40, step=5, key="comp_temp_b")
        comp_freq_b = st.slider("UAE B (kHz)", 0, 100, 0, step=5, key="comp_freq_b")

    comp_peso_ep = st.slider(
        t("ep_weight_label"),
        min_value=0.30,
        max_value=0.80,
        value=0.55,
        step=0.05,
        key="comp_peso",
    )

    if is_same_compound(comp_hba_a, comp_hbd_a):
        st.warning("⚠️ NADES A: HBA y HBD son el mismo compuesto — no es un NADES válido.")
    if is_same_compound(comp_hba_b, comp_hbd_b):
        st.warning("⚠️ NADES B: HBA y HBD son el mismo compuesto — no es un NADES válido.")

    run_comp = st.button(t("comp_run"), type="primary", key="btn_run_comp")

    if run_comp:
        _rha, _rda = RATIOS_DISPONIBLES[comp_ratio_a]
        _rhb, _rdb = RATIOS_DISPONIBLES[comp_ratio_b]
        props_a = calculate_nades_properties(
            comp_hba_a,
            comp_hbd_a,
            _rha,
            _rda,
            comp_water_a,
            comp_temp_a,
            HBA_COMPONENTS,
            HBD_COMPONENTS,
        )
        props_b = calculate_nades_properties(
            comp_hba_b,
            comp_hbd_b,
            _rhb,
            _rdb,
            comp_water_b,
            comp_temp_b,
            HBA_COMPONENTS,
            HBD_COMPONENTS,
        )
        sim_a = run_full_simulation(props_a, poly_df, peso_ep=comp_peso_ep, freq_us=comp_freq_a)
        sim_b = run_full_simulation(props_b, poly_df, peso_ep=comp_peso_ep, freq_us=comp_freq_b)

        def _avg(df, col, tipo=None):
            sub = df[df["tipo"] == tipo] if tipo else df
            return sub[col].mean() if len(sub) > 0 else 0.0

        comp_metrics = {
            "NADES A": {
                "label": f"{comp_hba_a.split('(')[0].strip()} : {comp_hbd_a} ({comp_ratio_a})",
                "EP (%)": _avg(sim_a, "EP (%)", "EP"),
                "NEP (%)": _avg(sim_a, "NEP (%)", "NEP"),
                "Estab. (%)": _avg(sim_a, "Estab. (%)"),
                "Combinado (%)": _avg(sim_a, "Combinado (%)"),
                "pH": props_a["pH"],
                "Viscosidad (cP)": props_a["viscosidad"],
                "Polaridad": props_a["polaridad"],
                "props": props_a,
                "sim": sim_a,
            },
            "NADES B": {
                "label": f"{comp_hba_b.split('(')[0].strip()} : {comp_hbd_b} ({comp_ratio_b})",
                "EP (%)": _avg(sim_b, "EP (%)", "EP"),
                "NEP (%)": _avg(sim_b, "NEP (%)", "NEP"),
                "Estab. (%)": _avg(sim_b, "Estab. (%)"),
                "Combinado (%)": _avg(sim_b, "Combinado (%)"),
                "pH": props_b["pH"],
                "Viscosidad (cP)": props_b["viscosidad"],
                "Polaridad": props_b["polaridad"],
                "props": props_b,
                "sim": sim_b,
            },
        }
        st.session_state["comp_metrics"] = comp_metrics
        st.session_state["comp_peso_ep"] = comp_peso_ep

    if "comp_metrics" in st.session_state:
        cm = st.session_state["comp_metrics"]
        cm_peso = st.session_state.get("comp_peso_ep", 0.55)
        a_data = cm["NADES A"]
        b_data = cm["NADES B"]

        st.markdown("---")
        st.markdown("### 📊 Resultados de la comparación")

        # ── Gauges A vs B ──
        ga1, ga2, ga3, ga4, gb1, gb2, gb3, gb4 = st.columns(8)
        gauge_cols_a = [ga1, ga2, ga3, ga4]
        gauge_cols_b = [gb1, gb2, gb3, gb4]
        gauge_keys = [
            ("EP (%)", "EP", "#2e86ab"),
            ("NEP (%)", "NEP", "#c44536"),
            ("Estab. (%)", "Estabilidad", "#048a81"),
            ("Combinado (%)", "Combinado", "#6b4226"),
        ]

        def _mini_gauge(val, title, color, label):
            return val

        # Mostrar métricas lado a lado
        st.markdown(
            f'<div style="display:flex;gap:1rem;margin-bottom:.5rem">'
            f'<div style="flex:1;background:#e8f4f9;border-radius:8px;padding:.8rem;border-left:4px solid #2e86ab">'
            f'<b style="color:#2e86ab">NADES A</b><br>'
            f'<small>{a_data["label"]}</small><br>'
            f"<b>{comp_water_a}% H₂O · {comp_temp_a}°C · {comp_freq_a} kHz</b>"
            f"</div>"
            f'<div style="flex:1;background:#fdf2f2;border-radius:8px;padding:.8rem;border-left:4px solid #c44536">'
            f'<b style="color:#c44536">NADES B</b><br>'
            f'<small>{b_data["label"]}</small><br>'
            f"<b>{comp_water_b}% H₂O · {comp_temp_b}°C · {comp_freq_b} kHz</b>"
            f"</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

        # Tabla de métricas comparativas
        _metrics_names = [
            "EP (%)",
            "NEP (%)",
            "Estab. (%)",
            "Combinado (%)",
            "pH",
            "Viscosidad (cP)",
            "Polaridad",
        ]
        comp_tbl = pd.DataFrame(
            {
                "Métrica": _metrics_names,
                "NADES A": [
                    round(a_data[m], 2) if isinstance(a_data[m], float) else a_data[m]
                    for m in _metrics_names
                ],
                "NADES B": [
                    round(b_data[m], 2) if isinstance(b_data[m], float) else b_data[m]
                    for m in _metrics_names
                ],
            }
        )
        comp_tbl["Δ (A−B)"] = comp_tbl["NADES A"] - comp_tbl["NADES B"]

        def _color_delta(val):
            if val > 1:
                return "color: #0a3d1a; font-weight:700"
            elif val < -1:
                return "color: #8b0000; font-weight:700"
            return ""

        st.dataframe(
            comp_tbl.style.applymap(_color_delta, subset=["Δ (A−B)"]).format(
                {"NADES A": "{:.2f}", "NADES B": "{:.2f}", "Δ (A−B)": "{:+.2f}"}
            ),
            use_container_width=True,
            hide_index=True,
        )
        fig_caption(7, f"Comparación de métricas: {a_data['label']} vs {b_data['label']}")

        # ── Gráfico de barras agrupadas ──
        st.markdown("#### Comparación de índices de extracción")
        fig_comp_bar = go.Figure()
        _idx_labels = ["EP (%)", "NEP (%)", "Estab. (%)", "Combinado (%)"]
        _idx_colors = ["#2e86ab", "#c44536", "#048a81", "#6b4226"]
        _idx_a_vals = [a_data[k] for k in _idx_labels]
        _idx_b_vals = [b_data[k] for k in _idx_labels]
        fig_comp_bar.add_trace(
            go.Bar(
                name="NADES A",
                x=_idx_labels,
                y=_idx_a_vals,
                marker_color="#2e86ab",
                text=[f"{v:.1f}%" for v in _idx_a_vals],
                textposition="outside",
            )
        )
        fig_comp_bar.add_trace(
            go.Bar(
                name="NADES B",
                x=_idx_labels,
                y=_idx_b_vals,
                marker_color="#c44536",
                text=[f"{v:.1f}%" for v in _idx_b_vals],
                textposition="outside",
            )
        )
        fig_comp_bar.update_layout(
            barmode="group",
            height=350,
            yaxis_range=[0, 110],
            yaxis_title="Índice promedio (%)",
            legend=dict(orientation="h", y=-0.2),
        )
        st.plotly_chart(fig_comp_bar, use_container_width=True)
        fig_caption(7, f"Índices de extracción comparados: NADES A vs B (peso EP={cm_peso:.0%})")

        # ── Radar overlay ──
        st.markdown("#### Perfil comparativo (radar)")
        _radar_cats = [
            t("radar_pol"),
            t("radar_flu"),
            t("radar_hbd"),
            t("radar_hba"),
            t("radar_acid"),
            t("radar_antx"),
        ]

        def _radar_vals_from_props(p):
            vn = 1 - np.log10(max(p["viscosidad"], 1)) / np.log10(10000)
            return [
                p["polaridad"],
                max(0, vn),
                p["cap_hbd"] / 10,
                p["cap_hba"] / 10,
                max(0, (5 - p["pH"]) / 5),
                p["antioxidant_nades"],
            ]

        rv_a = _radar_vals_from_props(a_data["props"])
        rv_b = _radar_vals_from_props(b_data["props"])
        cats_closed = _radar_cats + [_radar_cats[0]]

        fig_comp_rad = go.Figure()
        fig_comp_rad.add_trace(
            go.Scatterpolar(
                r=rv_a + [rv_a[0]],
                theta=cats_closed,
                fill="toself",
                name="NADES A",
                fillcolor="rgba(46,134,171,0.15)",
                line=dict(color="#2e86ab", width=2),
            )
        )
        fig_comp_rad.add_trace(
            go.Scatterpolar(
                r=rv_b + [rv_b[0]],
                theta=cats_closed,
                fill="toself",
                name="NADES B",
                fillcolor="rgba(196,69,54,0.15)",
                line=dict(color="#c44536", width=2),
            )
        )
        fig_comp_rad.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            height=380,
            legend=dict(orientation="h", y=-0.15),
        )
        st.plotly_chart(fig_comp_rad, use_container_width=True)
        fig_caption(7, "Perfil de propiedades fisicoquímicas NADES A vs B (normalizado 0–1)")

        # ── Curva de agua para ambos ──
        st.markdown("#### Curva extracción EP vs % agua — A y B")
        _wrange = range(0, 55, 5)
        _curve_a, _curve_b = [], []
        _rha2, _rda2 = RATIOS_DISPONIBLES[comp_ratio_a]
        _rhb2, _rdb2 = RATIOS_DISPONIBLES[comp_ratio_b]
        for _wc in _wrange:
            _pa = calculate_nades_properties(
                comp_hba_a,
                comp_hbd_a,
                _rha2,
                _rda2,
                _wc,
                comp_temp_a,
                HBA_COMPONENTS,
                HBD_COMPONENTS,
            )
            _sa = run_full_simulation(_pa, poly_df, peso_ep=cm_peso, freq_us=comp_freq_a)
            _curve_a.append(
                {
                    "Agua (%)": _wc,
                    "EP": _sa[_sa["tipo"] == "EP"]["EP (%)"].mean() if len(_sa) > 0 else 0,
                }
            )
            _pb = calculate_nades_properties(
                comp_hba_b,
                comp_hbd_b,
                _rhb2,
                _rdb2,
                _wc,
                comp_temp_b,
                HBA_COMPONENTS,
                HBD_COMPONENTS,
            )
            _sb = run_full_simulation(_pb, poly_df, peso_ep=cm_peso, freq_us=comp_freq_b)
            _curve_b.append(
                {
                    "Agua (%)": _wc,
                    "EP": _sb[_sb["tipo"] == "EP"]["EP (%)"].mean() if len(_sb) > 0 else 0,
                }
            )

        _cdf_a = pd.DataFrame(_curve_a)
        _cdf_b = pd.DataFrame(_curve_b)
        fig_comp_water = go.Figure()
        fig_comp_water.add_trace(
            go.Scatter(
                x=_cdf_a["Agua (%)"],
                y=_cdf_a["EP"],
                name="NADES A — EP",
                line=dict(color="#2e86ab", width=2),
                mode="lines+markers",
            )
        )
        fig_comp_water.add_trace(
            go.Scatter(
                x=_cdf_b["Agua (%)"],
                y=_cdf_b["EP"],
                name="NADES B — EP",
                line=dict(color="#c44536", width=2, dash="dash"),
                mode="lines+markers",
            )
        )
        fig_comp_water.add_vline(
            x=comp_water_a,
            line_dash="dot",
            line_color="#2e86ab",
            annotation_text=f"A: {comp_water_a}%",
        )
        fig_comp_water.add_vline(
            x=comp_water_b,
            line_dash="dot",
            line_color="#c44536",
            annotation_text=f"B: {comp_water_b}%",
        )
        fig_comp_water.update_layout(
            height=300,
            xaxis_title="Agua añadida (%)",
            yaxis_title="EP promedio (%)",
            yaxis_range=[0, 100],
            legend=dict(orientation="h", y=-0.25),
        )
        st.plotly_chart(fig_comp_water, use_container_width=True)
        fig_caption(
            7, "Efecto del % agua en el índice EP: NADES A (azul) vs NADES B (rojo punteado)"
        )

        # ── Veredicto ──
        delta_comb = a_data["Combinado (%)"] - b_data["Combinado (%)"]
        if abs(delta_comb) < 2:
            _veredicto = "⚖️ **Empate técnico** — diferencia < 2 pp. Ambos NADES son equivalentes para este objetivo."
            _v_color = "#666"
        elif delta_comb > 0:
            _veredicto = f"🏆 **NADES A es superior** por {delta_comb:.1f} pp de score combinado."
            _v_color = "#2e86ab"
        else:
            _veredicto = f"🏆 **NADES B es superior** por {-delta_comb:.1f} pp de score combinado."
            _v_color = "#c44536"

        st.markdown(
            f'<div style="border:2px solid {_v_color};border-radius:10px;padding:1rem;'
            f'background:#f8faff;margin-top:.5rem">'
            f'<span style="color:{_v_color};font-size:1.05rem">{_veredicto}</span>'
            f"</div>",
            unsafe_allow_html=True,
        )
        st.caption(
            f"Peso EP = {cm_peso:.0%} · Peso NEP = {1-cm_peso:.0%} · "
            "Score combinado incluye penalización por asimetría EP/NEP · "
            "Ref: Ferrada, C. Tesis Doctoral 2026"
        )
    else:
        st.info(
            "Configura NADES A y B en los paneles de arriba y presiona **Comparar NADES A vs B**."
        )
        st.markdown("""
        **¿Qué muestra el comparador?**
        - Tabla de métricas con diferencias (Δ) resaltadas
        - Gráfico de barras agrupadas de EP · NEP · Estabilidad · Combinado
        - Radar overlay de propiedades fisicoquímicas
        - Curva de extracción EP vs % agua para ambos NADES
        - **Veredicto automático** con el NADES ganador
        """)


# ── Sub-tab: Cribado Tesis (dentro de tab7) ──
with rtab_th:
    st.markdown(t("t7_th_title"))
    st.markdown(t("t7_th_desc"))
    thesis_temp = st.slider("Temperatura de cribado (°C)", 20, 80, 40, step=5, key="t_thesis")
    thesis_peso_ep = st.slider(
        "Peso EP en score combinado (cribado)",
        min_value=0.30,
        max_value=0.80,
        value=0.55,
        step=0.05,
        key="thesis_ep_weight",
    )

    @st.cache_data
    def get_thesis_comparison(t, pep):
        return compare_thesis_nades(poly_df, HBA_COMPONENTS, HBD_COMPONENTS, THESIS_NADES, t)

    thesis_df = get_thesis_comparison(thesis_temp, thesis_peso_ep)

    # Tarjetas de los 6 NADES
    cols = st.columns(3)
    for i, row in thesis_df.iterrows():
        with cols[i % 3]:
            ep_ = row["EP prom. (%)"]
            nep_ = row["NEP prom. (%)"]
            st_ = row["Estab. (%)"]
            comb_ = row.get("Combinado (%)", 0.0)
            color = row["color"]
            st.markdown(
                f'<div style="border:2px solid {color};border-radius:8px;padding:.8rem;margin-bottom:.6rem">'
                f'<b style="color:{color}">{row["NADES"]}</b><br>'
                f'<span style="font-size:.8rem">{row["Ratio"]} · {row["Agua (%)"]}% H₂O</span><br><br>'
                f"🟦 EP: <b>{ep_:.1f}%</b> &nbsp; 🟥 NEP: <b>{nep_:.1f}%</b><br>"
                f"🟩 Estab: <b>{st_:.1f}%</b> &nbsp; 🎯 Combinado: <b>{comb_:.1f}%</b><br>"
                f'<span style="font-size:.75rem">pH {row["pH efec."]} · {int(row["Viscosidad"])} cP · ETN {row["Polaridad"]}</span>'
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # Gráfico de barras agrupadas EP+NEP+Estab+Combinado
    thesis_melt = thesis_df[
        ["NADES", "EP prom. (%)", "NEP prom. (%)", "Estab. (%)", "Combinado (%)"]
    ].melt(id_vars="NADES", var_name="Índice", value_name="Valor (%)")
    color_map2 = {
        "EP prom. (%)": "#2e86ab",
        "NEP prom. (%)": "#c44536",
        "Estab. (%)": "#048a81",
        "Combinado (%)": "#6b4226",
    }
    fig_th = px.bar(
        thesis_melt,
        x="NADES",
        y="Valor (%)",
        color="Índice",
        barmode="group",
        color_discrete_map=color_map2,
    )
    fig_th.update_layout(
        height=400,
        xaxis_tickangle=-20,
        legend=dict(orientation="h", y=-0.30),
        yaxis_range=[0, 100],
    )
    st.plotly_chart(fig_th, use_container_width=True)

    # Radar comparativo de los 6
    st.markdown("#### Perfil comparativo de propiedades de los 6 NADES")
    fig_th_rad = go.Figure()
    radar_cats_th = ["Polaridad", "Fluidez", "Cap. HBD", "Acidez", "Antioxidante"]

    for i, row in thesis_df.iterrows():
        p = row["_props"]
        vn = 1 - np.log10(max(p["viscosidad"], 1)) / np.log10(10000)
        rv = [
            p["polaridad"],
            max(0, vn),
            p["cap_hbd"] / 10,
            max(0, (5 - p["pH"]) / 5),
            p["antioxidant_nades"],
        ]
        rv_closed = rv + [rv[0]]
        cats_closed = radar_cats_th + [radar_cats_th[0]]
        fig_th_rad.add_trace(
            go.Scatterpolar(
                r=rv_closed,
                theta=cats_closed,
                fill="toself",
                name=row["NADES"],
                fillcolor="rgba(0,0,0,0.05)",
                line=dict(color=THESIS_COLORS[i], width=2),
            )
        )
    fig_th_rad.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        height=420,
        legend=dict(orientation="h", y=-0.20),
    )
    st.plotly_chart(fig_th_rad, use_container_width=True)

    # Tabla resumen
    st.markdown("#### Tabla resumen")
    cols_tabla = [
        "NADES",
        "Ratio",
        "Agua (%)",
        "EP prom. (%)",
        "NEP prom. (%)",
        "Estab. (%)",
        "Combinado (%)",
        "pH efec.",
        "Viscosidad",
        "Polaridad",
    ]
    cols_show = [c for c in cols_tabla if c in thesis_df.columns]
    st.dataframe(
        thesis_df[cols_show]
        .style.background_gradient(subset=["EP prom. (%)"], cmap="Blues", vmin=0, vmax=100)
        .background_gradient(subset=["NEP prom. (%)"], cmap="Reds", vmin=0, vmax=80)
        .background_gradient(subset=["Estab. (%)"], cmap="Greens", vmin=0, vmax=100)
        .background_gradient(
            subset=["Combinado (%)"] if "Combinado (%)" in thesis_df.columns else [],
            cmap="YlOrBr",
            vmin=0,
            vmax=100,
        )
        .format(
            {
                "EP prom. (%)": "{:.1f}",
                "NEP prom. (%)": "{:.1f}",
                "Estab. (%)": "{:.1f}",
                "Combinado (%)": "{:.1f}",
                "pH efec.": "{:.2f}",
                "Viscosidad": "{:.0f} cP",
                "Polaridad": "{:.3f}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


# ── Sub-tab: Recomendador Global (dentro de tab7) ──
with rtab_rec:
    st.markdown(t("t7_rec_title"))
    st.markdown(
        '<div class="comb-badge">Evalúa automáticamente las 759 combinaciones HBA × HBD × ratio '
        "y encuentra el NADES óptimo según tu objetivo. Tres modos de búsqueda disponibles.</div>",
        unsafe_allow_html=True,
    )
    st.markdown("")

    # ── Selector de modo ──
    rec_mode = st.radio(
        "**Modo de búsqueda:**",
        ["🎯  Por objetivo EP / NEP", "💧  Optimizar % de agua", "🔧  Búsqueda completa"],
        horizontal=True,
        key="rec_mode_radio",
        help=(
            "🎯 Por objetivo: el simulador busca el NADES óptimo y el % agua óptimo automáticamente según tu prioridad\n"
            "💧 Optimizar agua: fija el % agua y encuentra el mejor NADES para esa condición\n"
            "🔧 Búsqueda completa: control total de todos los parámetros"
        ),
    )
    st.markdown("---")

    # ═══════════════════════════════════════════════════════════════
    # MODO 1 — Por objetivo EP / NEP
    # ═══════════════════════════════════════════════════════════════
    if rec_mode.startswith("🎯"):
        st.markdown("### 🎯 Recomendador por Objetivo")
        st.markdown(
            "Elige qué fracción quieres priorizar. El simulador barre **todas las combinaciones de NADES** "
            "en 5 niveles de agua (10–50%) y devuelve las **condiciones óptimas completas** "
            "(mejor NADES + % agua + temperatura + UAE)."
        )

        col_o1, col_o2 = st.columns(2)
        with col_o1:
            obj_temp = st.slider("Temperatura del proceso (°C)", 20, 80, 40, step=5, key="obj_temp")
        with col_o2:
            obj_freq = st.slider(
                "Frecuencia UAE (kHz, 0 = sin US)", 0, 100, 20, step=5, key="obj_freq"
            )

        st.markdown("")
        st.markdown("**¿Qué quieres maximizar?**")
        c_ep, c_bal, c_nep = st.columns(3)
        with c_ep:
            btn_ep = st.button(
                "🔵 Maximizar EP\n(polifenoles extraíbles)",
                use_container_width=True,
                key="btn_ep_obj",
                help="Peso EP = 0.80 — ideal para cuantificar polifenoles libres por HPLC",
            )
        with c_bal:
            btn_bal = st.button(
                "⚖️ Balance EP + NEP\n(extracción total)",
                use_container_width=True,
                type="primary",
                key="btn_bal_obj",
                help="Peso EP = 0.55 — score combinado equilibrado EP+NEP simultáneos",
            )
        with c_nep:
            btn_nep = st.button(
                "🔴 Maximizar NEP\n(polifenoles no extraíbles)",
                use_container_width=True,
                key="btn_nep_obj",
                help="Peso EP = 0.25 — prioriza taninos condensados/hidrolizables de la matriz",
            )

        if btn_ep:
            st.session_state["obj_target"] = "ep"
            st.session_state["obj_temp_v"] = obj_temp
            st.session_state["obj_freq_v"] = obj_freq
            st.session_state.pop("obj_result", None)
        elif btn_bal:
            st.session_state["obj_target"] = "balance"
            st.session_state["obj_temp_v"] = obj_temp
            st.session_state["obj_freq_v"] = obj_freq
            st.session_state.pop("obj_result", None)
        elif btn_nep:
            st.session_state["obj_target"] = "nep"
            st.session_state["obj_temp_v"] = obj_temp
            st.session_state["obj_freq_v"] = obj_freq
            st.session_state.pop("obj_result", None)

        obj_target = st.session_state.get("obj_target")

        if obj_target is not None and "obj_result" not in st.session_state:
            _peso_map_obj = {"ep": 0.80, "balance": 0.55, "nep": 0.25}
            _label_map_obj = {
                "ep": "Maximizar EP",
                "balance": "Balance EP+NEP",
                "nep": "Maximizar NEP",
            }
            _color_map_obj = {"ep": "#2e86ab", "balance": "#6b4226", "nep": "#c44536"}
            peso_rec_obj = _peso_map_obj[obj_target]
            _t_obj = st.session_state.get("obj_temp_v", obj_temp)
            _f_obj = st.session_state.get("obj_freq_v", obj_freq)

            best_rows_obj = []
            with st.spinner(
                f"Buscando el mejor NADES para «{_label_map_obj[obj_target]}»…  "
                f"(5 niveles de agua × 759 NADES)"
            ):
                for w_obj in [10, 20, 30, 40, 50]:
                    df_w_obj = sweep_all_nades(
                        HBA_COMPONENTS,
                        HBD_COMPONENTS,
                        poly_df,
                        water_pct=w_obj,
                        temp_C=_t_obj,
                        freq_us=_f_obj,
                        time_min=30,
                        peso_ep=peso_rec_obj,
                    )
                    if not df_w_obj.empty:
                        r_obj = df_w_obj.iloc[0].copy()
                        r_obj["Agua óptima (%)"] = w_obj
                        best_rows_obj.append(r_obj)

            if best_rows_obj:
                best_all_obj = (
                    pd.DataFrame(best_rows_obj)
                    .sort_values("Combinado (%)", ascending=False)
                    .reset_index(drop=True)
                )
                st.session_state["obj_result"] = best_all_obj
                st.session_state["obj_label"] = _label_map_obj[obj_target]
                st.session_state["obj_color"] = _color_map_obj[obj_target]
                st.session_state["obj_peso"] = peso_rec_obj

        if "obj_result" in st.session_state:
            best_all_obj = st.session_state["obj_result"]
            obj_label = st.session_state.get("obj_label", "")
            obj_color = st.session_state.get("obj_color", "#6b4226")
            obj_peso_v = st.session_state.get("obj_peso", 0.55)
            best_obj = best_all_obj.iloc[0]
            _t_obj_v = st.session_state.get("obj_temp_v", 40)
            _f_obj_v = st.session_state.get("obj_freq_v", 20)
            _agua_opt = int(best_obj["Agua óptima (%)"])

            # ── Tarjeta ganadora ──
            st.markdown(f"### 🏆 Mejor NADES para: *{obj_label}*")
            _bg_obj = (
                "#e8f4f9"
                if obj_color == "#2e86ab"
                else "#fdf2f2" if obj_color == "#c44536" else "#fdf8f2"
            )
            st.markdown(
                f'<div style="border:3px solid {obj_color};border-radius:12px;padding:1.2rem 1.5rem;'
                f'background:{_bg_obj};margin-bottom:1rem">'
                f'<span style="font-size:1.6rem">🥇</span> '
                f'<b style="font-size:1.2rem;color:{obj_color}">'
                f'{best_obj["HBA"].split("(")[0].strip()} : {best_obj["HBD"]}</b>'
                f'&nbsp;&nbsp;<span style="color:#666">({best_obj["Ratio"]})</span>'
                f"<br><br>"
                f"<b>💧 % Agua óptimo:</b>&nbsp;"
                f'<span style="font-size:1.15rem;color:{obj_color}"><b>{_agua_opt}%</b></span>'
                f"&emsp;|&emsp;"
                f'<b>🌡️ Temperatura:</b>&nbsp;<span style="font-size:1.1rem"><b>{_t_obj_v}°C</b></span>'
                f"&emsp;|&emsp;"
                f'<b>🔊 UAE:</b>&nbsp;<span style="font-size:1.1rem"><b>{_f_obj_v} kHz</b></span>'
                f"<br><br>"
                f'🔵 <b>EP:</b>&nbsp;<span style="font-size:1.2rem;color:#2e86ab">'
                f'<b>{best_obj["EP final (%)"]:.1f}%</b></span>'
                f"&emsp;&emsp;"
                f'🔴 <b>NEP:</b>&nbsp;<span style="font-size:1.2rem;color:#c44536">'
                f'<b>{best_obj["NEP final (%)"]:.1f}%</b></span>'
                f"&emsp;&emsp;"
                f'🎯 <b>Combinado:</b>&nbsp;<span style="font-size:1.2rem;color:{obj_color}">'
                f'<b>{best_obj["Combinado (%)"]:.1f}%</b></span>'
                f"</div>",
                unsafe_allow_html=True,
            )

            # ── Curva EP / NEP vs % agua para el NADES ganador ──
            st.markdown("#### Curva de extracción vs % Agua — NADES ganador")
            _ratio_str_obj = best_obj["Ratio"]
            _rh_obj, _rd_obj = (
                (int(x) for x in _ratio_str_obj.split(":")) if ":" in _ratio_str_obj else (1, 1)
            )
            agua_curve_obj = []
            for wc_obj in range(0, 55, 5):
                _pw_obj = calculate_nades_properties(
                    best_obj["HBA"],
                    best_obj["HBD"],
                    _rh_obj,
                    _rd_obj,
                    wc_obj,
                    _t_obj_v,
                    HBA_COMPONENTS,
                    HBD_COMPONENTS,
                )
                _proc_obj = simulate_3step_process(
                    _pw_obj,
                    poly_df,
                    freq_us=_f_obj_v,
                    temp_C=_t_obj_v,
                    time_min=30,
                    peso_ep=obj_peso_v,
                )
                ep_oc = (
                    _proc_obj[_proc_obj["tipo"] == "EP"]["EP final (%)"].mean()
                    if not _proc_obj.empty
                    else 0
                )
                nep_oc = (
                    _proc_obj[_proc_obj["tipo"] == "NEP"]["NEP final (%)"].mean()
                    if not _proc_obj.empty
                    else 0
                )
                agua_curve_obj.append(
                    {"Agua (%)": wc_obj, "EP (%)": round(ep_oc, 1), "NEP (%)": round(nep_oc, 1)}
                )

            agua_df_obj = pd.DataFrame(agua_curve_obj)
            fig_agua_obj = go.Figure()
            fig_agua_obj.add_trace(
                go.Scatter(
                    x=agua_df_obj["Agua (%)"],
                    y=agua_df_obj["EP (%)"],
                    name="EP (%)",
                    line=dict(color="#2e86ab", width=3),
                    mode="lines+markers",
                    marker=dict(size=7),
                )
            )
            fig_agua_obj.add_trace(
                go.Scatter(
                    x=agua_df_obj["Agua (%)"],
                    y=agua_df_obj["NEP (%)"],
                    name="NEP (%)",
                    line=dict(color="#c44536", width=3),
                    mode="lines+markers",
                    marker=dict(size=7),
                )
            )
            fig_agua_obj.add_vline(
                x=_agua_opt,
                line_dash="dot",
                line_color=obj_color,
                annotation_text=f"Óptimo: {_agua_opt}%",
                annotation_position="top right",
            )
            fig_agua_obj.update_layout(
                height=320,
                xaxis_title="Agua (%)",
                yaxis_title="Extracción final (%)",
                yaxis_range=[0, 100],
                legend=dict(orientation="h", y=-0.25),
            )
            st.plotly_chart(fig_agua_obj, use_container_width=True)
            st.caption(
                "Curva calculada con Proceso 3 Pasos (UAE + centrifugación + filtración) · "
                f"T = {_t_obj_v}°C · UAE = {_f_obj_v} kHz · "
                "La línea punteada marca el % agua con el mejor score combinado encontrado"
            )

            # ── Top candidato por nivel de agua ──
            st.markdown("#### Mejor NADES por cada nivel de agua evaluado")
            st.dataframe(
                best_all_obj[
                    [
                        "HBA",
                        "HBD",
                        "Ratio",
                        "Agua óptima (%)",
                        "EP final (%)",
                        "NEP final (%)",
                        "Combinado (%)",
                    ]
                ]
                .style.background_gradient(subset=["EP final (%)"], cmap="Blues", vmin=0, vmax=100)
                .background_gradient(subset=["NEP final (%)"], cmap="Reds", vmin=0, vmax=100)
                .background_gradient(subset=["Combinado (%)"], cmap="YlOrBr", vmin=0, vmax=100)
                .format(
                    {"EP final (%)": "{:.1f}", "NEP final (%)": "{:.1f}", "Combinado (%)": "{:.1f}"}
                ),
                use_container_width=True,
                hide_index=True,
            )
            st.caption(
                "Cada fila = el NADES ganador encontrado para ese nivel de agua específico. "
                "La fila #1 (arriba) es el óptimo global entre todos los niveles."
            )

            # ── Adoptar uno del ranking ──
            # Sin esto el recomendador y el panel lateral afirman cosas distintas sobre
            # cuál es el NADES activo, y hay que copiar los cuatro campos a mano.
            st.markdown("#### Adoptar uno de estos")
            _n_rank = len(best_all_obj)
            _elegido = st.selectbox(
                "NADES del ranking",
                options=list(range(_n_rank)),
                format_func=lambda i: (
                    f"#{i + 1} · {best_all_obj.iloc[i]['HBA'].split('(')[0].strip()} : "
                    f"{best_all_obj.iloc[i]['HBD']} ({best_all_obj.iloc[i]['Ratio']}, "
                    f"{int(best_all_obj.iloc[i]['Agua óptima (%)'])}% H₂O) — "
                    f"combinado {best_all_obj.iloc[i]['Combinado (%)']:.1f}%"
                ),
                key="rank_elegido",
            )
            if st.button("✅ Usar este NADES", type="primary", key="adoptar_nades"):
                _fila = best_all_obj.iloc[_elegido]
                st.session_state["sel_hba"] = str(_fila["HBA"])
                st.session_state["sel_hbd"] = str(_fila["HBD"])
                st.session_state["sel_ratio"] = str(_fila["Ratio"])
                st.session_state["sel_water"] = int(_fila["Agua óptima (%)"])
                st.rerun()
            st.caption(
                "Al adoptarlo pasa a ser el NADES activo: la franja superior y todas las "
                "demás pestañas se recalculan sobre él."
            )

        elif obj_target is None:
            st.info(
                "👆 Ajusta temperatura y UAE, luego presiona uno de los tres botones para encontrar el NADES óptimo."
            )
            st.markdown("""
            | Botón | Peso EP | Peso NEP | Ideal para... |
            |---|---|---|---|
            | 🔵 Maximizar EP | 80% | 20% | Análisis HPLC de polifenoles libres |
            | ⚖️ Balance | 55% | 45% | Extracción total simultánea EP+NEP |
            | 🔴 Maximizar NEP | 25% | 75% | Recuperación de taninos de la pared celular |

            > El simulador evalúa **759 combinaciones × 5 niveles de agua = 3 795 simulaciones**
            > y devuelve el mejor resultado con sus condiciones exactas.
            """)

    # ═══════════════════════════════════════════════════════════════
    # MODO 2 — Optimizar % de agua
    # ═══════════════════════════════════════════════════════════════
    elif rec_mode.startswith("💧"):
        st.markdown("### 💧 Optimizar % de Agua")
        st.markdown(
            "Ajusta el % de agua con el deslizador y encuentra qué NADES es el mejor "
            "**exactamente en esa condición**. También muestra cómo varía la extracción "
            "del NADES ganador al cambiar el % de agua."
        )

        col_w1, col_w2, col_w3 = st.columns(3)
        with col_w1:
            water_opt = st.slider("% Agua a evaluar", 0, 50, 30, step=5, key="opt_water_pct")
        with col_w2:
            water_temp = st.slider("Temperatura (°C)", 20, 80, 40, step=5, key="opt_water_temp")
        with col_w3:
            water_freq = st.slider("UAE (kHz)", 0, 100, 20, step=5, key="opt_water_freq")

        water_peso = st.slider(
            "Peso EP en score combinado", 0.30, 0.80, 0.55, step=0.05, key="opt_water_peso"
        )

        if st.button(
            f"🔍 Encontrar mejor NADES para {water_opt}% agua",
            type="primary",
            key="btn_water_opt",
        ):
            with st.spinner(f"Evaluando 759 NADES con {water_opt}% de agua…"):
                water_sweep_df = sweep_all_nades(
                    HBA_COMPONENTS,
                    HBD_COMPONENTS,
                    poly_df,
                    water_pct=water_opt,
                    temp_C=water_temp,
                    freq_us=water_freq,
                    time_min=30,
                    peso_ep=water_peso,
                )
            st.session_state["water_sweep_df"] = water_sweep_df
            st.session_state["water_sweep_w"] = water_opt
            st.session_state["water_sweep_temp"] = water_temp
            st.session_state["water_sweep_freq"] = water_freq
            st.session_state["water_sweep_peso"] = water_peso

        if "water_sweep_df" in st.session_state:
            w_df = st.session_state["water_sweep_df"]
            w_val = st.session_state["water_sweep_w"]
            w_temp = st.session_state["water_sweep_temp"]
            w_freq = st.session_state["water_sweep_freq"]
            w_peso = st.session_state["water_sweep_peso"]
            top_w = w_df.head(10)
            best_w = w_df.iloc[0]

            st.success(f"🏆 Mejor NADES con {w_val}% agua · {w_temp}°C · {w_freq} kHz")
            st.markdown(
                f'<div style="border:2px solid #048a81;border-radius:10px;padding:1rem 1.2rem;background:#f0fff8">'
                f'<b style="color:#048a81;font-size:1.15rem">'
                f'{best_w["HBA"].split("(")[0].strip()} : {best_w["HBD"]}</b>'
                f'&nbsp;&nbsp;<span style="color:#666">({best_w["Ratio"]})</span><br><br>'
                f"💧 <b>Agua:</b> {w_val}%"
                f"&emsp;|&emsp;🌡️ <b>T:</b> {w_temp}°C"
                f"&emsp;|&emsp;🔊 <b>UAE:</b> {w_freq} kHz<br><br>"
                f'🔵 EP: <b style="color:#2e86ab">{best_w["EP final (%)"]:.1f}%</b>'
                f'&emsp;🔴 NEP: <b style="color:#c44536">{best_w["NEP final (%)"]:.1f}%</b>'
                f'&emsp;🎯 Combinado: <b style="color:#048a81">{best_w["Combinado (%)"]:.1f}%</b>'
                f"</div>",
                unsafe_allow_html=True,
            )
            st.markdown("")

            # ── Curva EP / NEP vs % agua para el NADES ganador ──
            st.markdown("#### Curva de extracción vs % Agua — NADES ganador")
            _ratio_w = best_w["Ratio"]
            _rh_w, _rd_w = (int(x) for x in _ratio_w.split(":")) if ":" in _ratio_w else (1, 1)
            curve_data_w = []
            for wc_w in range(0, 55, 5):
                pw_wc = calculate_nades_properties(
                    best_w["HBA"],
                    best_w["HBD"],
                    _rh_w,
                    _rd_w,
                    wc_w,
                    w_temp,
                    HBA_COMPONENTS,
                    HBD_COMPONENTS,
                )
                proc_wc = simulate_3step_process(
                    pw_wc,
                    poly_df,
                    freq_us=w_freq,
                    temp_C=w_temp,
                    time_min=30,
                    peso_ep=w_peso,
                )
                ep_wc = (
                    proc_wc[proc_wc["tipo"] == "EP"]["EP final (%)"].mean()
                    if not proc_wc.empty
                    else 0
                )
                nep_wc = (
                    proc_wc[proc_wc["tipo"] == "NEP"]["NEP final (%)"].mean()
                    if not proc_wc.empty
                    else 0
                )
                curve_data_w.append(
                    {"Agua (%)": wc_w, "EP (%)": round(ep_wc, 1), "NEP (%)": round(nep_wc, 1)}
                )

            cdf_w = pd.DataFrame(curve_data_w)
            fig_cw = go.Figure()
            fig_cw.add_trace(
                go.Scatter(
                    x=cdf_w["Agua (%)"],
                    y=cdf_w["EP (%)"],
                    name="EP (%)",
                    line=dict(color="#2e86ab", width=3),
                    mode="lines+markers",
                    marker=dict(size=7),
                )
            )
            fig_cw.add_trace(
                go.Scatter(
                    x=cdf_w["Agua (%)"],
                    y=cdf_w["NEP (%)"],
                    name="NEP (%)",
                    line=dict(color="#c44536", width=3),
                    mode="lines+markers",
                    marker=dict(size=7),
                )
            )
            fig_cw.add_vline(
                x=w_val,
                line_dash="dot",
                line_color="#048a81",
                annotation_text=f"Evaluado: {w_val}%",
            )
            fig_cw.update_layout(
                height=320,
                xaxis_title="Agua (%)",
                yaxis_title="Extracción final (%)",
                yaxis_range=[0, 100],
                legend=dict(orientation="h", y=-0.25),
            )
            st.plotly_chart(fig_cw, use_container_width=True)
            st.caption(
                "Curva del NADES ganador con el % agua variando de 0 a 50% · "
                "La línea punteada marca el % agua evaluado · "
                "Proceso 3 Pasos completo (UAE + centrifugación + filtración)"
            )

            # ── Top 10 tabla ──
            st.markdown(f"#### Top 10 NADES para {w_val}% agua")
            cols_w = [
                c
                for c in [
                    "NADES",
                    "HBA",
                    "HBD",
                    "Ratio",
                    "EP final (%)",
                    "NEP final (%)",
                    "Degrad. T (%)",
                    "Combinado (%)",
                    "Estab. (%)",
                ]
                if c in top_w.columns
            ]
            st.dataframe(
                top_w[cols_w]
                .style.background_gradient(subset=["EP final (%)"], cmap="Blues", vmin=0, vmax=100)
                .background_gradient(subset=["NEP final (%)"], cmap="Reds", vmin=0, vmax=100)
                .background_gradient(subset=["Combinado (%)"], cmap="YlOrBr", vmin=0, vmax=100)
                .format(
                    {
                        "EP final (%)": "{:.1f}",
                        "NEP final (%)": "{:.1f}",
                        "Degrad. T (%)": "{:.1f}",
                        "Combinado (%)": "{:.1f}",
                        "Estab. (%)": "{:.1f}",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

            # ── Gráfico de barras Top 10 ──
            fig_bar_w = go.Figure()
            fig_bar_w.add_trace(
                go.Bar(
                    y=top_w["NADES"][::-1],
                    x=top_w["EP final (%)"][::-1],
                    name="EP final",
                    orientation="h",
                    marker_color="#2e86ab",
                )
            )
            fig_bar_w.add_trace(
                go.Bar(
                    y=top_w["NADES"][::-1],
                    x=top_w["NEP final (%)"][::-1],
                    name="NEP final",
                    orientation="h",
                    marker_color="#c44536",
                )
            )
            fig_bar_w.update_layout(
                barmode="group",
                height=max(300, len(top_w) * 30),
                xaxis_title="Índice (%)",
                xaxis_range=[0, 100],
                legend=dict(orientation="h", y=-0.15),
                margin=dict(l=220),
            )
            st.plotly_chart(fig_bar_w, use_container_width=True)

        else:
            st.info(
                f"Ajusta los parámetros y presiona **Encontrar mejor NADES para {water_opt}% agua**."
            )
            st.markdown("""
            💡 **¿Cuándo usar este modo?**
            - Tienes una restricción de % agua (ej: ≤20% para compatibilidad con HPLC)
            - Quieres comparar qué NADES es el mejor exactamente en esa condición de agua
            - Ver cómo el % de agua afecta la extracción del NADES ganador
            """)

    # ═══════════════════════════════════════════════════════════════
    # MODO 3 — Búsqueda completa (control total)
    # ═══════════════════════════════════════════════════════════════
    else:
        st.markdown("### 🔧 Búsqueda Completa")
        st.markdown(
            "Control total sobre todos los parámetros. Ideal para explorar el espacio de búsqueda "
            "y comparar combinaciones específicas."
        )

        col_r1, col_r2, col_r3, col_r4, col_r5 = st.columns(5)
        with col_r1:
            sweep_water = st.slider("Agua (%)", 0, 50, 30, step=5, key="sw_water")
        with col_r2:
            sweep_temp = st.slider(
                "Temperatura (°C)", 20, 80, int(proc_temp), step=5, key="sw_temp"
            )
        with col_r3:
            sweep_freq = st.slider("UAE (kHz)", 0, 100, int(freq_us), step=5, key="sw_freq")
        with col_r4:
            sweep_time = st.slider("Tiempo (min)", 5, 60, int(proc_time), step=5, key="sw_time")
        with col_r5:
            sweep_peso = st.slider("Peso EP", 0.30, 0.80, 0.55, step=0.05, key="sw_ep")

        top_n = st.slider("Top N candidatos a mostrar", 5, 30, 15, step=5)

        run_sweep = st.button("🔍 Ejecutar búsqueda global", type="primary")

        if run_sweep:
            with st.spinner("Evaluando todas las combinaciones HBA × HBD × ratio…"):
                sweep_df = sweep_all_nades(
                    HBA_COMPONENTS,
                    HBD_COMPONENTS,
                    poly_df,
                    water_pct=sweep_water,
                    temp_C=sweep_temp,
                    freq_us=sweep_freq,
                    time_min=sweep_time,
                    peso_ep=sweep_peso,
                )

            st.success(f"Búsqueda completada — {len(sweep_df)} combinaciones evaluadas")
            st.session_state["sweep_result"] = sweep_df
            st.session_state["sweep_top_n"] = top_n

        if "sweep_result" in st.session_state:
            sweep_df = st.session_state["sweep_result"]
            top_n_ = st.session_state.get("sweep_top_n", top_n)
            top_df = sweep_df.head(top_n_)

            # ── Top N en tarjetas ──
            st.markdown(f"#### Top {top_n_} NADES recomendados")
            medal = ["🥇", "🥈", "🥉"] + [""] * (top_n_ - 3)
            for rank, (_, row) in enumerate(top_df.iterrows()):
                m = medal[rank] if rank < len(medal) else ""
                comb_v = row.get("Combinado (%)", 0)
                ep_v = row.get("EP final (%)", 0)
                nep_v = row.get("NEP final (%)", 0)
                deg_v = row.get("Degrad. T (%)", 0)
                _hba_lbl = row["HBA"].split("(")[0].strip()
                st.markdown(
                    f'<div style="border:1px solid #6b4226;border-radius:8px;padding:.7rem 1rem;'
                    f'margin-bottom:.4rem;background:#fdf8f2">'
                    f"{m} <b>#{rank+1}</b> — "
                    f'<b>{_hba_lbl} : {row["HBD"]}</b> '
                    f'({row["Ratio"]} · {int(sweep_water)}% H₂O · {int(sweep_temp)}°C · {int(sweep_freq)} kHz)<br>'
                    f'🎯 Combinado: <b style="color:#6b4226">{comb_v:.1f}%</b> &nbsp;|&nbsp; '
                    f"🟦 EP: <b>{ep_v:.1f}%</b> &nbsp; 🟥 NEP: <b>{nep_v:.1f}%</b> &nbsp; "
                    f"🌡️ Degrad.T: <b>{deg_v:.1f}%</b>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

            st.markdown("---")

            # ── Gráfico de barras horizontales del Top N ──
            st.markdown("#### Score combinado — Top candidatos")
            fig_sw = go.Figure()
            fig_sw.add_trace(
                go.Bar(
                    y=top_df["NADES"][::-1],
                    x=top_df["EP final (%)"][::-1],
                    name="EP final",
                    orientation="h",
                    marker_color="#2e86ab",
                )
            )
            fig_sw.add_trace(
                go.Bar(
                    y=top_df["NADES"][::-1],
                    x=top_df["NEP final (%)"][::-1],
                    name="NEP final",
                    orientation="h",
                    marker_color="#c44536",
                )
            )
            fig_sw.update_layout(
                barmode="group",
                height=max(350, top_n_ * 28),
                xaxis_title="Índice (%)",
                xaxis_range=[0, 100],
                legend=dict(orientation="h", y=-0.15),
                margin=dict(l=220),
            )
            st.plotly_chart(fig_sw, use_container_width=True)

            # ── Scatter EP vs NEP coloreado por combinado ──
            st.markdown("#### Espacio de búsqueda EP vs NEP")
            fig_sc = px.scatter(
                sweep_df,
                x="EP final (%)",
                y="NEP final (%)",
                color="Combinado (%)",
                size_max=10,
                color_continuous_scale="YlOrBr",
                hover_data=["NADES", "Ratio", "HBA", "HBD", "Degrad. T (%)"],
                labels={
                    "EP final (%)": "EP final tras 3 pasos (%)",
                    "NEP final (%)": "NEP final tras 3 pasos (%)",
                },
            )
            top5 = sweep_df.head(5)
            fig_sc.add_trace(
                go.Scatter(
                    x=top5["EP final (%)"],
                    y=top5["NEP final (%)"],
                    mode="markers+text",
                    marker=dict(
                        size=12, color="gold", symbol="star", line=dict(color="black", width=1)
                    ),
                    text=["#" + str(i + 1) for i in range(len(top5))],
                    textposition="top center",
                    name="Top 5",
                )
            )
            fig_sc.update_layout(height=420)
            st.plotly_chart(fig_sc, use_container_width=True)

            # ── Tabla completa ──
            st.markdown("#### Tabla completa de candidatos")
            cols_sw = [
                c
                for c in [
                    "NADES",
                    "HBA",
                    "HBD",
                    "Ratio",
                    "EP final (%)",
                    "NEP final (%)",
                    "Degrad. T (%)",
                    "Combinado (%)",
                    "Estab. (%)",
                ]
                if c in sweep_df.columns
            ]
            st.dataframe(
                sweep_df[cols_sw]
                .style.background_gradient(subset=["EP final (%)"], cmap="Blues", vmin=0, vmax=100)
                .background_gradient(subset=["NEP final (%)"], cmap="Reds", vmin=0, vmax=100)
                .background_gradient(subset=["Degrad. T (%)"], cmap="Oranges", vmin=0, vmax=20)
                .background_gradient(subset=["Combinado (%)"], cmap="YlOrBr", vmin=0, vmax=100)
                .format(
                    {
                        "EP final (%)": "{:.1f}",
                        "NEP final (%)": "{:.1f}",
                        "Degrad. T (%)": "{:.1f}",
                        "Combinado (%)": "{:.1f}",
                        "Estab. (%)": "{:.1f}",
                    }
                ),
                use_container_width=True,
                hide_index=True,
                height=400,
            )
        else:
            st.info(
                "Ajusta los parámetros y presiona **Ejecutar búsqueda global** para encontrar el NADES óptimo."
            )
            st.markdown("""
            **¿Cómo funciona?**
            - Evalúa todas las combinaciones: 11 HBA × 23 HBD × 3 ratios = **759 combinaciones**
            - Para cada una simula el **Proceso de 3 Pasos** completo (UAE + centrifugación + filtración)
            - **Score combinado** = `peso_EP × EP + peso_NEP × NEP − 0.05 × (EP − NEP)²`
            - La penalización cuadrática premia NADES que equilibran ambas fracciones
            - Ref: Ferrada, C. Tesis Doctoral 2026 — metodología UAE-NADES 3 pasos integrados
            """)


# ══════════════════════════════════════════════════════════
# TAB 8 — METODOLOGÍA
# ══════════════════════════════════════════════════════════
with tab8:
    st.markdown(t("t8_title"))

    # ── Panel de fuente de datos ──
    st.markdown(
        '<div class="part-card" style="background:#f3f6fb;border-color:#2E86AB">'
        '<b style="color:#2E86AB">Fuente de datos: fruto (baya) de '
        "<i>Berberis microphylla</i> G. Forst</b><br>"
        '<small style="color:#0d1f35">'
        f'<b>Compuestos:</b> {(poly_df["tipo"] == "EP").sum()} EP + '
        f'{(poly_df["tipo"] == "NEP").sum()} NEP<br>'
        "<b>EP:</b> Ruiz et al. (2024) Horticulturae 10, 458, Tabla 2 — "
        "cuantificados por HPLC-DAD-ESI-MS/MS<br>"
        "<b>NEP:</b> modelo teórico original de la tesis"
        "</small></div>",
        unsafe_allow_html=True,
    )
    st.markdown("")

    with st.expander("Modelo 1 — Extracción EP (basado en literatura)", expanded=True):
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("""
            **Factores y pesos:**
            | Factor | Peso | Principio |
            |---|---|---|
            | Polaridad | 35% | *Like dissolves like* (ETN) |
            | pH | 30% | Estabilidad estructural por clase |
            | Cap. HBD | 20% | Solvatación de grupos –OH |
            | Viscosidad | 15% | Transferencia de masa |
            | Bonus agua | ≤10% | Óptimo empírico ~25% agua |
            """)
        with col_b:
            st.latex(r"I_{EP} = 0.35 S_p + 0.30 S_{pH} + 0.20 S_{HBD} + 0.15 S_v + B_w")
            st.latex(r"S_p = e^{-\frac{(P_{NADES}-P_{opt})^2}{2\sigma^2}},\quad\sigma=0.08")
            st.latex(r"S_v = \frac{1}{1+\log_{10}(\eta)/4}")

    with st.expander("Modelo 2 — Extracción NEP (NOVEL — sin literatura previa)", expanded=True):
        st.markdown(
            '<div class="novel-badge">Este modelo es una contribución original de esta tesis. '
            "No existe literatura que evalúe NADES para NEP de <em>Berberis microphylla</em>.</div>",
            unsafe_allow_html=True,
        )
        st.markdown("")
        col_c, col_d = st.columns(2)
        with col_c:
            st.markdown("""
            **Factores mecanísticos:**
            | Factor | Peso | Mecanismo |
            |---|---|---|
            | CWP — Penetración pared celular | 20% | PM bajo + baja viscosidad → difusión intracelular |
            | HBD — Disrupción H-bonds | 25% | Compite con sitios de unión proteína-tanino |
            | HP — Hidrólisis | 25% | pH < 3 hidroliza ésteres (t. hidrolizables) |
            | MS — Hinchamiento | 15% | Agua + polaridad swellan la pared celular |
            | SP — Solubilización | 15% | Polaridad del NADES vs. polaridad del NEP |

            **Techo teórico: 78%** — Taninos condensados con enlace C–C interflavánicos
            no son hidrolizables por ningún NADES.
            """)
        with col_d:
            st.latex(
                r"I_{NEP} = (0.20\,CWP + 0.25\,HBD_{dis} + 0.25\,HP + 0.15\,MS + 0.15\,SP)\times 0.80"
            )
            st.latex(r"HP_{hidroliz.} = \max\!\left(0,\;\frac{3.5 - pH}{3.0}\right)")
            st.latex(r"CWP = 0.5\cdot\frac{1}{1+\log_{10}(PM)/\log_{10}200} + 0.5\cdot S_v")

    with st.expander("Modelo 3 — Estabilidad oxidativa en NADES", expanded=True):
        col_e, col_f = st.columns(2)
        with col_e:
            st.markdown("""
            **Mecanismo:** Los NADES forman puentes de H con los grupos –OH fenólicos,
            bloqueando físicamente el acceso del O₂ y radicales libres.
            Componentes ácidos (cítrico, málico) quelan Fe³⁺ → previenen
            oxidación catalítica de Fenton.

            | Factor | Peso | Descripción |
            |---|---|---|
            | Prot. –OH | 30% | cap_HBD / grupos_OH del polifenol |
            | Barrera O₂ | 20% | log(viscosidad) / log(5000) |
            | Antioxid. NADES | 25% | Propiedad intrínseca de los componentes |
            | Estab. pH | 15% | Óptimo por clase (antocianinas: pH < 4) |
            | Estab. Térmica | 10% | Arrhenius simplificado; crítico > 50°C |
            """)
        with col_f:
            st.latex(r"I_{Estab} = 0.30\,HBP + 0.20\,O_2B + 0.25\,AC + 0.15\,pHs + 0.10\,TS")
            st.latex(r"HBP = \min\!\left(1,\;\frac{cap_{HBD}}{n_{OH}}\right)")
            st.latex(r"O_2B = \min\!\left(1,\;\frac{\log_{10}\eta}{\log_{10}5000}\right)")

    with st.expander("Nota científica — Por qué los NADES dan alta estabilidad", expanded=False):
        st.markdown("""
        **Tres mecanismos principales (revisión de literatura):**

        1. **Red supramolecular de H-bonds** (Dai & Verpoorte 2014):
           Los NADES forman una red tridimensional continua de puentes de hidrógeno.
           Esta red rodea físicamente los grupos –OH fenólicos, bloqueando el acceso del O₂
           y radicales libres incluso a concentraciones de agua del 20-40%.

        2. **Reducción del potencial redox de Fe³⁺** (Chanioti & Tzia 2017):
           Los componentes ácidos (cítrico, málico, ascórbico) quelan Fe³⁺ formando
           complejos estables, previniendo la oxidación catalítica de Fenton
           (Fe³⁺ + H₂O₂ → OH• → degradación de polifenoles).

        3. **Exclusión dieléctrica de O₂** (Benvenutti et al. 2019):
           La alta constante dieléctrica del entorno DES (ε >> EtOH) reduce
           la solubilidad del O₂ en el sistema. Menos O₂ disuelto = menos oxidación.

        **Calibración del modelo:** Los índices de estabilidad del simulador están
        calibrados para dar 73-90% para NADES representativos, consistente con:
        - Benvenutti et al. 2019: 80-95% retención de antocianinas con NADES
        - Chanioti & Tzia 2017: 92% retención con ChCl:Ác. Cítrico
        - vs. 60-75% retención con EtOH/MeOH convencional
        """)

    with st.expander("Modelo 4 — Score Combinado EP+NEP (NOVEL)", expanded=True):
        st.markdown(
            '<div class="comb-badge">El score combinado premia NADES que extraen ambas fracciones '
            "simultáneamente. La penalización cuadrática desfavorece NADES que son muy buenos en "
            "una fracción pero malos en la otra.</div>",
            unsafe_allow_html=True,
        )
        st.markdown("")
        col_g, col_h = st.columns(2)
        with col_g:
            st.markdown("""
            **Formulación:**
            - `base = peso_EP × EP + peso_NEP × NEP`
            - `penalización = 0.05 × (EP − NEP)²`
            - `Combinado = base − penalización`

            **Interpretación:**
            - Un NADES con EP=80% y NEP=80% → Combinado ≈ 80%
            - Un NADES con EP=90% y NEP=40% → base=67% pero penalización=12.5 → Combinado≈55%
            - La penalización premia el **equilibrio** sobre la especialización
            """)
        with col_h:
            st.latex(
                r"I_{Comb} = (w_{EP}\cdot I_{EP} + w_{NEP}\cdot I_{NEP}) - 0.05\cdot(I_{EP}-I_{NEP})^2"
            )
            st.latex(r"w_{EP} + w_{NEP} = 1.0,\quad w_{EP} \in [0.30, 0.80]")
            st.markdown(
                "Valor predeterminado: **w_EP = 0.55** (ligeramente sesgado hacia EP por su mayor concentración en la muestra)"
            )

    st.markdown("---")
    st.markdown("#### Relación con los criterios experimentales de selección")
    st.markdown("""
    | Criterio experimental | Índice simulado relacionado |
    |---|---|
    | **TPC** (Folin-Ciocalteu) | EP promedio · NEP parcial (post-hidrólisis) |
    | **TAC** (pH diferencial) | EP de antocianinas · Estabilidad pH |
    | **DPPH / FRAP** | Estabilidad (polifenoles protegidos = mayor actividad retenida) |
    | **Selección óptima** | Score Combinado EP+NEP (maximizar extracción total) |
    """)

    st.markdown("#### Referencias")
    st.markdown("""
    **Fruto — Berberis microphylla:**
    - **Ruiz, A. et al.** (2024). *Horticulturae* 10, 458 — Base de datos EP, 28 compuestos (Tabla 2).
    - Castro-López, C. *et al.* (2016). *J. Funct. Foods*, 24, 455–467 — Perfil polifenólico calafate.

    **Hojas — Berberis spp.:**
    - **Mocan, A. et al.** (2017). *Front. Pharmacol.* 8, 234 — Composición polifenólica hojas.
    - Andola, H.C. et al. (2010). *Pharmacogn. Mag.* 6, 264 — Berberis vulgaris hojas.
    - Kharkwal, H. et al. (2012). *Orient. Pharm. Exp. Med.* 12, 35 — Polifenoles en hojas de Berberis.
    - Biswas, S.K. et al. (2013). *Phytomedicine* 20, 1051 — Revisión comprensiva Berberis.

    **Tallo/Corteza — Berberis spp.:**
    - **Muñoz, O. et al.** (2011). *J. Ethnopharmacol.* 136, 57 — Berberis de Chile (corteza/raíz).
    - Imenshahidi, M. & Hosseinzadeh, H. (2019). *Phytother. Res.* 33, 504 — Revisión berberina y Berberis.

    **Modelos de extracción y estabilidad:**
    - Dai, Y. *et al.* (2013). *Anal. Chim. Acta*, 766, 61–68 — Propiedades DES naturales.
    - Espino, M. *et al.* (2016). *Talanta*, 162, 412–419 — DES para extracción fenólica.
    - Benvenutti, L. *et al.* (2019). *Food Res. Int.*, 119, 710–718 — NADES y antocianinas.
    - Tiwari, B.K. et al. (2010). *Food Res. Int.*, 43, 1956 — UAE y polifenoles.
    - Saura-Calixto, F. et al. (2010). *J. Agric. Food Chem.*, 58, 11932 — Fracción NEP.
    - Chanioti, S. & Tzia, C. (2017). *Food Bioprocess Technol.* 10, 1999 — NADES óptimo.
    - Torskangerpoll, K. & Andersen, Ø.M. (2005). *Food Chem.* 89, 427 — Antocianinas y pH.

    **Modelo novel:**
    - **Ferrada, C.** (2026). Tesis Doctoral, Pontificia Universidad Católica de Valparaíso (PUCV) — Score combinado EP+NEP; modelo NEP; extracción simultánea con NADES; hojas y tallo Berberis.
    """)

    st.markdown("---")

    # ── Modelo 5: Degradación Térmica + Proceso 3 Pasos ──
    with st.expander(
        "Modelo 5 — Degradación Térmica (Arrhenius) + Proceso 3 Pasos", expanded=False
    ):
        col_m5a, col_m5b = st.columns(2)
        with col_m5a:
            st.markdown("""
            **Degradación Térmica — Arrhenius:**
            | Clase | Ea (kJ/mol) | T umbral (°C) |
            |---|---|---|
            | Antocianina | 75 | 45 |
            | Flavonol | 55 | 60 |
            | Flavan-3-ol | 60 | 55 |
            | Ác. Hidroxicinámico | 50 | 65 |
            | Tanino Condensado | 45 | 70 |
            | Tanino Hidrolizable | 42 | 70 |

            **Factor protección NADES:** k × 0.75 (Chanioti & Tzia 2017 — NADES mantiene 92% vs ~70% EtOH)

            **Proceso 3 Pasos (Ferrada 2026):**
            - **Paso 1:** UAE + degradación T → ep_P1 = EP × ret_T
            - **Paso 2:** Centrifugación → ep_P2 = ep_P1 × 0.96 (pérdida <4%)
            - **Paso 3:** Filtración 0.22 μm → sin pérdida si PM < 2000 Da
            """)
        with col_m5b:
            st.latex(
                r"k(T) = k_{ref} \cdot e^{-\frac{E_a}{R}\left(\frac{1}{T_{ref}}-\frac{1}{T}\right)}"
            )
            st.latex(r"k_{NADES}(T) = 0.75 \cdot k(T)")
            st.latex(r"C_{ret}(t) = e^{-k_{NADES} \cdot t}")
            st.latex(r"EP_{P1} = EP_{bruto} \cdot C_{ret}(t_{proc})")
            st.latex(r"NEP_{P1} = NEP_{bruto} \cdot (1 - 0.45 \cdot (1 - C_{ret}))")
            st.caption(
                "NEP más protegido en la matriz → pierde solo 45% de lo que pierde EP · "
                "Ref: Wang & Xu (2007) Food Chem. 101, 1338 · Fang (2011) 129, 267 · "
                "Ferrada, C. Tesis Doctoral 2026"
            )

    # ── Modelo 6: Monte Carlo EP + NEP ──
    st.markdown("---")
    st.markdown("### 🎲 Análisis de Incertidumbre — Monte Carlo (EP + NEP)")
    st.markdown(
        "Estimación de la incertidumbre de los modelos EP y NEP mediante perturbación "
        "aleatoria de los parámetros del NADES. El modelo EP (consolidado en literatura) "
        "tiene menor incertidumbre (±12%) que el modelo NEP (teórico novel, ±20%)."
    )

    mc_col1, mc_col2 = st.columns(2)

    with mc_col1:
        st.markdown("#### Monte Carlo — Modelo EP")
        if st.button("▶ MC EP (400 iteraciones)", key="mc_ep_run"):
            with st.spinner("Simulando 400 perturbaciones EP…"):
                mc_ep = ep_monte_carlo(props, poly_df, n_iter=400, uncertainty=0.12)
            st.session_state["mc_ep_result"] = mc_ep

        if "mc_ep_result" in st.session_state:
            mc_ep = st.session_state["mc_ep_result"]
            if mc_ep["samples"]:
                ep1, ep2, ep3, ep4 = st.columns(4)
                ep1.metric("EP medio", f"{mc_ep['mean']:.1f}%")
                ep2.metric("Desv. std", f"±{mc_ep['std']:.1f}%")
                ep3.metric("IC 90%", f"[{mc_ep['p5']:.1f}–{mc_ep['p95']:.1f}]%")
                ep4.metric("CV", f"{mc_ep['cv']:.1f}%")

                fig_mc_ep = go.Figure()
                fig_mc_ep.add_trace(
                    go.Histogram(
                        x=mc_ep["samples"],
                        nbinsx=30,
                        marker_color="#2e86ab",
                        opacity=0.75,
                        name="Distribución EP (%)",
                    )
                )
                fig_mc_ep.add_vline(
                    x=mc_ep["mean"],
                    line_dash="solid",
                    line_color="#333",
                    annotation_text=f"Media: {mc_ep['mean']:.1f}%",
                )
                fig_mc_ep.add_vrect(
                    x0=mc_ep["p5"],
                    x1=mc_ep["p95"],
                    fillcolor="rgba(46,134,171,0.12)",
                    annotation_text="IC 90%",
                    annotation_position="top left",
                )
                fig_mc_ep.update_layout(
                    height=280,
                    xaxis_title="Índice EP (%)",
                    yaxis_title="Frecuencia",
                    showlegend=False,
                )
                st.plotly_chart(fig_mc_ep, use_container_width=True)
                st.caption(
                    "N=400 · Perturbación ±12%: cap_HBD, pH, viscosidad, polaridad · "
                    "Incertidumbre menor que NEP (modelo más consolidado en literatura) · "
                    "Ref: Espino et al. (2016) Talanta 162, 412"
                )

    with mc_col2:
        st.markdown("#### Monte Carlo — Modelo NEP")
        if st.button("▶ MC NEP (400 iteraciones)", key="mc_nep_run2"):
            with st.spinner("Simulando 400 perturbaciones NEP…"):
                mc_nep2 = nep_monte_carlo(props, poly_df, n_iter=400, uncertainty=0.20)
            st.session_state["mc_nep_result2"] = mc_nep2

        if "mc_nep_result2" in st.session_state:
            mc_nep2 = st.session_state["mc_nep_result2"]
            if mc_nep2["samples"]:
                np1, np2, np3, np4 = st.columns(4)
                np1.metric("NEP medio", f"{mc_nep2['mean']:.1f}%")
                np2.metric("Desv. std", f"±{mc_nep2['std']:.1f}%")
                np3.metric("IC 90%", f"[{mc_nep2['p5']:.1f}–{mc_nep2['p95']:.1f}]%")
                np4.metric("CV", f"{mc_nep2['cv']:.1f}%")

                fig_mc_nep = go.Figure()
                fig_mc_nep.add_trace(
                    go.Histogram(
                        x=mc_nep2["samples"],
                        nbinsx=30,
                        marker_color="#c44536",
                        opacity=0.75,
                        name="Distribución NEP (%)",
                    )
                )
                fig_mc_nep.add_vline(
                    x=mc_nep2["mean"],
                    line_dash="solid",
                    line_color="#333",
                    annotation_text=f"Media: {mc_nep2['mean']:.1f}%",
                )
                fig_mc_nep.add_vrect(
                    x0=mc_nep2["p5"],
                    x1=mc_nep2["p95"],
                    fillcolor="rgba(196,69,54,0.12)",
                    annotation_text="IC 90%",
                    annotation_position="top left",
                )
                fig_mc_nep.update_layout(
                    height=280,
                    xaxis_title="Índice NEP (%)",
                    yaxis_title="Frecuencia",
                    showlegend=False,
                )
                st.plotly_chart(fig_mc_nep, use_container_width=True)
                st.caption(
                    "N=400 · Perturbación ±20%: cap_HBD, cap_HBA, pH, viscosidad, polaridad, antioxidante · "
                    "Mayor incertidumbre (modelo teórico novel sin validación experimental aún) · "
                    "Ref: Saltelli et al. (2004) Sensitivity Analysis in Practice · Ferrada, C. Tesis Doctoral 2026"
                )


# ══════════════════════════════════════════════════════════
# TAB 9 — COMPATIBILIDAD HPTLC
# ══════════════════════════════════════════════════════════
with tab9:
    from tabs.hptlc_tab import render_hptlc

    render_hptlc(props)


# ══════════════════════════════════════════════════════════
# SENSIBILIDAD — cuánto depende el resultado de lo no medido
# ══════════════════════════════════════════════════════════
with atab_sens:
    from tabs.sensibilidad_tab import render_sensibilidad

    # El patrón de referencia real de la literatura de antocianinas: hidroalcohólico
    # acidificado. ETN por las ecuaciones de Spange 2024 (Liquids 4:191).
    _REFERENCIAS_CONVENCIONALES = {
        "EtOH:H₂O 70:30 acidificado": {
            "polaridad": 0.716,
            "pH": 2.5,
            "cap_hbd": 1.58,
            "viscosidad": 2.0,
            "water_pct": 30,
            "water_pct_efectivo": 30,
        },
        "MeOH:H₂O 70:30 acidificado": {
            "polaridad": 0.813,
            "pH": 2.5,
            "cap_hbd": 1.49,
            "viscosidad": 2.0,
            "water_pct": 30,
            "water_pct_efectivo": 30,
        },
    }

    render_sensibilidad(
        {"NADES activo": props, **_REFERENCIAS_CONVENCIONALES},
        poly_df,
    )

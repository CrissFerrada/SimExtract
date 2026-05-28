# 🫐 Simulador NADES — Extracción de Polifenoles  
### *NADES Simulator — Polyphenol Extraction*

**Español 🇨🇱** · [English 🇬🇧](#english-version)

---

> **Beta 0.6** · Tesis Doctoral 2026 · © Cristofher Ferrada · Todos los derechos reservados

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-red?logo=streamlit)](https://streamlit.io/)
[![Versión](https://img.shields.io/badge/Versión-Beta%200.6-green)]()
[![Licencia](https://img.shields.io/badge/Licencia-Propietaria-orange)]()

---

## Descripción

Simulador interactivo para el diseño y evaluación de **Solventes Eutécticos Profundos Naturales (NADES)** aplicados a la extracción de polifenoles de *Berberis microphylla* G. Forst (calafate).

Desarrollado como parte de una **Tesis Doctoral** en la Pontificia Universidad Católica de Valparaíso (PUCV), el simulador integra modelos fisicoquímicos basados en literatura científica indexada con un modelo teórico original para la extracción de Polifenoles No Extraíbles (NEP).

## Funcionalidades principales

| Módulo | Descripción |
|--------|-------------|
| **Diseño de NADES** | 11 HBA × 23 HBD — 759 combinaciones evaluables |
| **Extracción EP** | 28 compuestos (Ruiz et al. 2024) con modelo fisicoquímico |
| **Extracción NEP** | Modelo teórico novel (Ferrada 2026) — sin precedente en literatura |
| **Proceso 3 Pasos** | UAE + centrifugación + filtración — simulación completa paso a paso |
| **Degradación térmica** | Modelo Arrhenius por clase de polifenol con factor protección NADES |
| **UAE (ultrasonido)** | Curva de cavitación 0–100 kHz, óptimo ~20–25 kHz |
| **Recomendador** | Búsqueda global con UAE, temperatura y tiempo como variables |
| **Monte Carlo** | Análisis de incertidumbre para modelos EP y NEP (400 iteraciones) |
| **Cinética + S:L** | Curva de extracción C(t) + optimización sólido:líquido |
| **Diseño Experimental** | Generador Box-Behnken / CCD / Factorial 2ᵏ con descarga CSV |
| **Análisis Económico** | Costo por extracción + reutilización del NADES (ciclos) |
| **Mis Datos** | Importar CSV experimental + Parity Plot + R² vs modelo |
| **Perfiles** | Fruto · Hojas · Tallo/Corteza de *Berberis microphylla* |

## Interfaz — 8 pestañas

```
⚡ Resultados       → Gauges EP/NEP/Estab/Combinado · Tabla · Curva de agua · Excel
🔬 Análisis         → Sub-tabs: EP · NEP · Estabilidad · Interacción NADES-Polifenol
🔊 Proceso UAE      → Curvas UAE · Simulación 3 Pasos · Degradación térmica Arrhenius
📐 Optimización     → Cinética C(t) · Razón S:L · Diseño experimental
💰 Economía         → Costo por extracción · Comparación solventes · Reutilización
📊 Mis Datos        → Importar CSV · Comparar con modelo · Parity Plot
🎯 Recomendador     → Búsqueda global 759 NADES · Cribado Tesis (6 NADES Etapa 1)
📚 Metodología      → Ecuaciones · Referencias · Monte Carlo EP+NEP
```

## Requisitos

- Python 3.10 o superior (recomendado 3.11)
- Dependencias listadas en `requirements.txt`

```
streamlit>=1.35.0
plotly>=5.22.0
pandas>=2.0.0
numpy>=1.26.0
matplotlib>=3.8.0
openpyxl>=3.1.0
```

## Instalación y uso

### Windows (recomendado — sin configuración)

```
Doble clic en:  SimNADES.bat
```

La primera vez instala las dependencias automáticamente (2–5 min). Las siguientes veces abre directamente en el navegador.

> **Sin Python instalado:** ejecuta primero `PREPARAR_BUNDLE_COMPLETO_WINDOWS.bat` para descargar Python embebido (~450 MB, funciona sin internet luego).

### macOS

```bash
chmod +x Lanzar_macOS.command   # solo la primera vez
# Luego: doble clic en Lanzar_macOS.command
```

### Linux

```bash
chmod +x Lanzar_Linux.sh   # solo la primera vez
./Lanzar_Linux.sh
```

### Manual (cualquier plataforma con Python instalado)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Abrir en el navegador: `http://localhost:8501`

## Archivos del proyecto

```
app.py          → Aplicación Streamlit principal (interfaz, gráficos, exportar)
model.py        → Modelos de simulación fisicoquímica (EP, NEP, UAE, Arrhenius, 3 pasos)
data.py         → Base de datos HBA/HBD, THESIS_NADES, perfiles polifenólicos
requirements.txt → Dependencias Python
LEEME.txt       → Guía de usuario completa (Windows/macOS/Linux)

Lanzadores:
  SimNADES.bat                   → Windows
  Lanzar_macOS.command           → macOS
  Lanzar_Linux.sh                → Linux
```

## Fundamento científico

Los modelos implementados están basados en literatura científica indexada:

**Extracción de Polifenoles:**
- Espino et al. (2016) *Talanta* 162, 412-419 — modelo fisicoquímico (polaridad, HBD, pH)
- Ruiz et al. (2024) *Horticulturae* 10(5), 458 — 28 compuestos polifenólicos HPLC-DAD

**Extracción No Extractable (NEP):**
- Ferrada, C. (2026) Tesis Doctoral PUCV — modelo mecanístico novel (sin precedente)
- Saura-Calixto et al. (2010) *J. Agric. Food Chem.* 58(21), 11932-11938 — cuantificación NEP

**Ultrasonido (UAE):**
- Tiwari et al. (2010) *Food Res. Int.* 43(7), 1956-1966 — cavitación acústica
- Mason et al. (2011) *Ultrason. Sonochem.* 18, 226-241 — mecanismos de extracción por UAE

**Degradación Térmica:**
- Wang & Xu (2007) *Food Chem.* 101(4), 1338-1344 — modelo Arrhenius polifenoles
- Buchweitz et al. (2016) *Food Res. Int.* 89, 966-974 — estabilidad térmica compuestos fenólicos

**NADES y Estabilidad:**
- Benvenutti et al. (2019) *Food Res. Int.* 119, 710-718 — NADES y protección antocianinas
- Florindo et al. (2019) *ACS Sustain. Chem. Eng.* 7, 2509-2523 — NADES aplicaciones sostenibles

## Citar este software

Si utilizas este simulador en publicaciones científicas, por favor cita:

> Ferrada, C. (2026). *Simulador NADES para extracción de polifenoles de Berberis microphylla G. Forst* (Beta 0.6) [Software]. Tesis Doctoral, Pontificia Universidad Católica de Valparaíso (PUCV). https://github.com/CrissFerrada/SimNADES

## Autor y licencia

**Autor:** Cristofher Ferrada  
**Contexto:** Tesis Doctoral — Extracción de polifenoles de *Berberis microphylla* G. Forst con NADES  
**Año:** 2026

> ⚠️ Este software es parte de un trabajo de tesis doctoral en desarrollo. Queda prohibida su reproducción, distribución o modificación sin autorización expresa y por escrito del autor.

---

## English version

### Description

Interactive simulator for the design and evaluation of **Natural Deep Eutectic Solvents (NADES)** applied to polyphenol extraction from *Berberis microphylla* G. Forst (calafate berry).

Developed as part of a **PhD thesis** (Pontificia Universidad Católica de Valparaíso - PUCV, 2026). The simulator integrates physicochemical models from indexed scientific literature with a novel theoretical model for Non-Extractable Polyphenol (NEP) extraction — a contribution with no prior literature precedent for this species + NADES combination.

### Key features

- NADES design: 11 HBA × 23 HBD components — 759 evaluable combinations
- EP extraction: 28 compounds (Ruiz et al. 2024) with physicochemical model
- NEP extraction: novel mechanistic model (Ferrada 2026)
- **3-step process simulation:** UAE + centrifugation + 0.22 μm filtration
- Thermal degradation: Arrhenius model per polyphenol class (6 classes, NADES protection factor)
- UAE: cavitation curve 0–100 kHz, optimum ~20–25 kHz
- **Global recommender:** all 759 combinations ranked by combined EP+NEP score
- Monte Carlo uncertainty analysis for both EP and NEP models
- Extraction kinetics C(t) + solid:liquid ratio optimization
- Experimental design generator: Box-Behnken / CCD / Full factorial
- Economic analysis: cost per extraction + NADES reuse cycles
- Import experimental CSV + Parity Plot + R² vs model
- Plant profiles: Fruit · Leaves · Stem/Bark

### Requirements & installation

Requires Python 3.10+ and the packages in `requirements.txt`. On Windows, double-click the `.bat` launcher (installs dependencies automatically). On macOS/Linux, use the corresponding shell script.

```bash
pip install -r requirements.txt
streamlit run app.py
# Open browser at http://localhost:8501
```

### Citation

> Ferrada, C. (2026). *NADES Simulator for polyphenol extraction from Berberis microphylla G. Forst* (Beta 0.6) [Software]. PhD Thesis, Pontificia Universidad Católica de Valparaíso (PUCV). https://github.com/CrissFerrada/SimNADES

### License

© 2026 Cristofher Ferrada. All rights reserved. This software is part of an ongoing doctoral thesis. Reproduction, distribution or modification without explicit written authorization from the author is prohibited.

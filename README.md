# SimExtract

> Tesis Doctoral 2026 · © Cristofher Ferrada · PUCV
> [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

**Simulador interactivo para el diseño y evaluación de Solventes Eutécticos Profundos
Naturales (NADES) aplicados a la extracción de polifenoles de _Berberis microphylla_ G.
Forst.**

SimExtract forma parte del ecosistema de tesis doctoral de Cristofher Ferrada en la Pontificia
Universidad Católica de Valparaíso (PUCV). El software integra modelos fisicoquímicos de
extracción de polifenoles extraíbles (EP), un modelo mecanístico para polifenoles no
extraíbles (NEP), estabilidad térmica, ultrasonido asistido (UAE), análisis económico,
reutilización de NADES y comparación con datos experimentales.

## Statement of need

Natural deep eutectic solvents are increasingly used as greener extraction media for
phenolics, but selecting a practical NADES formulation still requires balancing polarity,
viscosity, pH, hydrogen-bonding capacity, water content, ultrasound conditions, thermal
stability, and cost. SimExtract provides a transparent, reproducible tool for ranking candidate
NADES systems and documenting the assumptions behind extraction decisions before full
laboratory optimization is available.

## Funcionalidades principales

| Módulo | Descripción |
|---|---|
| Diseño de NADES | 14 HBA × 25 HBD con razones molares configurables, incluidos eutécticos hidrofóbicos (HDES) de timol, mentol, alcanfor y ác. decanoico |
| Extracción EP | Modelo fisicoquímico para polifenoles extraíbles |
| Extracción NEP | Modelo mecanístico para polifenoles no extraíbles |
| Proceso UAE | Simulación de ultrasonido, centrifugación y filtración |
| Estabilidad | Modelo Arrhenius con protección por red NADES |
| Optimización | Cinética, razón sólido:líquido y diseños experimentales |
| Economía | Costo por extracción y reutilización del solvente |
| Mis datos | Importación CSV y comparación con el modelo |

## Instalación

```powershell
python -m pip install -r requirements.txt
```

## Uso

```powershell
streamlit run app.py
```

Abrir en el navegador: `http://localhost:8501`.

También se mantienen lanzadores para Windows, macOS y Linux para usuarios no técnicos.

## Verificación

```powershell
python -m black --check app.py model.py data.py tests
python -m ruff check app.py model.py data.py tests
python -m pytest -q
```

## Fundamento científico

Los modelos implementados se apoyan en literatura de NADES, extracción asistida por
ultrasonido, estabilidad de polifenoles, compuestos no extraíbles y perfiles de
_Berberis microphylla_. Las referencias principales para JOSS se listan en `paper.bib`.

## Cómo citar

Ferrada, C. (2026). *SimExtract: SimExtract for polyphenol extraction from Berberis
microphylla G. Forst* (Beta 0.6) [Software]. PhD Thesis, Pontificia Universidad Católica de
Valparaíso (PUCV). https://github.com/CrissFerrada/SimExtract

## Autor y licencia

Autor/Creador: Cristofher Ferrada — Dr(c) en Ciencias mención Química, PUCV.

© 2026 Cristofher Ferrada — Pontificia Universidad Católica de Valparaíso (PUCV).
Licenciado bajo Apache License 2.0. Ver LICENSE.

---

## English version

SimExtract is an interactive simulator for designing and evaluating Natural Deep Eutectic
Solvents (NADES) for polyphenol extraction from _Berberis microphylla_ G. Forst. It supports
NADES formulation, EP/NEP extraction scoring, ultrasound-assisted extraction, thermal
degradation, kinetic exploration, solid:liquid ratio optimization, experimental-design
generation, economic analysis, and comparison with user-supplied experimental data.

### Statement of need

NADES extraction workflows require simultaneous consideration of solvent structure,
hydrogen-bonding capacity, viscosity, pH, added water, temperature, ultrasound conditions,
stability, and cost. SimExtract gives researchers a reproducible decision-support tool for
screening formulations and recording model assumptions before final experimental calibration.

### Installation and use

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

### Tests and formatting

```bash
python -m black --check app.py model.py data.py tests
python -m ruff check app.py model.py data.py tests
python -m pytest -q
```

### License

© 2026 Cristofher Ferrada — Pontificia Universidad Católica de Valparaíso (PUCV).
Licensed under Apache License 2.0. See LICENSE.

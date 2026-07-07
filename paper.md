---
title: "SimNADES: an open simulator for natural deep eutectic solvent design in polyphenol extraction"
tags:
  - chemistry
  - extraction
  - NADES
  - polyphenols
  - green chemistry
  - Berberis microphylla
authors:
  - name: Cristofher Ferrada
    orcid: 0000-0002-1821-9903
    affiliation: 1
affiliations:
  - name: Pontificia Universidad Catolica de Valparaiso, Chile
    index: 1
date: 7 July 2026
bibliography: paper.bib
---

# Summary

SimNADES is an open-source Streamlit application and Python model for exploring
natural deep eutectic solvents (NADES) in the extraction of polyphenols from
*Berberis microphylla* G. Forst. The software combines a curated set of hydrogen
bond acceptor and donor components, physicochemical descriptors, extraction
heuristics, thermal-stability factors, ultrasound-assisted extraction settings,
and a three-step process model to compare candidate solvent systems. It is aimed
at researchers who need a transparent computational companion for planning
laboratory experiments, prioritizing NADES formulations, and documenting the
assumptions behind solvent-selection decisions.

The simulator separates extractable polyphenols (EP), which are represented using
reported calafate phenolic profiles, from non-extractable polyphenols (NEP), which
are modeled as matrix-associated compounds whose recovery depends on solvent
polarity, hydrogen-bonding capacity, viscosity, water fraction, temperature, and
ultrasound conditions [@ruiz2024calafate; @saura2010nep]. Rather than replacing
experimental validation, SimNADES provides a reproducible screening layer for
green-extraction workflows.

# Statement of need

NADES have become important in green analytical chemistry because they can be
prepared from abundant natural compounds and tuned for selective extraction
tasks [@espino2016designer; @dai2013natural]. However, practical formulation
work is often fragmented across spreadsheets, literature notes, and ad-hoc
scripts. This is especially limiting for plant matrices such as calafate, where
phenolic composition, matrix binding, degradation, ultrasound conditions, and
solvent handling all influence the experimental design. SimNADES addresses this
gap by offering a single, inspectable simulator that links solvent composition to
model outputs relevant for EP and NEP recovery.

The software is useful for thesis projects and early-stage method development
because it makes trade-offs visible before expensive or time-consuming laboratory
runs. Users can screen combinations, compare candidate NADES, inspect expected
stability, estimate process behavior, and export tables for downstream reporting.
The open Apache-2.0 license also enables adaptation by other laboratories working
on polyphenols, green solvents, or food and plant matrices.

# Functionality/Implementation

The core implementation is organized around Python modules for data definitions
and model calculations, with a Streamlit interface for interactive exploration.
The model includes component databases for NADES formulation, polyphenol records
for calafate tissues, solvent-property calculations, EP and NEP extraction
scores, thermal-degradation estimates, ultrasound-assisted extraction modifiers,
Monte Carlo uncertainty tools, experimental-design generators, and export
utilities. Automated tests cover the central calculation pathways so that changes
to the model can be checked with `pytest`.

The interface exposes practical controls for hydrogen-bond acceptor and donor
selection, molar ratio, water percentage, temperature, time, ultrasound frequency,
solid-to-liquid ratio, and plant tissue. Results are presented as tables and
plots suitable for comparing solvent candidates, ranking scenarios, and
communicating the assumptions used in a simulation. The code depends on common
scientific Python packages and can be installed from a reproducible
`requirements.txt` file.

# Acknowledgements

This work was developed by Cristofher Ferrada at Pontificia Universidad Catolica
de Valparaiso (PUCV), Chile, in the context of doctoral research on green
extraction strategies for polyphenols from *Berberis microphylla* G. Forst. The
author thanks the academic community whose experimental and methodological work
on NADES, calafate phenolics, ultrasound-assisted extraction, and
non-extractable polyphenols made this simulator possible.

"""Persistent experimental log.

Results used to live in `st.session_state` and died with the session. They now
accumulate on disk so the parity plot grows across sessions and the RP-18
hypothesis can be confronted with what actually happened on the plate.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

RUTA_BITACORA = Path(__file__).parent / "data" / "experimentos.csv"

COLUMNAS = [
    "fecha",
    "NADES",
    "HBA",
    "HBD",
    "Ratio",
    "Agua (%)",
    "Temp (°C)",
    "TPC_exp",
    "placa",
    "siembra_directa_ok",
    "notas",
]


def cargar_bitacora(ruta: Path = RUTA_BITACORA) -> pd.DataFrame:
    """Load the experimental log, returning an empty frame if absent.

    Args:
        ruta: Path to the CSV log.

    Returns:
        The log with `COLUMNAS` as its columns, possibly empty.
    """
    if not ruta.exists():
        return pd.DataFrame(columns=COLUMNAS)
    df = pd.read_csv(ruta)
    for columna in COLUMNAS:
        if columna not in df.columns:
            df[columna] = pd.NA
    return df[COLUMNAS]


def anexar_experimentos(df: pd.DataFrame, ruta: Path = RUTA_BITACORA) -> pd.DataFrame:
    """Append rows to the log and persist it.

    Args:
        df: Rows to append. Missing columns are filled with NA.
        ruta: Path to the CSV log.

    Returns:
        The full log after appending.
    """
    ruta.parent.mkdir(parents=True, exist_ok=True)
    entrante = df.copy()
    for columna in COLUMNAS:
        if columna not in entrante.columns:
            entrante[columna] = pd.NA
    completo = pd.concat([cargar_bitacora(ruta), entrante[COLUMNAS]], ignore_index=True)
    completo.to_csv(ruta, index=False)
    return completo

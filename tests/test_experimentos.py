from pathlib import Path

import pandas as pd

from experimentos import COLUMNAS, anexar_experimentos, cargar_bitacora


def _fila() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "fecha": "2026-09-02",
                "NADES": "ChCl:Ac.Citrico",
                "HBA": "Cloruro de Colina (ChCl)",
                "HBD": "Ácido Cítrico",
                "Ratio": "1:1",
                "Agua (%)": 30,
                "Temp (°C)": 40,
                "TPC_exp": 85.2,
                "placa": "rp18-w-f254s",
                "siembra_directa_ok": True,
                "notas": "sin cola visible",
            }
        ]
    )


def test_bitacora_vacia_devuelve_columnas_esperadas(tmp_path: Path) -> None:
    df = cargar_bitacora(tmp_path / "experimentos.csv")
    assert list(df.columns) == COLUMNAS
    assert df.empty


def test_lo_anexado_sobrevive_a_releer_el_archivo(tmp_path: Path) -> None:
    ruta = tmp_path / "experimentos.csv"
    anexar_experimentos(_fila(), ruta)
    recargado = cargar_bitacora(ruta)
    assert len(recargado) == 1
    assert recargado.iloc[0]["NADES"] == "ChCl:Ac.Citrico"
    assert bool(recargado.iloc[0]["siembra_directa_ok"]) is True


def test_anexar_dos_veces_acumula_no_reemplaza(tmp_path: Path) -> None:
    ruta = tmp_path / "experimentos.csv"
    anexar_experimentos(_fila(), ruta)
    anexar_experimentos(_fila(), ruta)
    assert len(cargar_bitacora(ruta)) == 2

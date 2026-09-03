# -*- coding: utf-8 -*-
"""Tabla de prevalencia en BAYA por grupo conformacional, para el profesor.

Clasifica por evidencia cuantitativa, no por el flag is_major de data.py
(que tiene 4 incoherencias con su propia regla).
"""
import csv
import io
import sys
from pathlib import Path

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent.parent))

from priorizar_conformeros import asignar_grupo, perfil  # noqa: E402
import data as rd  # noqa: E402

# Una estructura puede corresponder a varias entradas del repo (isomeros)
MAPEO = {
    "Quercetín-3-rutinosido (Rutina)": ["Quercetín-3-rutinosido"],
    "Ácido Clorogénico (5-cafeoilquínico)": ["5-Cafeoilquínico (5-CQ)"],
    "3-Cafeoilquínico": ["Cafeoilquínico (CQ)"],
    "4-Cafeoilquínico": ["4-Cafeoilquínico (4-CQ)"],
    "Cafeoilglucárico (isómeros A–D)": [
        "Cafeoilglucárico A (CGI-A)", "Cafeoilglucárico B (CGI-B)",
        "Cafeoilglucárico C (CGI-C)", "Cafeoilglucárico D (CGI-D)"],
    "Dicafeoilglucárico": [
        "Dicafeoilglucárico (DCgluc)", "3,5-Dicafeoilglucárico (3,5-DCQ)",
        "4,5-Dicafeoilglucárico (4,5-DCQ)"],
    "Procianidina B1": ["Proantocianidina B1"],
    "Procianidina B2": ["Proantocianidina B2"],
}
UMBRAL_PRINCIPAL = 1.0  # umol/g peso fresco (maximo observado)


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    df = rd.get_polyphenol_database()
    rep = {r["nombre"]: r for _, r in df.iterrows()}
    filas = []
    for r in csv.DictReader((AQUI / "polifenoles_calafate.csv").open(encoding="utf-8")):
        nombres = MAPEO.get(r["nombre"], [r["nombre"]])
        entradas = [rep[n] for n in nombres if n in rep]
        cuant = [e for e in entradas if e["concentracion_max"] == e["concentracion_max"]]
        if cuant:
            mx = max(e["concentracion_max"] for e in cuant)
            categoria = "Principal" if mx >= UMBRAL_PRINCIPAL else "Minoritario"
            valor = f"{mx:.2f}"
            detalle = (f"{len(cuant)} isómeros cuantificados" if len(cuant) > 1 else "")
        elif r["fuente"] == "Modelo NEP":
            mx, categoria, valor = -1, "Sin cuantificar (NEP)", "—"
            detalle = "fracción no extraíble; sin literatura de cuantificación"
        else:
            mx, categoria, valor = -2, "Identificado, no cuantificado", "—"
            detalle = "asignación por MS; isómero no resuelto"
        filas.append({
            "grupo": asignar_grupo(perfil(r["SMILES_canonico"])),
            "compuesto": r["nombre"], "clase": r["clase"],
            "categoria": categoria, "max_umol_g": valor,
            "fuente": r["fuente"], "detalle": detalle, "_orden": -mx,
        })
    filas.sort(key=lambda x: (x["grupo"], x["_orden"]))
    campos = ["grupo", "compuesto", "clase", "categoria", "max_umol_g", "fuente", "detalle"]
    with (AQUI / "prevalencia_baya.csv").open("w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        wr.writeheader()
        wr.writerows(filas)

    for g in (1, 2, 3):
        sub = [x for x in filas if x["grupo"] == g]
        print(f"\n{'='*100}\nGRUPO {g} — {len(sub)} compuestos\n{'='*100}")
        for x in sub:
            print(f"  {x['compuesto'][:38]:38s} {x['max_umol_g']:>7s}  "
                  f"{x['categoria']:30s} [{x['fuente']}]")
    print(f"\nCSV: {AQUI / 'prevalencia_baya.csv'}")
    print(f"Criterio: principal si el máximo observado ≥ {UMBRAL_PRINCIPAL} µmol/g PF")


if __name__ == "__main__":
    main()

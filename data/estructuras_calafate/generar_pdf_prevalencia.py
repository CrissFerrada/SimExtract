# -*- coding: utf-8 -*-
"""PDF de la tabla de prevalencia en baya, por grupo conformacional.

Uso:  python generar_pdf_prevalencia.py   (requiere prevalencia_baya.csv)
Salida: prevalencia_baya.pdf
"""
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402

AQUI = Path(__file__).parent
UMBRAL = 1.0

COLOR = {
    "Principal": ("#1a5c2a", "#e8f4ec"),
    "Minoritario": ("#8a5a00", "#fdf5e6"),
    "Identificado, no cuantificado": ("#7a2060", "#fbeef6"),
    "Sin cuantificar (NEP)": ("#4a4a4a", "#f0f0f0"),
}
ORDEN_CAT = [
    "Principal",
    "Minoritario",
    "Identificado, no cuantificado",
    "Sin cuantificar (NEP)",
]
TITULO_GRUPO = {
    1: "Grupo 1 — sistemas rígidos",
    2: "Grupo 2 — un azúcar o un éster sobre anillo",
    3: "Grupo 3 — dos azúcares, cadenas abiertas y dímeros",
}
# (campo, x, alineación, ancho máximo en caracteres)
COLS = [
    ("compuesto", 0.055, "left", 34),
    ("clase", 0.425, "left", 19),
    ("max_umol_g", 0.655, "right", 8),
    ("categoria", 0.675, "left", 24),
    ("fuente", 0.945, "right", 15),
]
ENCABEZADOS = ["Compuesto", "Clase", "Máx.", "Categoría", "Fuente"]


def corta(s, n):
    return s if len(s) <= n else s[: n - 1] + "…"


def pagina_grupo(pdf, grupo, filas):
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.text(0.055, 0.955, TITULO_GRUPO[grupo], size=14, weight="bold")
    fig.text(
        0.055,
        0.932,
        f"{len(filas)} compuestos · fruto (baya) de Berberis microphylla G. Forst",
        size=9,
        color="#555",
        style="italic",
    )

    y = 0.890
    fig.text(0.655, y + 0.016, "µmol/g PF", size=6.5, color="#777", ha="right")
    for (_campo, x, ha, _ancho), enc in zip(COLS, ENCABEZADOS):
        fig.text(x, y, enc, size=8, weight="bold", color="#333", ha=ha)
    fig.lines.append(
        plt.Line2D(
            [0.05, 0.95], [y - 0.009, y - 0.009], color="#999", lw=0.8,
            transform=fig.transFigure,
        )
    )

    y -= 0.032
    for fila in filas:
        fg, bg = COLOR[fila["categoria"]]
        fig.patches.append(
            plt.Rectangle(
                (0.05, y - 0.008), 0.90, 0.023, facecolor=bg, edgecolor="none",
                transform=fig.transFigure, zorder=0,
            )
        )
        for campo, x, ha, ancho in COLS:
            resalta = campo in ("categoria", "max_umol_g")
            fig.text(
                x, y, corta(fila[campo], ancho), size=7.6, ha=ha, zorder=1,
                color=fg if resalta else "#111",
                weight="bold" if campo == "categoria" and fila["categoria"] == "Principal" else "normal",
            )
        y -= 0.027

    fig.text(
        0.055, 0.048,
        f"Principal: máximo observado ≥ {UMBRAL} µmol/g de peso fresco.\n"
        "Cuantificación: Ruiz et al. (2024) Horticulturae 10, 458, Tabla 2.\n"
        "Identificado, no cuantificado: asignado por MS sin resolver el isómero.",
        size=7, color="#555", linespacing=1.7, va="bottom",
    )
    pdf.savefig(fig)
    plt.close(fig)


def portada(pdf, filas):
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.text(0.5, 0.90, "Prevalencia en la baya", ha="center", size=24, weight="bold")
    fig.text(0.5, 0.868, "Berberis microphylla G. Forst — fruto", ha="center",
             size=13, style="italic")
    fig.text(0.5, 0.836, "Compuestos por grupo de complejidad conformacional",
             ha="center", size=11, color="#555")

    y = 0.755
    for g in (1, 2, 3):
        sub = [f for f in filas if f["grupo"] == g]
        fig.text(0.10, y, TITULO_GRUPO[g], size=10.5, weight="bold")
        y -= 0.027
        for cat in ORDEN_CAT:
            c = sum(1 for f in sub if f["categoria"] == cat)
            if c:
                fig.text(0.13, y, cat, size=9, color=COLOR[cat][0])
                fig.text(0.66, y, str(c), size=9, color=COLOR[cat][0], ha="right")
                y -= 0.023
        y -= 0.020

    principales = sorted(
        (f for f in filas if f["categoria"] == "Principal"),
        key=lambda f: -float(f["max_umol_g"]),
    )[:5]
    fig.text(0.5, 0.375, "Componentes principales, de mayor a menor", ha="center",
             size=10.5, weight="bold")
    fig.text(
        0.5, 0.348,
        "\n".join(
            f"{f['compuesto']} — {f['max_umol_g']} µmol/g   (grupo {f['grupo']})"
            for f in principales
        ),
        ha="center", va="top", size=9.5, linespacing=1.9,
    )

    fig.text(
        0.5, 0.165,
        "Ninguno de los 7 compuestos del Grupo 1 está cuantificado en la baya:\n"
        "todos caen en la categoría «identificado, no cuantificado».\n"
        "Los componentes principales se concentran en los Grupos 2 y 3.",
        ha="center", va="top", size=9, linespacing=1.8,
        bbox=dict(boxstyle="round,pad=0.8", facecolor="#f4f4f0", edgecolor="#bbb"),
    )
    fig.text(0.5, 0.05, "Cristofher Ferrada · PUCV 2026", ha="center", size=8, color="#666")
    pdf.savefig(fig)
    plt.close(fig)


def main():
    with (AQUI / "prevalencia_baya.csv").open(encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    for f in filas:
        f["grupo"] = int(f["grupo"])

    salida = AQUI / "prevalencia_baya.pdf"
    with PdfPages(salida) as pdf:
        portada(pdf, filas)
        for g in (1, 2, 3):
            pagina_grupo(pdf, g, [f for f in filas if f["grupo"] == g])
        info = pdf.infodict()
        info["Title"] = "Prevalencia de polifenoles en baya de Berberis microphylla"
        info["Author"] = "Cristofher Ferrada — PUCV"

    print(f"PDF: {salida}")


if __name__ == "__main__":
    main()

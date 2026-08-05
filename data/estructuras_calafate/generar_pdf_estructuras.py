# -*- coding: utf-8 -*-
"""Genera un PDF con las estructuras 2D de los polifenoles de calafate.

Uso:  python generar_pdf_estructuras.py
Salida: estructuras_polifenoles_calafate.pdf  +  png/<InChIKey>.png
"""
import csv
import io
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem
from rdkit.Chem.Draw import rdMolDraw2D

RDLogger.DisableLog("rdApp.*")
AQUI = Path(__file__).parent
PNG = AQUI / "png"
PNG.mkdir(exist_ok=True)

ORDEN_CLASES = [
    "Antocianina",
    "Flavonol",
    "Flavona",
    "Flavan-3-ol",
    "Ác. Hidroxicinámico",
    "Ác. Hidroxibenzoico",
    "Tanino Condensado",
    "Alcaloide isoquinolínico",
]
COLS, ROWS = 2, 3
PPP = COLS * ROWS  # estructuras por pagina


def render(smiles: str, ancho: int = 900, alto: int = 700) -> Image.Image:
    """Dibuja la molecula en 2D y devuelve la imagen."""
    m = Chem.MolFromSmiles(smiles)
    AllChem.Compute2DCoords(m)
    d = rdMolDraw2D.MolDraw2DCairo(ancho, alto)
    o = d.drawOptions()
    o.addStereoAnnotation = True  # marca R/S y cis/trans: relevante para COSMO-RS
    o.bondLineWidth = 2
    d.DrawMolecule(rdMolDraw2D.PrepareMolForDrawing(m))
    d.FinishDrawing()
    return Image.open(io.BytesIO(d.GetDrawingText()))


def main() -> None:
    filas = list(csv.DictReader((AQUI / "polifenoles_calafate.csv").open(encoding="utf-8")))
    filas.sort(key=lambda r: (ORDEN_CLASES.index(r["clase"]) if r["clase"] in ORDEN_CLASES else 99,
                              r["nombre"]))

    pdf_path = AQUI / "estructuras_polifenoles_calafate.pdf"
    with PdfPages(pdf_path) as pdf:
        # ── Portada ───────────────────────────────────────────────
        fig = plt.figure(figsize=(8.27, 11.69))  # A4 vertical
        fig.text(0.5, 0.78, "Polifenoles de calafate", ha="center", size=26, weight="bold")
        fig.text(0.5, 0.735, "Berberis microphylla G. Forst", ha="center", size=15, style="italic")
        fig.text(0.5, 0.69, "Estructuras químicas para COSMO-RS", ha="center", size=13)
        n_clases = {}
        for r in filas:
            n_clases[r["clase"]] = n_clases.get(r["clase"], 0) + 1
        y = 0.60
        fig.text(0.5, y, f"{len(filas)} estructuras discretas", ha="center", size=12, weight="bold")
        y -= 0.035
        for c in ORDEN_CLASES:
            if c in n_clases:
                fig.text(0.5, y, f"{c} — {n_clases[c]}", ha="center", size=10.5)
                y -= 0.026
        nota = (
            "Las antocianinas se representan como CATIÓN FLAVILIO (carga +1),\n"
            "que es la especie dominante a pH 2–4 (rango de los NADES de este trabajo).\n\n"
            "Fórmula, peso molecular y carga verificados computacionalmente (RDKit).\n"
            "La estereoquímica NO está verificada: contrastar por InChIKey contra\n"
            "PubChem antes del paso QM.\n\n"
            "Fuente de la lista: Ruiz et al. (2024) Horticulturae 10, 458 (fruto);\n"
            "Mocan et al. (2017) y Muñoz et al. (2011) para hojas y tallo,\n"
            "con asignaciones generalizadas de Berberis spp."
        )
        fig.text(0.5, 0.28, nota, ha="center", va="top", size=9, linespacing=1.6,
                 bbox=dict(boxstyle="round,pad=0.8", facecolor="#f4f4f0", edgecolor="#bbb"))
        fig.text(0.5, 0.05, "Cristofher Ferrada · PUCV 2026 · Simulador NADES",
                 ha="center", size=8, color="#666")
        pdf.savefig(fig)
        plt.close(fig)

        # ── Páginas de estructuras ────────────────────────────────
        for ini in range(0, len(filas), PPP):
            lote = filas[ini:ini + PPP]
            fig, axes = plt.subplots(ROWS, COLS, figsize=(8.27, 11.69))
            axes = axes.ravel()
            for ax in axes:
                ax.axis("off")
            for ax, r in zip(axes, lote):
                img = render(r["SMILES_canonico"])
                img.save(PNG / f"{r['InChIKey']}.png")
                ax.imshow(img)
                carga = int(r["carga_formal"])
                signo = f"  ·  carga {carga:+d}" if carga else ""
                ax.set_title(r["nombre"], size=9.5, weight="bold", pad=4)
                ax.text(0.5, -0.06,
                        f"{r['clase']}  ·  {r['formula']}  ·  {r['MW_calculado']} g/mol{signo}\n"
                        f"{r['parte_planta']}  ·  {r['InChIKey']}",
                        transform=ax.transAxes, ha="center", va="top", size=7, color="#333")
            fig.suptitle("Polifenoles de calafate — estructuras para COSMO-RS",
                         size=9, color="#666", y=0.985)
            fig.text(0.5, 0.012, f"página {ini // PPP + 2}", ha="center", size=7, color="#888")
            fig.tight_layout(rect=[0, 0.02, 1, 0.97])
            pdf.savefig(fig)
            plt.close(fig)

        d = pdf.infodict()
        d["Title"] = "Estructuras de polifenoles de calafate para COSMO-RS"
        d["Author"] = "Cristofher Ferrada — PUCV"
        d["Subject"] = "Berberis microphylla G. Forst — 40 estructuras discretas"

    print(f"PDF: {pdf_path}")
    print(f"PNG individuales: {len(list(PNG.glob('*.png')))} en {PNG}")


if __name__ == "__main__":
    main()

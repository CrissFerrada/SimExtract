# -*- coding: utf-8 -*-
"""PDF de los grupos de complejidad conformacional, con las estructuras dibujadas.

Uso:  python generar_pdf_prioridad.py
Salida: prioridad_conformacional.pdf
"""
import csv
import importlib.util
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI))

from priorizar_conformeros import asignar_grupo, perfil  # noqa: E402

_spec = importlib.util.spec_from_file_location("gpe", AQUI / "generar_pdf_estructuras.py")
_gpe = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_gpe)
render = _gpe.render

COLS, ROWS = 2, 3
PPP = COLS * ROWS

GRUPOS = {
    1: {
        "titulo": "Grupo 1 — sistemas rígidos",
        "criterio": "Agliconas. Sin azúcar ni cadena acilada.\n"
                    "Anillos fusionados; la libertad rotacional se reduce\n"
                    "casi por completo a los hidroxilos.",
        "presupuesto": "20–50 confórmeros · búsqueda rápida",
        "rol": "Validan el flujo completo —geometría, COSMO, parametrización,\n"
               "mezcla de solvente— antes de comprometer cómputo en lo caro.",
        "nota": "",
    },
    2: {
        "titulo": "Grupo 2 — un azúcar o un éster sobre anillo",
        "criterio": "Un fragmento piranósico, o un éster sobre un anillo.\n"
                    "El anillo acota fuertemente el espacio conformacional.",
        "presupuesto": "100–300 confórmeros",
        "rol": "Núcleo del estudio: aquí están los glicósidos mayoritarios\n"
               "del fruto de calafate.",
        "nota": "Los cafeoilquínicos entran acá aunque no tengan azúcar: el anillo\n"
                "de ácido quínico restringe igual que una piranosa.",
    },
    3: {
        "titulo": "Grupo 3 — dos azúcares, cadenas abiertas y dímeros",
        "criterio": "Dos fragmentos de azúcar, poliésteres, polioles de cadena\n"
                    "abierta o dímeros voluminosos.",
        "presupuesto": "500+ confórmeros · exploración sistemática obligatoria",
        "rol": "Último tramo. Fijar el número de confórmeros por convergencia\n"
               "de γ∞, no por presupuesto.",
        "nota": "Dos casos que un conteo de enlaces rotables clasifica mal:\n"
                "• Procianidinas B1/B2 — solo 3 enlaces rotables pesados, pero 42 átomos\n"
                "  y un enlace interflavano de rotación impedida que genera familias\n"
                "  de rotámeros separadas por barreras altas.\n"
                "• Ácido glucárico — es una cadena ABIERTA, no un anillo piranósico:\n"
                "  no restringe nada, es de lo más flexible del conjunto.",
    },
}


def pagina_texto(pdf, titulo, cuerpo, pie="", size_t=20):
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.text(0.5, 0.72, titulo, ha="center", size=size_t, weight="bold", wrap=True)
    fig.text(0.5, 0.62, cuerpo, ha="center", va="top", size=10.5, linespacing=1.8)
    if pie:
        fig.text(0.5, 0.26, pie, ha="center", va="top", size=8.5, linespacing=1.7,
                 bbox=dict(boxstyle="round,pad=0.7", facecolor="#f4f4f0", edgecolor="#bbb"))
    pdf.savefig(fig)
    plt.close(fig)


def main() -> None:
    filas = list(csv.DictReader((AQUI / "polifenoles_calafate.csv").open(encoding="utf-8")))
    datos = []
    for r in filas:
        p = perfil(r["SMILES_canonico"])
        datos.append({**r, **p, "grupo": asignar_grupo(p)})
    datos.sort(key=lambda x: (x["grupo"], x["n_torsiones"], x["MW"]))

    salida = AQUI / "prioridad_conformacional.pdf"
    with PdfPages(salida) as pdf:
        # ── Portada ───────────────────────────────────────────────
        cuentas = {g: sum(1 for d in datos if d["grupo"] == g) for g in (1, 2, 3)}
        cuerpo = (
            "Orden de trabajo para el flujo COSMO-RS\n"
            "de más rígido a más flexible\n\n\n"
            f"Grupo 1 · sistemas rígidos — {cuentas[1]} compuestos\n"
            f"Grupo 2 · un azúcar o un éster sobre anillo — {cuentas[2]} compuestos\n"
            f"Grupo 3 · dos azúcares, cadenas abiertas y dímeros — {cuentas[3]} compuestos"
        )
        pie = (
            "Sobre el conteo de torsiones\n\n"
            "NumRotatableBonds de RDKit NO cuenta los enlaces C–OH, porque el oxígeno\n"
            "es terminal. Para COSMO-RS esa omisión es grave: la orientación de cada\n"
            "hidroxilo define dónde queda el sitio donor/aceptor y cambia el perfil sigma.\n\n"
            "La quercetina tiene 1 enlace rotable pesado y 5 hidroxilos.\n\n"
            "Por eso cada ficha reporta ambas cifras, y el grupo se asigna con la suma.\n"
            "Ni siquiera el Grupo 1 es trivial para COSMO-RS.\n\n"
            "Los presupuestos de confórmeros son órdenes de magnitud para dimensionar,\n"
            "no valores calibrados: fijarlos subiendo confórmeros hasta que γ∞ deje de\n"
            "moverse, en un compuesto de cada grupo."
        )
        pagina_texto(pdf, "Polifenoles de calafate", cuerpo + "\n", pie, size_t=24)

        # ── Por grupo ─────────────────────────────────────────────
        for g in (1, 2, 3):
            meta = GRUPOS[g]
            sub = [d for d in datos if d["grupo"] == g]
            cuerpo = (f"{meta['criterio']}\n\n"
                      f"{len(sub)} compuestos\n\n"
                      f"{meta['presupuesto']}\n\n\n{meta['rol']}")
            pagina_texto(pdf, meta["titulo"], cuerpo, meta["nota"], size_t=17)

            for ini in range(0, len(sub), PPP):
                lote = sub[ini:ini + PPP]
                fig, axes = plt.subplots(ROWS, COLS, figsize=(8.27, 11.69))
                axes = axes.ravel()
                for ax in axes:
                    ax.set_xticks([])
                    ax.set_yticks([])
                    for s in ax.spines.values():
                        s.set_visible(False)
                for ax, d in zip(axes, lote):
                    ax.imshow(render(d["SMILES_canonico"]))
                    ax.set_title(d["nombre"], size=9.5, weight="bold", pad=5)
                    ax.set_xlabel(
                        f"{d['n_torsiones']} torsiones  "
                        f"({d['n_rot_pesados']} rot + {d['n_OH']} OH + {d['n_OMe']} OMe)\n"
                        f"azúcares {d['n_azucares']}  ·  ésteres {d['n_esteres']}  ·  "
                        f"{d['atomos_pesados']} át. pesados  ·  {d['MW']} g/mol\n"
                        f"{d['clase']}",
                        size=6.8, color="#333", linespacing=1.5, labelpad=7)
                for ax in axes[len(lote):]:
                    ax.set_visible(False)
                fig.suptitle(meta["titulo"], size=9, color="#666", y=0.99)
                fig.tight_layout(rect=[0, 0.02, 1, 0.975])
                fig.subplots_adjust(hspace=0.35, wspace=0.05)
                pdf.savefig(fig)
                plt.close(fig)

        info = pdf.infodict()
        info["Title"] = "Prioridad conformacional — polifenoles de calafate para COSMO-RS"
        info["Author"] = "Cristofher Ferrada — PUCV"

    print(f"PDF: {salida}")


if __name__ == "__main__":
    main()

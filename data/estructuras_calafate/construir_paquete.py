# -*- coding: utf-8 -*-
"""Construye el paquete completo: CSV, .smi, SDF 3D y PNG.

Uso:  python construir_paquete.py
Aborta si `generar_estructuras.validar()` reporta cualquier fallo.
"""
import csv
import sys
from pathlib import Path

from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, Descriptors, inchi, rdMolDescriptors

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent.parent))  # raiz del repo, para data.py

from generar_estructuras import ESTRUCTURAS, PROCEDENCIA, validar  # noqa: E402
import data as repo_data  # noqa: E402

RDLogger.DisableLog("rdApp.*")

ALIAS = {
    "Quercetín-3-rutinosido": "Quercetín-3-rutinosido (Rutina)",
    "Rutina": "Quercetín-3-rutinosido (Rutina)",
    "5-Cafeoilquínico (5-CQ)": "Ácido Clorogénico (5-cafeoilquínico)",
    "Ácido Clorogénico": "Ácido Clorogénico (5-cafeoilquínico)",
    "Cafeoilquínico (CQ)": "3-Cafeoilquínico",
    "4-Cafeoilquínico (4-CQ)": "4-Cafeoilquínico",
    "3,5-Dicafeoilglucárico (3,5-DCQ)": "Dicafeoilglucárico",
    "Cafeoilglucárico A (CGI-A)": "Cafeoilglucárico (isómeros A–D)",
    "Cafeoilglucárico B (CGI-B)": "Cafeoilglucárico (isómeros A–D)",
    "Cafeoilglucárico C (CGI-C)": "Cafeoilglucárico (isómeros A–D)",
    "Cafeoilglucárico D (CGI-D)": "Cafeoilglucárico (isómeros A–D)",
    "Dicafeoilglucárico (DCgluc)": "Dicafeoilglucárico",
    "4,5-Dicafeoilglucárico (4,5-DCQ)": "Dicafeoilglucárico",
    "Proantocianidina B1": "Procianidina B1",
    "Proantocianidina B2": "Procianidina B2",
    "Berberina (*alcaloide)": "Berberina (*alcaloide, no polifenol)",
}
SIN_ESTRUCTURA = [
    "Taninos Hidrolizables (totales)",
    "Proantocianidinas poliméricas",
    "Taninos condensados (HMW)",
]


def embed_3d(m):
    """Genera una geometría de partida. ETKDG y, si falla, ETDG (más tolerante
    con cationes aromáticos como el flavilio)."""
    mh = Chem.AddHs(m)
    for params in (AllChem.ETKDGv3(), AllChem.ETDG()):
        params.useRandomCoords = True
        params.randomSeed = 42
        if AllChem.EmbedMolecule(mh, params) == 0:
            AllChem.MMFFOptimizeMolecule(mh, maxIters=400)
            return mh
    return None


def main() -> None:
    fallos = validar(verbose=False)
    if fallos:
        print("ABORTADO — la validación de estructuras falló:")
        for n, p in fallos:
            print(f"  - {n}: {p}")
        sys.exit(1)
    print(f"Validación OK: {len(ESTRUCTURAS)} estructuras\n")

    repo = {}
    for _, r in repo_data.get_polyphenol_database().iterrows():
        repo[r["nombre"]] = {"mw": r["peso_molecular"]}

    png_dir, sdf_dir = AQUI / "png", AQUI / "sdf"
    png_dir.mkdir(exist_ok=True)
    sdf_dir.mkdir(exist_ok=True)
    for viejo in list(sdf_dir.glob("*.sdf")) + list(png_dir.glob("*.png")):
        viejo.unlink()

    filas, avisos, sin_3d = [], [], []
    combinado = Chem.SDWriter(str(AQUI / "polifenoles_calafate_3D.sdf"))

    for nombre, clase, smi, carga, _n_anillos in ESTRUCTURAS:
        m = Chem.MolFromSmiles(smi)
        ikey = inchi.MolToInchiKey(m)
        mw = Descriptors.MolWt(m)

        mw_repo, nombres_repo = None, []
        for nr, info in repo.items():
            if ALIAS.get(nr, nr) == nombre:
                mw_repo = info["mw"]
                nombres_repo.append(nr)
        if mw_repo is not None and abs(mw_repo - mw) > 1.5:
            avisos.append((nombre, mw_repo, round(mw, 2)))

        conf = embed_3d(m)
        if conf is None:
            sin_3d.append(nombre)
        else:
            for k, v in [("clase", clase), ("carga", str(carga)), ("InChIKey", ikey),
                         ("fuente", PROCEDENCIA.get(nombre, "Ruiz 2024"))]:
                conf.SetProp(k, v)
            conf.SetProp("_Name", nombre)
            combinado.write(conf)
            w = Chem.SDWriter(str(sdf_dir / f"{ikey}.sdf"))
            w.write(conf)
            w.close()

        filas.append({
            "nombre": nombre,
            "clase": clase,
            "fuente": PROCEDENCIA.get(nombre, "Ruiz 2024"),
            "nombres_en_repo": "|".join(sorted(nombres_repo)),
            "SMILES_canonico": Chem.MolToSmiles(m),
            "InChIKey": ikey,
            "formula": rdMolDescriptors.CalcMolFormula(m),
            "MW_calculado": round(mw, 2),
            "MW_repo": mw_repo if mw_repo is not None else "",
            "carga_formal": carga,
            "estado_ionico": ("catión flavilio (pH 2–4)" if clase == "Antocianina"
                              else "catión cuaternario" if carga == 1 else "neutro"),
            "archivo_sdf": f"sdf/{ikey}.sdf" if conf is not None else "",
        })

    combinado.close()

    with (AQUI / "polifenoles_calafate.csv").open("w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        wr.writeheader()
        wr.writerows(filas)
    with (AQUI / "polifenoles_calafate.smi").open("w", encoding="utf-8") as f:
        for r in filas:
            f.write(f"{r['SMILES_canonico']}\t{r['nombre']}\n")

    print(f"Estructuras: {len(filas)} · sin 3D: {sin_3d or 'ninguna'}")
    print(f"Entradas poliméricas excluidas: {len(SIN_ESTRUCTURA)}")
    print(f"\nDiscrepancias de MW vs data.py ({len(avisos)}):")
    for n, a, b in avisos:
        print(f"  - {n}: repo {a} vs calculado {b}")
    huerfanos = [n for n in repo if n not in SIN_ESTRUCTURA
                 and ALIAS.get(n, n) not in {e[0] for e in ESTRUCTURAS}]
    print(f"Nombres del repo sin mapear: {huerfanos or 'ninguno'}")


if __name__ == "__main__":
    main()

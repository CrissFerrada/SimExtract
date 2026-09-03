# -*- coding: utf-8 -*-
"""Agrupa las estructuras por complejidad conformacional para el flujo COSMO-RS.

Criterio (de más rígido a más flexible):
  Grupo 1 — agliconas, sin azúcar; poca libertad rotacional
  Grupo 2 — un fragmento de azúcar; el anillo piranósico restringe la exploración
  Grupo 3 — dos azúcares, cadenas aciladas o poliésteres; requiere exploración
            sistemática del espacio conformacional

Sobre el conteo de torsiones
----------------------------
`NumRotatableBonds` de RDKit ignora los enlaces C–OH porque el oxígeno es
terminal. Para COSMO-RS eso subestima el problema: la orientación de cada
hidroxilo cambia dónde queda el sitio donor/aceptor y por tanto el perfil
sigma. Se reportan las dos cifras y el grupo se asigna con la suma.
"""
import csv
import sys
from pathlib import Path

from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors, rdMolDescriptors

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI))
RDLogger.DisableLog("rdApp.*")

# Anillo piranósico saturado (glucosa, galactosa, ramnosa). No matchea el
# anillo C de flavonoides ni el ciclohexano del ácido quínico.
PIRANOSA = Chem.MolFromSmarts("[CX4]1[OX2][CX4][CX4][CX4][CX4]1")
HIDROXILO = Chem.MolFromSmarts("[OX2H]")
METOXI = Chem.MolFromSmarts("[CX4H3][OX2][#6]")
ESTER = Chem.MolFromSmarts("[CX3](=O)[OX2][#6]")


def perfil(smiles: str) -> dict:
    m = Chem.MolFromSmiles(smiles)
    n_rot = rdMolDescriptors.CalcNumRotatableBonds(m)
    n_oh = len(m.GetSubstructMatches(HIDROXILO))
    n_ome = len(m.GetSubstructMatches(METOXI))
    n_azucar = len(m.GetSubstructMatches(PIRANOSA))
    n_ester = len(m.GetSubstructMatches(ESTER))
    return {
        "n_rot_pesados": n_rot,
        "n_OH": n_oh,
        "n_OMe": n_ome,
        "n_torsiones": n_rot + n_oh + n_ome,
        "n_azucares": n_azucar,
        "n_esteres": n_ester,
        "atomos_pesados": m.GetNumHeavyAtoms(),
        "MW": round(Descriptors.MolWt(m), 2),
    }


def asignar_grupo(p: dict) -> int:
    """Grupo por criterio químico; las torsiones lo corroboran.

    Tres casos que un conteo de enlaces rotables por sí solo clasifica mal:

    - Dímeros tipo procianidina: solo 3 enlaces rotables pesados, pero 42
      átomos y un enlace interflavano cuya rotación está impedida y genera
      familias de rotámeros separadas por barreras altas. No es una búsqueda
      barata aunque el conteo lo sugiera.
    - Ácido glucárico: es una cadena ABIERTA, no un anillo piranósico. No
      restringe nada; al contrario, es de lo más flexible del conjunto.
    - Cafeoilquínicos: un éster sobre un anillo de ácido quínico. El anillo
      acota igual que una piranosa, así que van con los monoglicósidos.
    """
    poliol_abierto = p["n_azucares"] == 0 and p["n_OH"] >= 6 and p["n_rot_pesados"] >= 6
    if (p["n_azucares"] >= 2 or p["n_esteres"] >= 2 or poliol_abierto
            or (p["n_azucares"] == 1 and p["n_esteres"] >= 1)
            or p["atomos_pesados"] >= 40):
        return 3
    if p["n_azucares"] == 1 or p["n_esteres"] == 1:
        return 2
    return 1


# Presupuesto sugerido de búsqueda conformacional por grupo
PRESUPUESTO = {
    1: "20–50 confórmeros · búsqueda rápida basta",
    2: "100–300 confórmeros · el anillo piranósico acota el espacio",
    3: "500+ confórmeros · exploración sistemática obligatoria",
}


def main() -> None:
    filas = list(csv.DictReader((AQUI / "polifenoles_calafate.csv").open(encoding="utf-8")))
    out = []
    for r in filas:
        p = perfil(r["SMILES_canonico"])
        g = asignar_grupo(p)
        out.append({"grupo": g, "nombre": r["nombre"], "clase": r["clase"],
                    "InChIKey": r["InChIKey"], **p})
    out.sort(key=lambda x: (x["grupo"], x["n_torsiones"], x["MW"]))

    campos = ["grupo", "nombre", "clase", "n_azucares", "n_esteres", "n_rot_pesados",
              "n_OH", "n_OMe", "n_torsiones", "atomos_pesados", "MW", "InChIKey"]
    with (AQUI / "prioridad_conformacional.csv").open("w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        wr.writeheader()
        wr.writerows(out)

    for g in (1, 2, 3):
        sub = [x for x in out if x["grupo"] == g]
        print(f"\n{'='*94}\nGRUPO {g} — {len(sub)} compuestos · {PRESUPUESTO[g]}\n{'='*94}")
        print(f"{'compuesto':40s} {'azuc':>4s} {'est':>4s} {'rot':>4s} {'OH':>3s} "
              f"{'OMe':>4s} {'tors':>5s} {'pesados':>8s} {'MW':>8s}")
        for x in sub:
            print(f"{x['nombre'][:40]:40s} {x['n_azucares']:4d} {x['n_esteres']:4d} "
                  f"{x['n_rot_pesados']:4d} {x['n_OH']:3d} {x['n_OMe']:4d} "
                  f"{x['n_torsiones']:5d} {x['atomos_pesados']:8d} {x['MW']:8.2f}")
    print(f"\nCSV: {AQUI / 'prioridad_conformacional.csv'}")


if __name__ == "__main__":
    main()

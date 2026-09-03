# -*- coding: utf-8 -*-
"""Estructuras de polifenoles de calafate para COSMO-RS.

IMPORTANTE — números de cierre de anillo
----------------------------------------
Los fragmentos reutilizables se insertan dentro de plantillas mientras los
anillos de la plantilla siguen ABIERTOS. Si un fragmento reusa el mismo número
de cierre que la plantilla, el SMILES cierra el anillo contra el átomo
equivocado y produce un macrociclo con la misma fórmula molecular. El peso
molecular NO detecta ese error.

Por eso cada fragmento tiene su propio rango de numeración (%10–%16 azúcares,
%80 anillo B, %90–%93 núcleos) y `validar()` comprueba tamaño y número de
anillos, que sí es sensible a la conectividad.
"""

# ── Azúcares (numeración propia %10–%16) ──────────────────────────
GLC = "O[C@@H]%10O[C@H](CO)[C@@H](O)[C@H](O)[C@H]%10O"        # beta-D-glucopiranosilo
GAL = "O[C@@H]%11O[C@H](CO)[C@H](O)[C@H](O)[C@H]%11O"         # beta-D-galactopiranosilo
RHA = "O[C@H]%12O[C@@H](C)[C@H](O)[C@H](O)[C@H]%12O"          # alfa-L-ramnopiranosilo
RUT = ("O[C@@H]%13O[C@H](CO[C@@H]%14O[C@@H](C)[C@H](O)[C@H](O)[C@H]%14O)"
       "[C@@H](O)[C@H](O)[C@H]%13O")                          # rutinosilo (6-O-alfa-L-Rha-beta-D-Glc)
MAL_GLC = "O[C@@H]%15O[C@H](COC(=O)CC(=O)O)[C@@H](O)[C@H](O)[C@H]%15O"   # 6''-malonil-Glc
MAL_GAL = "O[C@@H]%16O[C@H](COC(=O)CC(=O)O)[C@H](O)[C@H](O)[C@H]%16O"    # 6''-malonil-Gal

# ── Anillo B (numeración %80) ─────────────────────────────────────
B_CY = "c%80ccc(O)c(O)c%80"          # cianidina / quercetina    3',4'-diOH
B_DP = "c%80cc(O)c(O)c(O)c%80"       # delfinidina               3',4',5'-triOH
B_PN = "c%80ccc(O)c(OC)c%80"         # peonidina / isorhamnetina 3'-OMe,4'-OH
B_PT = "c%80cc(O)c(O)c(OC)c%80"      # petunidina                3'-OMe,4',5'-diOH
B_MV = "c%80cc(OC)c(O)c(OC)c%80"     # malvidina                 3',5'-diOMe,4'-OH
B_KA = "c%80ccc(O)cc%80"             # kaempferol                4'-OH


def flavylium(b, r3="O"):
    """Catión flavilio 3,5,7-trisustituido. Núcleo en %90/%91."""
    return f"Oc%90cc(O)c%91cc({r3})c([o+]c%91c%90)-{b}"


def flavonol(b, r3="O"):
    """3-hidroxiflavona (flavonol) 5,7-diOH. Núcleo en %92/%93."""
    return f"O=c%92c({r3})c(-{b})oc%93cc(O)cc(O)c%92%93"


# (nombre, clase, SMILES, carga formal, n_anillos esperado)
ESTRUCTURAS = [
    # ── ANTOCIANINAS (catión flavilio, pH 2-4) ─────────────────────
    ("Delfinidin-3-glucósido",  "Antocianina", flavylium(B_DP, GLC), 1, 4),
    ("Delfinidin-3-rutinosido", "Antocianina", flavylium(B_DP, RUT), 1, 5),
    ("Cianidín-3-glucósido",    "Antocianina", flavylium(B_CY, GLC), 1, 4),
    ("Cianidín-3-rutinosido",   "Antocianina", flavylium(B_CY, RUT), 1, 5),
    ("Petunidín-3-glucósido",   "Antocianina", flavylium(B_PT, GLC), 1, 4),
    ("Petunidín-3-rutinosido",  "Antocianina", flavylium(B_PT, RUT), 1, 5),
    ("Peonidín-3-glucósido",    "Antocianina", flavylium(B_PN, GLC), 1, 4),
    ("Peonidín-3-rutinosido",   "Antocianina", flavylium(B_PN, RUT), 1, 5),
    ("Malvidín-3-glucósido",    "Antocianina", flavylium(B_MV, GLC), 1, 4),
    ("Malvidín-3-rutinosido",   "Antocianina", flavylium(B_MV, RUT), 1, 5),

    # ── FLAVONOLES ────────────────────────────────────────────────
    ("Quercetín-3-rutinosido (Rutina)", "Flavonol", flavonol(B_CY, RUT), 0, 5),
    ("Quercetín-3-galactosido",         "Flavonol", flavonol(B_CY, GAL), 0, 4),
    ("Quercetín-3-glucósido",           "Flavonol", flavonol(B_CY, GLC), 0, 4),
    ("Quercetín-3-malonilgalactosido",  "Flavonol", flavonol(B_CY, MAL_GAL), 0, 4),
    ("Quercetín-3-malonilglucósido",    "Flavonol", flavonol(B_CY, MAL_GLC), 0, 4),
    ("Isorhamnetín-3-rutinosido",       "Flavonol", flavonol(B_PN, RUT), 0, 5),
    ("Isorhamnetín-3-galactosido",      "Flavonol", flavonol(B_PN, GAL), 0, 4),
    ("Quercetín-3-rhamnosido",          "Flavonol", flavonol(B_CY, RHA), 0, 4),
    ("Kaempferol-3-glucósido",          "Flavonol", flavonol(B_KA, GLC), 0, 4),
    ("Quercetina",                      "Flavonol", flavonol(B_CY, "O"), 0, 3),
    ("Isorhamnetina",                   "Flavonol", flavonol(B_PN, "O"), 0, 3),

    # ── FLAVONAS ──────────────────────────────────────────────────

    # ── FLAVAN-3-OLES ─────────────────────────────────────────────
    ("Catequina",    "Flavan-3-ol", "O[C@H]1Cc2c(O)cc(O)cc2O[C@@H]1c1ccc(O)c(O)c1", 0, 3),
    ("Epicatequina", "Flavan-3-ol", "O[C@@H]1Cc2c(O)cc(O)cc2O[C@@H]1c1ccc(O)c(O)c1", 0, 3),

    # ── ACIDOS HIDROXICINAMICOS ───────────────────────────────────
    ("Ácido Cafeico",  "Ác. Hidroxicinámico", "OC(=O)/C=C/c1ccc(O)c(O)c1", 0, 1),
    ("Ácido Ferúlico", "Ác. Hidroxicinámico", "OC(=O)/C=C/c1ccc(O)c(OC)c1", 0, 1),
    ("Ácido Clorogénico (5-cafeoilquínico)", "Ác. Hidroxicinámico",
     "O[C@@H]1C[C@](O)(C(=O)O)C[C@H](OC(=O)/C=C/c2ccc(O)c(O)c2)[C@@H]1O", 0, 2),
    ("3-Cafeoilquínico", "Ác. Hidroxicinámico",
     "O[C@@H]1C[C@](O)(C(=O)O)C[C@H](O)[C@H]1OC(=O)/C=C/c1ccc(O)c(O)c1", 0, 2),
    ("4-Cafeoilquínico", "Ác. Hidroxicinámico",
     "O[C@H]1C[C@](O)(C(=O)O)C[C@H](O)[C@@H]1OC(=O)/C=C/c1ccc(O)c(O)c1", 0, 2),
    ("Cafeoilglucárico (isómeros A–D)", "Ác. Hidroxicinámico",
     "OC(=O)[C@H](O)[C@@H](O)[C@H](O)[C@@H](OC(=O)/C=C/c1ccc(O)c(O)c1)C(=O)O", 0, 1),
    ("Dicafeoilglucárico", "Ác. Hidroxicinámico",
     "OC(=O)[C@H](O)[C@@H](OC(=O)/C=C/c1ccc(O)c(O)c1)[C@H](O)[C@@H](OC(=O)/C=C/c1ccc(O)c(O)c1)C(=O)O", 0, 2),

    # ── ACIDOS HIDROXIBENZOICOS ───────────────────────────────────
    ("Ácido Elágico",        "Ác. Hidroxibenzoico", "O=c1oc2c(O)c(O)cc3c(=O)oc4c(O)c(O)cc1c4c23", 0, 4),

    # ── TANINOS CONDENSADOS (dímeros discretos) ───────────────────
    ("Procianidina B1", "Tanino Condensado",
     "O[C@@H]1[C@H](c2ccc(O)c(O)c2)Oc2cc(O)cc(O)c2[C@H]1[C@@H]1[C@H](O)[C@@H](c2ccc(O)c(O)c2)Oc2cc(O)cc(O)c21", 0, 6),
    ("Procianidina B2", "Tanino Condensado",
     "O[C@H]1[C@H](c2ccc(O)c(O)c2)Oc2cc(O)cc(O)c2[C@H]1[C@@H]1[C@@H](O)[C@H](c2ccc(O)c(O)c2)Oc2cc(O)cc(O)c21", 0, 6),

]


FUENTE = {
    "Ruiz 2024": "Ruiz et al. (2024) Horticulturae 10, 458, Tabla 2 — cuantificado en fruto",
    "Molecules 2019": "Molecules 24, 3331 — identificado en fruto; isómero no resuelto",
    "JChromA 2013": "J. Chromatogr. A 1281, 38 — cuantificado en fruto",
    "Modelo NEP": "Modelo teórico de la tesis; sin literatura previa Berberis + NADES",
}
# Compuestos que NO están en Ruiz 2024 y entran por otra fuente de fruto
PROCEDENCIA = {
    "Catequina": "Molecules 2019", "Epicatequina": "Molecules 2019",
    "Quercetina": "Molecules 2019", "Isorhamnetina": "Molecules 2019",
    "Kaempferol-3-glucósido": "Molecules 2019",
    "Ácido Cafeico": "Molecules 2019", "Ácido Ferúlico": "JChromA 2013",
    "Procianidina B1": "Modelo NEP", "Procianidina B2": "Modelo NEP",
    "Ácido Elágico": "Modelo NEP",
}


def validar(verbose=True):
    """Verifica parseo, carga, tamaño de anillo y número de anillos.

    El chequeo de anillos es el que detecta colisiones de numeración: un
    macrociclo espurio conserva la fórmula pero cambia tamaño y conteo.
    """
    from rdkit import Chem, RDLogger
    from rdkit.Chem import Descriptors, rdMolDescriptors

    RDLogger.DisableLog("rdApp.*")
    fallos = []
    for nombre, _clase, smi, carga, n_anillos in ESTRUCTURAS:
        m = Chem.MolFromSmiles(smi)
        if m is None:
            fallos.append((nombre, "no parsea"))
            continue
        ri = m.GetRingInfo().AtomRings()
        tam_max = max((len(r) for r in ri), default=0)
        q = Chem.GetFormalCharge(m)
        problemas = []
        if q != carga:
            problemas.append(f"carga {q} != {carga}")
        if tam_max > 6:
            problemas.append(f"anillo de {tam_max} miembros (¿colisión de numeración?)")
        if len(ri) != n_anillos:
            problemas.append(f"{len(ri)} anillos != {n_anillos} esperados")
        if problemas:
            fallos.append((nombre, "; ".join(problemas)))
        if verbose:
            estado = "OK" if not problemas else "FALLA: " + "; ".join(problemas)
            print(f"{nombre[:40]:40s} {rdMolDescriptors.CalcMolFormula(m):20s} "
                  f"{Descriptors.MolWt(m):8.2f} {len(ri):2d} anillos  {estado}")
    return fallos


if __name__ == "__main__":
    fallos = validar()
    print(f"\n{len(ESTRUCTURAS)} estructuras · {len(fallos)} con problema")
    for n, p in fallos:
        print(f"  - {n}: {p}")

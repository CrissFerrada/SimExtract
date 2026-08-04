# -*- coding: utf-8 -*-
"""Genera y verifica las estructuras de polifenoles de calafate para COSMO-RS."""

# Fragmentos reutilizables
GLC = "O[C@@H]1O[C@H](CO)[C@@H](O)[C@H](O)[C@H]1O"          # beta-D-glucopiranosilo
GAL = "O[C@@H]1O[C@H](CO)[C@H](O)[C@H](O)[C@H]1O"           # beta-D-galactopiranosilo
RHA = "O[C@H]1O[C@@H](C)[C@H](O)[C@H](O)[C@H]1O"            # alfa-L-ramnopiranosilo
RUT = "O[C@@H]1O[C@H](CO[C@@H]2O[C@@H](C)[C@H](O)[C@H](O)[C@H]2O)[C@@H](O)[C@H](O)[C@H]1O"
MAL_GLC = "O[C@@H]1O[C@H](COC(=O)CC(=O)O)[C@@H](O)[C@H](O)[C@H]1O"   # 6''-malonil-glucosilo
MAL_GAL = "O[C@@H]1O[C@H](COC(=O)CC(=O)O)[C@H](O)[C@H](O)[C@H]1O"    # 6''-malonil-galactosilo

# Nucleo flavilio: aglicona con sustituyente en C3 -> {r3}, anillo B -> {b}
def flavylium(b, r3="O"):
    return f"Oc1cc(O)c2cc({r3})c([o+]c2c1)-{b}"

B_CY = "c1ccc(O)c(O)c1"          # cianidina   3',4'-diOH
B_DP = "c1cc(O)c(O)c(O)c1"       # delfinidina 3',4',5'-triOH
B_PN = "c1ccc(O)c(OC)c1"         # peonidina   3'-OMe,4'-OH
B_PT = "c1cc(O)c(O)c(OC)c1"      # petunidina  3'-OMe,4',5'-diOH
B_MV = "c1cc(OC)c(O)c(OC)c1"     # malvidina   3',5'-diOMe,4'-OH

# Nucleo flavonol (3-hidroxiflavona): sustituyente en C3 -> {r3}
def flavonol(b, r3="O"):
    return f"O=c1c({r3})c(-{b})oc2cc(O)cc(O)c12"

B_QU = "c1ccc(O)c(O)c1"          # quercetina    3',4'-diOH
B_IR = "c1ccc(O)c(OC)c1"         # isorhamnetina 3'-OMe,4'-OH
B_KA = "c1ccc(O)cc1"             # kaempferol    4'-OH

CAFEOIL = "C(=O)/C=C/c1ccc(O)c(O)c1"   # acilo cafeoilo

ESTRUCTURAS = [
    # ── ANTOCIANINAS (cation flavilio, pH 2-4) ─────────────────────
    ("Delfinidin-3-glucósido",  "Antocianina", flavylium(B_DP, GLC), 1),
    ("Delfinidin-3-rutinosido", "Antocianina", flavylium(B_DP, RUT), 1),
    ("Cianidín-3-glucósido",    "Antocianina", flavylium(B_CY, GLC), 1),
    ("Cianidín-3-rutinosido",   "Antocianina", flavylium(B_CY, RUT), 1),
    ("Petunidín-3-glucósido",   "Antocianina", flavylium(B_PT, GLC), 1),
    ("Petunidín-3-rutinosido",  "Antocianina", flavylium(B_PT, RUT), 1),
    ("Peonidín-3-glucósido",    "Antocianina", flavylium(B_PN, GLC), 1),
    ("Peonidín-3-rutinosido",   "Antocianina", flavylium(B_PN, RUT), 1),
    ("Malvidín-3-glucósido",    "Antocianina", flavylium(B_MV, GLC), 1),
    ("Malvidín-3-rutinosido",   "Antocianina", flavylium(B_MV, RUT), 1),

    # ── FLAVONOLES ────────────────────────────────────────────────
    ("Quercetín-3-rutinosido (Rutina)", "Flavonol", flavonol(B_QU, RUT), 0),
    ("Quercetín-3-galactosido",         "Flavonol", flavonol(B_QU, GAL), 0),
    ("Quercetín-3-glucósido",           "Flavonol", flavonol(B_QU, GLC), 0),
    ("Quercetín-3-malonilgalactosido",  "Flavonol", flavonol(B_QU, MAL_GAL), 0),
    ("Quercetín-3-malonilglucósido",    "Flavonol", flavonol(B_QU, MAL_GLC), 0),
    ("Isorhamnetín-3-rutinosido",       "Flavonol", flavonol(B_IR, RUT), 0),
    ("Isorhamnetín-3-galactosido",      "Flavonol", flavonol(B_IR, GAL), 0),
    ("Quercetín-3-rhamnosido",          "Flavonol", flavonol(B_QU, RHA), 0),
    ("Kaempferol-3-glucósido",          "Flavonol", flavonol(B_KA, GLC), 0),
    ("Quercetina",                      "Flavonol", flavonol(B_QU, "O"), 0),
    ("Isorhamnetina",                   "Flavonol", flavonol(B_IR, "O"), 0),

    # ── FLAVONAS ──────────────────────────────────────────────────
    ("Luteolina", "Flavona", "O=c1cc(-c2ccc(O)c(O)c2)oc2cc(O)cc(O)c12", 0),
    ("Vitexina",  "Flavona",
     "O=c1cc(-c2ccc(O)cc2)oc2c(-[C@@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)c(O)cc(O)c12", 0),

    # ── FLAVAN-3-OLES ─────────────────────────────────────────────
    ("Catequina",    "Flavan-3-ol", "O[C@H]1Cc2c(O)cc(O)cc2O[C@@H]1c1ccc(O)c(O)c1", 0),
    ("Epicatequina", "Flavan-3-ol", "O[C@@H]1Cc2c(O)cc(O)cc2O[C@@H]1c1ccc(O)c(O)c1", 0),

    # ── ACIDOS HIDROXICINAMICOS ───────────────────────────────────
    ("Ácido Cafeico",  "Ác. Hidroxicinámico", "OC(=O)/C=C/c1ccc(O)c(O)c1", 0),
    ("Ácido Ferúlico", "Ác. Hidroxicinámico", "OC(=O)/C=C/c1ccc(O)c(OC)c1", 0),
    ("Ácido Clorogénico (5-cafeoilquínico)", "Ác. Hidroxicinámico",
     "O[C@@H]1C[C@](O)(C(=O)O)C[C@H](OC(=O)/C=C/c2ccc(O)c(O)c2)[C@@H]1O", 0),
    ("3-Cafeoilquínico", "Ác. Hidroxicinámico",
     "O[C@@H]1C[C@](O)(C(=O)O)C[C@H](O)[C@H]1OC(=O)/C=C/c1ccc(O)c(O)c1", 0),
    ("4-Cafeoilquínico", "Ác. Hidroxicinámico",
     "O[C@H]1C[C@](O)(C(=O)O)C[C@H](O)[C@@H]1OC(=O)/C=C/c1ccc(O)c(O)c1", 0),
    ("3,5-Dicafeoilquínico", "Ác. Hidroxicinámico",
     "O[C@@H]1[C@@H](OC(=O)/C=C/c2ccc(O)c(O)c2)C[C@](O)(C(=O)O)C[C@H]1OC(=O)/C=C/c1ccc(O)c(O)c1", 0),
    # Cafeoilglucaricos: acido glucarico esterificado con cafeoilo (isomeros A-D
    # difieren solo en la posicion del acilo; se emiten como un unico constitucional)
    ("Cafeoilglucárico (isómeros A–D)", "Ác. Hidroxicinámico",
     "OC(=O)[C@H](O)[C@@H](O)[C@H](O)[C@@H](OC(=O)/C=C/c1ccc(O)c(O)c1)C(=O)O", 0),
    ("Dicafeoilglucárico", "Ác. Hidroxicinámico",
     "OC(=O)[C@H](O)[C@@H](OC(=O)/C=C/c1ccc(O)c(O)c1)[C@H](O)[C@@H](OC(=O)/C=C/c1ccc(O)c(O)c1)C(=O)O", 0),

    # ── ACIDOS HIDROXIBENZOICOS ───────────────────────────────────
    ("Ácido Gálico",         "Ác. Hidroxibenzoico", "OC(=O)c1cc(O)c(O)c(O)c1", 0),
    ("Ácido Protocatéquico", "Ác. Hidroxibenzoico", "OC(=O)c1ccc(O)c(O)c1", 0),
    ("Ácido Vanílico",       "Ác. Hidroxibenzoico", "OC(=O)c1ccc(O)c(OC)c1", 0),
    ("Ácido Elágico",        "Ác. Hidroxibenzoico", "O=c1oc2c(O)c(O)cc3c(=O)oc4c(O)c(O)cc1c4c23", 0),

    # ── TANINOS CONDENSADOS (dimeros discretos) ───────────────────
    ("Procianidina B1", "Tanino Condensado",
     "O[C@@H]1[C@H](c2ccc(O)c(O)c2)Oc2cc(O)cc(O)c2[C@H]1[C@@H]1[C@H](O)[C@@H](c2ccc(O)c(O)c2)Oc2cc(O)cc(O)c21", 0),
    ("Procianidina B2", "Tanino Condensado",
     "O[C@H]1[C@H](c2ccc(O)c(O)c2)Oc2cc(O)cc(O)c2[C@H]1[C@@H]1[C@@H](O)[C@H](c2ccc(O)c(O)c2)Oc2cc(O)cc(O)c21", 0),

    # ── ALCALOIDE (no polifenol; se incluye por estar en tallo) ────
    ("Berberina (*alcaloide, no polifenol)", "Alcaloide isoquinolínico",
     "COc1ccc2cc3[n+](cc2c1OC)CCc1cc2OCOc2cc1-3", 1),
]

if __name__ == "__main__":
    from rdkit import Chem
    from rdkit.Chem import Descriptors, rdMolDescriptors

    print(f"{'compuesto':42s} {'formula':22s} {'MW':>8s}  carga  estado")
    malos = 0
    for nombre, clase, smi, carga in ESTRUCTURAS:
        m = Chem.MolFromSmiles(smi)
        if m is None:
            print(f"{nombre:42s} {'--':22s} {'--':>8s}   ERROR DE PARSEO")
            malos += 1
            continue
        f = rdMolDescriptors.CalcMolFormula(m)
        mw = Descriptors.MolWt(m)
        q = Chem.GetFormalCharge(m)
        ok = "OK" if q == carga else f"CARGA {q} != {carga}"
        if q != carga:
            malos += 1
        print(f"{nombre:42s} {f:22s} {mw:8.2f}  {q:+d}     {ok}")
    print(f"\nTotal: {len(ESTRUCTURAS)} estructuras, {malos} con problema")

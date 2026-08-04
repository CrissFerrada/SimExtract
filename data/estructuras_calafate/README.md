# Estructuras de polifenoles de calafate — entrada para COSMO-RS

Estructuras químicas de los polifenoles reportados en literatura para
*Berberis microphylla* G. Forst (calafate), en formato utilizable por un flujo COSMO-RS.

**Generado:** 2026-08-04 · **Fuente de la lista de compuestos:** `data.py` de este repositorio
(fruto, hojas y tallo) · **Herramienta:** RDKit 2026.03.3

---

## Contenido

| Archivo | Qué es |
|---|---|
| `polifenoles_calafate.csv` | Tabla maestra: nombre, clase, parte de planta, SMILES canónico, InChIKey, fórmula, MW, carga formal, estado iónico |
| `polifenoles_calafate.smi` | SMILES + nombre, una línea por compuesto |
| `polifenoles_calafate_3D.sdf` | Todas las estructuras en un solo SDF con coordenadas 3D |
| `sdf/<InChIKey>.sdf` | Una estructura por archivo, nombrada por InChIKey |

**40 estructuras discretas**, cubriendo las siete clases: antocianinas, flavonoles, flavonas,
flavan-3-oles, ácidos hidroxicinámicos, ácidos hidroxibenzoicos y proantocianidinas
(dímeros). Se incluye además berberina, marcada explícitamente como alcaloide y no polifenol,
por estar reportada en tallo.

---

## Lee esto antes de correr nada

### 1. Estado de protonación — es la decisión que más afecta el resultado

**Las antocianinas están como catión flavilio (carga +1).** A pH 2–4, que es el rango de los
NADES de este trabajo, el flavilio es la especie dominante. Las antocianinas interconvierten
entre flavilio (catiónico), base quinoidal (neutra), hemicetal y chalcona según el pH; si las
modelas como neutras, el perfil sigma no corresponde a la especie que realmente tienes en
solución, y todo lo que construyas encima hereda el error.

Los **ácidos fenólicos** están en forma **neutra**. A pH 3 es razonable (pKa 4.2–4.5 para los
hidroxicinámicos, ~4.4 para el gálico), pero si vas a modelar a pH más alto tienes que generar
las formas desprotonadas.

La columna `estado_ionico` del CSV indica la especie de cada estructura.

### 2. Lo que está verificado y lo que no

**Verificado computacionalmente:** que cada SMILES parsea, su fórmula molecular, su peso
molecular y su carga formal. Esto atrapa errores de constitución.

**NO verificado:** la **estereoquímica**. El peso molecular no distingue glucósido de
galactósido, ni catequina de epicatequina. Para COSMO-RS la estereoquímica sí importa, porque
cambia la geometría y con ella el perfil sigma.

**Antes del paso QM, verifica cada estructura por su InChIKey contra PubChem.** El InChIKey
está en el CSV justamente para que la verificación sea una búsqueda y no una inspección visual
de SMILES. Prioriza los azúcares (glucósido/galactósido/ramnósido) y los flavan-3-oles
(catequina/epicatequina y los dímeros B1/B2), que es donde un error estereoquímico es más
probable y más costoso.

### 3. Las geometrías 3D son de partida, no un ensemble conformacional

Los SDF traen **un confórmero** por molécula (ETKDG + optimización MMFF ligera). Sirve como
geometría inicial, no como resultado.

Los glicósidos de este conjunto son muy flexibles: rutinósidos y dicafeoil-derivados tienen
decenas de confórmeros accesibles a temperatura ambiente. **COSMO-RS promedia sobre un
ensemble conformacional ponderado por Boltzmann**, así que la búsqueda conformacional es parte
del cálculo y hay que hacerla en tu propio flujo, no darla por hecha con estos archivos.

### 4. Flujo COSMO-RS esperado

Las parametrizaciones estándar de COSMOtherm (familia `BP_TZVP_C3x`) esperan archivos COSMO
generados con un nivel de teoría específico. Sustituirlo por otro invalida la parametrización:

1. Búsqueda conformacional desde estas geometrías
2. Optimización de cada confórmero con COSMO
3. *Single point* BP86 / def-TZVP con COSMO (ε = ∞) → archivo `.cosmo`
4. COSMOtherm con la parametrización que corresponda al nivel usado

Para las **especies cargadas** (10 antocianinas + berberina), revisa cómo trata tu
parametrización a los iones: el coeficiente de actividad de un ion aislado no es directamente
comparable con el de un neutro, y según lo que quieras predecir puede requerir tratar el par
iónico.

---

## Entradas excluidas

Tres entradas de `data.py` **no tienen estructura discreta** y no se pueden llevar a COSMO-RS:

| Entrada | PM en repo | Motivo |
|---|---|---|
| Taninos Hidrolizables (totales) | 1200 | Mezcla polimérica |
| Proantocianidinas poliméricas | 2500 | Mezcla polimérica |
| Taninos condensados (HMW) | 4000 | Mezcla polimérica |

No se les inventó un representante. Si necesitas incluirlas en el cálculo, la práctica
defendible es declarar un **oligómero proxy** —procianidina B2 para los condensados, ácido
elágico para los hidrolizables— y decir explícitamente que es un proxy, no la especie real.
Ambos ya están en el conjunto como estructuras propias.

---

## Discrepancias detectadas contra `data.py`

La verificación cruzada encontró dos pesos moleculares inconsistentes en el repositorio.
**No se corrigieron en `data.py`**; se reportan aquí para que decidas:

| Compuesto | PM en `data.py` | PM calculado | Fórmula |
|---|---|---|---|
| Cafeoilglucárico (A–D) | 370.3 | **372.28** | C15H16O11 |
| Dicafeoilglucárico | 516.4 | **534.43** | C24H22O14 |

Un éster cafeoílico del ácido glucárico da C15H16O11 = 372.28 (glucárico C6H10O8 + cafeico
C9H8O4 − H2O). El valor 516.4 del dicafeoilglucárico corresponde exactamente al
**dicafeoilquínico** (C25H24O12 = 516.45), lo que sugiere que en algún momento se copió el peso
del derivado quínico al glucárico.

Refuerza esa sospecha que la entrada `4,5-Dicafeoilglucárico (4,5-DCQ)` lleva el nombre
"glucárico" con la abreviatura "DCQ", que es la de los dicafeoilquínicos. Vale la pena volver a
Ruiz et al. (2024) Tabla 2 y confirmar cuál de los dos es.

Los cafeoilglucáricos A–D son **isómeros posicionales** del mismo constitucional: difieren solo
en qué hidroxilo del ácido glucárico lleva el acilo. Se emitió **una** estructura para los
cuatro. Si tu estudio necesita distinguirlos, hay que fijar la posición del acilo en cada uno,
y esa asignación tiene que salir del artículo original, no de un modelo.

---

## Referencias de la lista de compuestos

- Ruiz et al. (2024) *Horticulturae* 10, 458 — 28 compuestos en fruto por HPLC-DAD-ESI-MS/MS
- Mocan et al. (2017) *Front. Pharmacol.* — hojas, *Berberis* spp.
- Muñoz et al. (2011) *J. Ethnopharmacol.* — tallo/corteza, *Berberis* spp.
- Biswas et al. (2013) — flavan-3-oles en hojas

Las asignaciones de hojas y tallo son **generalizadas de *Berberis* spp.**, no específicas de
*B. microphylla*; así están anotadas en `data.py` y esa limitación se traslada a este conjunto.

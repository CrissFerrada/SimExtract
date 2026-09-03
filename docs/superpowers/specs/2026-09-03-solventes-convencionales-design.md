# Familia de solventes convencionales

**Proyecto:** SimExtract — Tesis Doctoral PUCV 2026
**Fecha:** 2026-09-03
**Estado:** diseño aprobado, pendiente de plan de implementación
**Autor del diseño:** Cristofher Ferrada (con Claude Code)

---

## 1. El hueco que cierra

SimExtract no puede responder hoy la pregunta que un revisor hace primero:

> ¿Es mejor que **etanol:agua 70:30 acidificado**?

Toda tesis de química verde se sostiene sobre la misma afirmación —*tan bueno como el
convencional, pero más verde*— y el programa no conoce ningún solvente convencional. No
puede probar ni la mitad de esa frase. **Esto no es ampliar alcance: es agregar el control
que falta.**

Hay además un segundo pago, y conecta con el módulo HPTLC: un solvente convencional **es
volátil**, así que no deja matriz en el origen y su veredicto HPTLC sale favorable. El
programa mostraría entonces la tensión real del trabajo en una sola pantalla — *el NADES
extrae mejor y es verde, pero cobra el paso analítico; el hidroalcohólico siembra limpio
pero es tóxico*. Hoy solo se ve la mitad favorable.

## 2. Por qué es barato

El motor de extracción ya es agnóstico al solvente. `ep_extraction_score` consume
exactamente cinco magnitudes:

| Consume | Definida para cualquier solvente |
|---|---|
| `polaridad` | Sí — ETN de Reichardt |
| `pH` | Sí |
| `cap_hbd` | Sí — conteo de sitios donadores |
| `viscosidad` | Sí |
| `water_pct_efectivo` | Sí |

Lo específico de NADES está encapsulado en `calculate_nades_properties()`: las reglas de
mezcla, el bonus eutéctico y la saturación de agua del HDES.

**Entonces esto es añadir una segunda capa de entrada que produzca el mismo diccionario,
no reescribir el modelo.**

## 3. Regla de construcción

La misma que gobierna el módulo HPTLC, y se reutiliza su registro `evidencia.py`:

> Cada valor emitido debe tener fuente verificable. Donde no exista, se declara el vacío y
> **no se emite número**.

Insignias `MEDIDO` / `INFERIDO` / `SIN_FUENTE` como en `hptlc.py`.

## 4. Lo que la literatura establece

### 4.1 La escala de polaridad 🟩

ET(30) de Reichardt, normalizada a **ETN** con agua = 1,000 y tetrametilsilano = 0,000. Es
la escala empírica estándar, medida por solvatocromismo del colorante betaína 30. Hay
valores publicados para 84 solventes y remedidos para 186 más.

### 4.2 La polaridad de las mezclas **no es lineal** 🟩

Spange, S. (2024). *Polarity of Organic Solvent/Water Mixtures Measured with Reichardt's
B30 and Related Solvatochromic Probes — A Critical Review.* Liquids 4(1):191-230.
DOI [10.3390/liquids4010010](https://doi.org/10.3390/liquids4010010)

La relación ET(30) frente a la fracción molar de agua **da una línea curva**, tanto para
metanol/agua como para etanol/agua y etilenglicol/agua. La causa es solvatación
preferencial: en alcoholes acuosos la sonda es solvatada preferentemente **por el alcohol**.

Consecuencia directa: un EtOH:H₂O 70:30 se comporta más parecido al etanol de lo que su
30 % de agua sugeriría. **Promediar linealmente sobreestimaría la polaridad de todos los
hidroalcohólicos y los rankearía mal frente a los NADES** — justo el resultado que la tesis
quiere defender.

### 4.3 Capacidad donadora de puente de hidrógeno 🟩

El parámetro α de Kamlet-Taft mide acidez donadora de puente de H, que es la magnitud
análoga a `cap_hbd`. Se registra por solvente **como descriptor documentado de contraste**,
no como entrada del motor (ver §6.2).

### 4.4 Verdor 🟩

`SimEluent/data/solventes.csv` ya trae puntaje CHEM21 para 13 solventes convencionales. Se
reutiliza en vez de duplicarlo.

## 5. Decisiones tomadas

### 5.1 Solo valores medidos, sin interpolar

Las mezclas se registran **por composición concreta y con su valor publicado**
(EtOH:H₂O 50/70/80, MeOH:H₂O 50/70/80…). Una composición sin valor tabulado **no se
interpola**: se declara vacío y el solvente no se puede seleccionar en ella.

Es la única opción que no inventa números, y es coherente con la regla de §3.

### 5.2 La regla lineal del agua en NADES también se revisa

`calculate_nades_properties()` usa hoy:

```python
pol_eff = pol_neat * (1 - w) + 1.0 * w   # ETN(agua) = 1.0
```

Es la misma simplificación que §4.2 documenta como incorrecta en mezclas acuosas.

**Se revisa, pero de forma auditable.** La regla de mezcla pasa a ser un parámetro
seleccionable y versionado (`REGLA_MEZCLA = "lineal" | "solvatacion_preferencial"`), con la
lineal como valor por defecto inicial. Motivo: cambiarla mueve todos los resultados
previos, y el autor debe poder comparar antes/después en vez de que los números se le
desplacen en silencio.

Cada resultado guardado en la bitácora registra con qué regla se calculó.

**Limitación honesta:** los estudios de solvatación preferencial son con la sonda betaína
en mezclas binarias. Extenderlos a NADES + agua **no está establecido**. La regla no lineal
para NADES sale marcada `INFERIDO`, no `MEDIDO`.

## 6. Arquitectura

Archivo nuevo `solventes.py`, hermano de `hptlc.py`. No importa Streamlit.

```
solventes.py
├── Solvente(NamedTuple)        # nombre, familia, ETN, alfa_kt, hbd, viscosidad, pH, verdor
├── SOLVENTES: dict[str, Solvente]
├── MEZCLAS: dict[str, Mezcla]  # composiciones con ETN medido
├── ACIDIFICADOS: dict[...]     # los patrones reales (§6.3)
└── propiedades_convencional(...) -> dict   # mismo dict que calculate_nades_properties
```

`propiedades_convencional()` devuelve **exactamente las mismas claves** que
`calculate_nades_properties()`, de modo que todo lo posterior —EP, NEP, estabilidad,
ultrasonido, cinética, proceso 3 pasos, economía, HPTLC— funciona sin tocarse.

### 6.1 Claves que devuelve

Las mismas, con dos honestas en cero: `antioxidant_nades = 0.0` (un solvente convencional
no aporta protección antioxidante) y `bifasico = False`.

### 6.2 El mapeo que **no** se hace

`cap_hbd` en el modelo actual es un **conteo entero de sitios donadores** (ChCl 2,
prolina 3). Kamlet-Taft α es continuo y adimensional (agua ≈ 1,17). Mapear uno al otro
requeriría una constante inventada que distorsionaría todo el ranking.

**Se cuenta igual que en los NADES:** agua 2, metanol 1, etanol 1, acetona 0,
acetonitrilo 0, acetato de etilo 0, ácido fórmico 1, ácido acético 1. α queda registrado
por solvente como contraste documentado.

### 6.3 Los acidificados son el patrón real

No basta con metanol puro. La literatura de antocianinas usa sistemas acidificados, y esos
son la referencia contra la que hay que comparar. Entran como entradas propias con su pH
medido, no como un solvente más con un pH inventado.

## 7. Vacíos declarados

| Vacío | Por qué |
|---|---|
| ⬜ Composiciones sin ETN publicado | No se interpolan (§5.1) |
| ⬜ Regla no lineal aplicada a NADES | Solvatación preferencial no está establecida para NADES + agua |
| ⬜ NEP sobre solventes convencionales | Se calcula pero sale marcado **extrapolación sin validar**: el modelo NEP es aporte original calibrado con NADES |
| ⬜ Viscosidad de mezclas a temperatura | Requiere valores por composición y temperatura |

## 8. Alcance

**Entra:** `solventes.py`, la tabla con sus fuentes, los acidificados, la regla de mezcla
versionada, y que el selector de la interfaz permita elegir familia (NADES o convencional)
alimentando el mismo motor.

**No entra:** técnicas de extracción más allá del ultrasonido que ya existe (fase C), ni
variables de proceso nuevas (fase D).

## 9. Criterios de aceptación

1. `propiedades_convencional()` devuelve el mismo conjunto de claves que
   `calculate_nades_properties()`, verificado por prueba.
2. Un solvente convencional recorre EP, NEP, estabilidad, cinética, proceso y HPTLC sin
   que ninguna de esas funciones se modifique.
3. Ninguna composición sin ETN publicado es seleccionable.
4. NEP sobre convencional sale siempre marcado como extrapolación.
5. El veredicto HPTLC de un hidroalcohólico es más favorable que el de un NADES
   equivalente, y el motivo citado es la volatilidad.
6. La regla de mezcla queda registrada en cada resultado guardado.

## 10. Dependencia externa

Los valores de ETN por composición están en Spange (2024), §4.2. **MDPI bloquea la descarga
automática**, así que el PDF lo aporta el autor desde su acceso institucional. Hasta
entonces la tabla de mezclas queda vacía y declarada como tal — el resto del módulo se
construye y se prueba igual.

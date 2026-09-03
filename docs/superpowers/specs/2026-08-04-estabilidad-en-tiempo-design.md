# Módulo de Estabilidad en el Tiempo (almacenamiento)

**Proyecto:** SimExtract — Tesis Doctoral PUCV 2026
**Fecha:** 2026-08-04
**Estado:** diseño aprobado, pendiente de plan de implementación
**Autor del diseño:** Cristofher Ferrada (con Claude Code)

---

## 1. Contexto y problema

El simulador modela hoy tres cosas: cuánto se extrae (EP/NEP), cuánto se degrada
térmicamente **durante** la extracción (minutos), y un índice instantáneo de protección
del solvente. No modela nada en escala de **días a meses**.

Esa es justamente la escala que gobierna el trabajo real: entre la extracción y el
análisis HPTLC pasan días, y los polifenoles mayoritarios de *Berberis microphylla*
—antocianinas 3-glicosiladas **no aciladas**— son los más lábiles de la fracción fenólica.

Hay además una razón de fondo, propia de este trabajo: **el NADES fue elegido como
sustituto de la atmósfera inerte**. El laboratorio no dispone de línea de N₂, y la
hipótesis de trabajo es que la red supramolecular del solvente provee por sí sola la
protección frente a oxidación que normalmente se obtiene purgando con gas inerte. El
módulo debe cuantificar esa hipótesis, no solo producir curvas.

## 2. Decisiones que el módulo debe responder

1. **Ventana analítica** — "extraído hoy, ¿hasta qué día puedo correr el HPTLC?"
2. **Elección de solvente** — vida útil como criterio adicional en el ranking de NADES.
3. **Protocolo de almacenamiento** — qué temperatura, qué exclusión de luz, qué headspace.
4. **Argumento de tesis** — cuánta atmósfera inerte sustituye el NADES.
5. **Descongelación** — a qué temperatura descongelar una muestra congelada para que llegue
   al HPTLC con la mayor retención posible.

Las cuatro primeras son consultas distintas sobre una misma curva
`retención(t | solvente, condiciones)`. La quinta integra esa misma cinética sobre una
trayectoria térmica en vez de a temperatura constante (§6.1).

## 3. Alcance

**Dentro:** cinética de degradación por compuesto durante almacenamiento; efecto de
temperatura, luz, headspace y solvente; cinética integrada sobre la trayectoria de
descongelación; calibración con datos experimentales propios; cinco vistas en la app.

**Fuera (por ahora):** modelo de vías competitivas oxidación/hidrólisis con balance de masa
entre especies y predicción del *cambio de perfil* (aparición de bandas de aglicona). Es la
evolución natural del módulo, y se decide **después** de tener el módulo de compatibilidad
HPTLC. Ver §11.

## 4. Prerrequisito — corrección de `thermal_degradation()`

`model.py:1123` calcula la constante de velocidad como

```python
k_T = p["k_ref"] * np.exp(-p["Ea"] / R * (1.0 / T_ref - 1.0 / T_K))
```

El paréntesis está invertido para una constante de velocidad: produce que `k` **disminuya**
al subir la temperatura. Verificado numéricamente (antocianina, 30 min): 0.080 % de
degradación a 25 °C, 0.030 % a 60 °C, 0.000 % a 95 °C. Es la causa de que la columna
`Degrad. T (%)` salga 0.0 en todo el barrido de `sweep_all_nades`.

La forma correcta es

```python
k_T = p["k_ref"] * np.exp(-p["Ea"] / R * (1.0 / T_K - 1.0 / T_ref))
```

Nota: la misma expresión con el paréntesis en el orden actual es **correcta** en
`calculate_nades_properties` para la viscosidad, porque la viscosidad sí decrece con la
temperatura. No debe "corregirse" ahí.

**Consecuencia:** al invertir el signo, los `k_ref` actuales quedan sobredimensionados —
fueron ajustados para dar salidas plausibles bajo el signo equivocado. Con el `k_ref` actual
corregido, las antocianinas darían t½ ≈ 8 min a 95 °C. Hay que **recalibrar `k_ref` por clase**
contra vidas medias térmicas de literatura antes de dar por cerrado el arreglo.

Este trabajo es prerrequisito porque el módulo nuevo comparte la tabla de `Ea` (§5.3).

## 5. Núcleo cinético

### 5.1 Ecuación de retención

Primer orden con fracción residual:

```
(1)   C(t)/C₀ = C_res + (1 − C_res) · exp(−k · t)          t en días
```

Colapsa a primer orden puro cuando `C_res = 0`. La fracción residual representa la
subpoblación estabilizada por acilación y copigmentación, que la literatura de
almacenamiento observa sistemáticamente como plateau y que el primer orden puro no
reproduce (predice retención → 0).

### 5.2 Descomposición de la constante de velocidad

```
(2)   k = k_clase · f_est · f_T · f_solv · f_luz · f_O₂
```

`k_clase` en d⁻¹, definida a 25 °C, oscuridad, aire, en solución hidroalcohólica de
referencia (etanol 70 %).

### 5.3 Factor estructural

```
(3)   f_est = f_OH · f_gli
(4)   f_OH  = (oh_groups / oh_ref,clase)^0.5
(5)   f_gli = 1.0  si glicosilado
              2.5  si aglicona
```

`f_OH` separa delfinidina (3 OH en anillo B, lábil) de malvidina (2 metoxilos, estable);
ambas son mayoritarias en calafate, de modo que la distinción es observable. `f_gli`
refleja que el azúcar en C-3 bloquea la apertura del anillo a chalcona.

`oh_groups` ya existe en las tres bases de polifenoles. **`glicosilado` es un campo nuevo**
y debe agregarse explícitamente: no se puede derivar del nombre con seguridad, porque
"Rutina" y "Vitexina" son glicósidos sin sufijo delator y un regex sobre el nombre fallaría
en silencio en dos compuestos abundantes.

### 5.4 Factor de temperatura

```
(6)   f_T = exp(−Ea/R · (1/T − 1/T_ref))        T_ref = 298.15 K
```

`Ea` por clase se toma de la **tabla compartida** con `thermal_degradation()` (§4). Un único
valor de energía de activación por clase en todo el simulador; dos valores distintos para la
misma antocianina serían una incoherencia interna atacable en la defensa.

Rango de validez y regímenes: §6.

### 5.5 Factor de solvente

No se vuelve a modelar la protección del solvente. Se reutiliza `stability_score()`, que ya
integra capacidad HBD, viscosidad, capacidad antioxidante y pH:

```
(7)   S      = stability_score(props, poly, temp_C = 25).total
(8)   f_solv = exp(−γ · (S − S_ref))
```

Calibrado con `S_ref = 0.50` (≈ etanol acuoso) → `f_solv = 1.0`, y `γ` tal que
ChCl:Ác. Málico (S ≈ 0.78) dé `f_solv ≈ 0.45`.

**Restricción crítica de implementación:** `stability_score()` contiene internamente un
término térmico (`ts`). Debe invocarse **fijo a 25 °C** para que la dependencia con la
temperatura viva únicamente en `f_T` (ec. 6). En caso contrario la temperatura entra dos
veces y el modelo es incoherente.

### 5.6 Factores ambientales

```
(9)    f_luz ∈ { luz_ambiente: 2.2 , vial_ambar: 1.3 , oscuridad_total: 1.0 }
(10)   f_O₂  ∈ { aire_headspace: 1.00 , headspace_minimo: 0.75 , inerte: 0.45 }
```

`f_luz` depende de clase; las antocianinas son las más fotolábiles y llevan el coeficiente
más alto.

Sobre los niveles de luz: papel aluminio y una pieza opaca impresa en 3D son
**fotoquímicamente equivalentes** (ambas son exclusión total) y entran como el mismo nivel
`oscuridad_total`. La pieza impresa aporta reproducibilidad entre viales, no atenuación
adicional; modelarla como un nivel distinto sería precisión falsa.

Sobre el oxígeno: `headspace_minimo` (llenar el vial al ras) es la única palanca de oxígeno
disponible sin equipamiento y el módulo debe recomendarla explícitamente. `inerte` se
implementa desde el inicio aunque el laboratorio no disponga de N₂, porque es el término de
referencia de la métrica de §7.

### 5.7 Fracción residual

`C_res` por clase. Antocianinas bajo (≈ 0.10) porque las de calafate son mayoritariamente
**no aciladas** (Ruiz et al. 2024); flavonoles y taninos en 0.30–0.35.

**`C_res` es el parámetro peor sustentado del módulo** y es el objetivo número uno de la
calibración experimental. Debe aparecer así etiquetado en las salidas.

## 6. Regímenes de temperatura

Arrhenius no es extrapolable a temperatura criogénica. Tres regímenes:

| Régimen | Rango | Tratamiento |
|---|---|---|
| Ambiente / refrigeración | 25 °C, 4 °C | Arrhenius (ec. 6). Terreno sólido, es donde está la literatura. |
| Congelación | −20 °C | Arrhenius **con bandera de riesgo** (ver abajo) |
| Ultracongelación | −80 °C | Por debajo de T_g: régimen detenido, limitado por difusión |

**Riesgo de crioconcentración.** Los NADES del proyecto llevan 20–30 % de agua. Si esa agua
cristaliza, el soluto se concentra en la fase líquida remanente y la degradación puede
**acelerarse** respecto a 4 °C. Si en cambio el sistema vitrifica —comportamiento habitual en
NADES, y la razón por la que los azúcares son crioprotectores clásicos— la degradación se
frena bruscamente. Cuál de las dos ocurre depende de la composición y no es predecible con
confianza desde primeros principios.

El módulo emite bandera explícita cuando `water_pct > 20` y `T < 0 °C`:
*"−20 °C puede ser peor que 4 °C en este sistema; verificar experimentalmente antes de
adoptarlo como protocolo."*

**T_g.** Campo por sistema, estimado por composición. Es, junto con `C_res`, **el parámetro
más débil del módulo**, y el candidato natural a medición por DSC. No se consignan valores
de T_g de NADES específicos como si estuvieran establecidos. Por debajo de T_g el módulo
reporta *"degradación detenida, limitada por difusión"* con una cota, no una cifra de
retención con decimales.

**Ciclos congelación–descongelación.** Término discreto aparte: almacenar a −20 °C y analizar
cinco veces son cinco ciclos, y esa pérdida no aparece en ninguna curva continua. La pérdida
por ciclo **no es una constante** sino el resultado de integrar la cinética a lo largo de la
trayectoria térmica de descongelación (§6.1).

### 6.1 Descongelación

Pregunta operativa: descongelar a temperatura ambiente, a 4 °C o a 10 °C, ¿cuál conserva más
analito para el HPTLC? Tiene un óptimo real y no monótono, por dos efectos que empujan en
sentido contrario.

**Trayectoria térmica** (enfriamiento/calentamiento newtoniano):

```
(11)   T(t) = T_ext − (T_ext − T₀) · exp(−t/τ)
```

`τ` es la constante de tiempo térmica del vial: depende de masa, geometría y medio. Aire
quieto es lento (decenas de minutos para un vial de 2 mL); baño de agua es un orden de
magnitud más rápido. `τ` es parámetro de entrada, medible con un termopar en un vial testigo.

**Pérdida durante la descongelación:**

```
(12)   pérdida = 1 − exp( −∫₀^t_eq k(T(t)) · f_cc(T(t)) dt )
```

Integrada numéricamente por trapecio sobre la trayectoria (numpy, sin dependencia nueva).

**`f_cc` — factor de crioconcentración.** Se aplica solo dentro de la ventana de fusión, entre
la temperatura de transición vítrea del sistema crioconcentrado y la de fusión del hielo.
Dentro de esa ventana coexisten hielo y fase líquida, y el soluto —incluidos el oxígeno
disuelto y los ácidos del NADES— está a concentración máxima. Fuera de la ventana `f_cc = 1`.

**El compromiso.** Descongelar frío mantiene `k` bajo pero **alarga el tiempo dentro de la
ventana de crioconcentración**; descongelar caliente la cruza rápido pero a mayor `k`. Como
`k` crece exponencialmente con T (ec. 6) mientras el tiempo en la ventana escala
aproximadamente con `1/ΔT`, el mínimo de la ec. (12) existe y es calculable.

**Segunda restricción, impuesta por el HPTLC.** La temperatura de descongelación tiene además
un **piso** que no viene de la degradación sino de la siembra: un NADES a 4 °C es demasiado
viscoso para que un aplicador de banda dosifique de forma reproducible. La viscosidad a cada
temperatura ya la entrega `calculate_nades_properties()`, de modo que el módulo puede reportar
la temperatura mínima que satisface un umbral de viscosidad de siembra.

La recomendación final es por tanto un **intervalo**, no un punto: acotado por abajo por la
viscosidad de siembra y por arriba por la degradación acumulada.

```
(13)   C_final = C(t_almacenamiento) · (1 − pérdida_descongelación)^n_ciclos
```

**Predicción cualitativa esperada, como control de sanidad:** debería ganar la descongelación
rápida —baño de agua a temperatura moderada— frente a la lenta en refrigerador, porque el
término dominante es el tiempo dentro de la ventana de crioconcentración y no la temperatura
pico. Si el módulo recomienda descongelar lento a 4 °C, auditar `f_cc` antes de creerle.

**Nota sobre "−4 °C".** Si la intención es descongelar *a* −4 °C, conviene notar que con
20–30 % de agua y descenso crioscópico el sistema puede seguir parcialmente sólido a esa
temperatura, es decir, permanecer indefinidamente dentro de la ventana de crioconcentración
—el peor lugar posible. El módulo evalúa cualquier temperatura que se le pida; esta en
particular debe mirarse con cuidado.

## 7. Métrica principal — equivalencia de atmósfera inerte

```
(14)   Equivalencia = k(EtOH 70 %, inerte, oscuridad) / k(NADES, aire, oscuridad)
```

Equivalencia ≥ 1 sostiene el enunciado: *"el extracto en este NADES, en aire, se degrada más
lento que el mismo extracto en etanol bajo nitrógeno"*. Es la razón de fondo por la que se
eligió NADES y va como salida principal del módulo, no dentro de la comparación de solventes.

Uso secundario: el día que exista línea de N₂, la métrica indica cuánto extra compra sobre lo
que el solvente ya proveía.

## 8. Arquitectura

**Módulo nuevo `stability_time.py`.** No se agrega a `model.py`, que ya tiene ~1.250 líneas y
nueve responsabilidades. Física propia, parámetros propios, calibración propia, testeable
aislado.

Interfaz pública:

| Función | Devuelve |
|---|---|
| `storage_curve(props, poly_df, cond, t_max, calibracion=None)` | DataFrame largo: compuesto × t → retención |
| `shelf_life(props, poly_df, cond, umbral=0.90)` | t90/t50 por compuesto y TPC ponderado |
| `compare_storage_conditions(props, poly_df)` | Grilla T × luz × headspace → t90 + banderas |
| `compare_solvents(lista_props, poly_df, cond)` | Ranking por t90 + equivalencia de atmósfera |
| `thaw_loss(props, poly_df, T_ext, tau, T_0)` | Pérdida por un evento de descongelación (ec. 12) |
| `optimal_thaw(props, poly_df, umbral_visc)` | Intervalo de temperatura recomendado: piso por viscosidad de siembra, techo por degradación |

`shelf_life`, `compare_storage_conditions` y `compare_solvents` se construyen sobre
`storage_curve`; `optimal_thaw` se construye sobre `thaw_loss`.

`CondicionesAlmacenamiento` es un dataclass: `temp_C`, `luz`, `atmosfera`, `n_ciclos`,
`descongelacion` (a su vez `T_ext`, `tau`).

Tabla de parámetros cinéticos: dict a nivel de módulo con cita por entrada, siguiendo el
patrón de `_params` dentro de `thermal_degradation()`.

**Cambios en archivos existentes:**
- `model.py` — extraer tabla `Ea` por clase a constante compartida; corregir signo (§4).
- `data.py` — agregar campo `glicosilado: bool` a las tres bases de polifenoles.
- `app.py` — pestaña nueva con las cuatro vistas.

## 9. Calibración

`calibracion=None` por defecto: corre con parámetros de literatura y marca cada salida como
predicción teórica.

Con un DataFrame `(compuesto | clase, t_dias, retencion_pct, condiciones)` reajusta `k` y
`C_res` para los compuestos presentes y deja el resto en literatura — **calibración parcial**,
que es la forma en que llegarán los datos reales.

**Método de ajuste, sin dependencia nueva.** No hay scipy en `requirements.txt`. Barrido en
grilla sobre `C_res ∈ [0, 0.6]`; para cada valor, regresión lineal exacta de
`ln[(C − C_res)/(1 − C_res)]` contra `t` (numpy). Se retiene el par con menor SSE. Devuelve
R² y número de puntos.

**Regla de honestidad.** Toda salida lleva `origen ∈ {"literatura", "calibrado"}` y el número
de puntos experimentales que la respaldan. Nada se presenta como medido si no lo fue. Mismo
criterio aplicado en SimEluent.

## 10. Salidas en la app

Pestaña nueva, cuatro vistas:

1. **Curva** — retención vs días, línea por compuesto, agrupable por clase; banda de
   incertidumbre por Monte Carlo sobre `k` y `C_res` (±25 %), reutilizando el patrón de
   `nep_monte_carlo`.
2. **Ventana analítica** — t90 y t50 por compuesto y para TPC ponderado por concentración,
   expresado como fecha límite de análisis.
3. **Protocolo** — grilla temperatura × luz × headspace con t90, delta respecto a la
   condición base, y banderas de riesgo. Restringida a lo disponible en el laboratorio;
   `inerte` se muestra marcado como no disponible.
4. **Escenarios de temperatura** — ambiente / 4 °C / −20 °C / −80 °C con t90, equivalencia de
   atmósfera y banderas.
5. **Descongelación** — pérdida por evento en función de la temperatura y del medio de
   descongelación (aire vs baño), con el intervalo recomendado y sus dos cotas explícitas:
   viscosidad de siembra por abajo, degradación acumulada por arriba.

**Predicción cualitativa esperada, como control de sanidad:** la ganancia grande está entre
ambiente y 4 °C; el salto de 4 °C a −20 °C es menor de lo que la intuición sugiere y
**posiblemente negativo** por crioconcentración; −80 °C es indistinguible de −20 °C en un
sistema que vitrifique bien. Si el módulo dice otra cosa, auditarlo antes de creerle.

## 11. Testing

Invariantes primero — atrapan errores de signo y de unidades, que es exactamente la clase de
error encontrada en §4:

- `C(0) = 1` y `lim(t→∞) = C_res`, exactos
- monotonía decreciente en `t` para todo compuesto
- t90 disminuye al subir T, al pasar a luz ambiente, al aumentar headspace
- t90(antocianina) < t90(flavonol) para mismo solvente y condición
- un NADES protector da t90 mayor que la línea base etanol 70 %
- **round-trip de calibración**: curva sintética con `k` y `C_res` conocidos + ruido; el ajuste
  debe recuperarlos dentro de tolerancia
- coherencia entre módulos: la `Ea` compartida da el mismo valor en `thermal_degradation` y
  en `f_T`
- bandera de crioconcentración se activa con `water_pct > 20` y `T < 0`
- la integral de descongelación (ec. 12) converge al reducir el paso de integración
- `thaw_loss` es mayor con `τ` grande (aire) que con `τ` chico (baño) a igual `T_ext`, que es
  la afirmación central del §6.1
- `optimal_thaw` devuelve un intervalo no vacío, o falla explícitamente si el umbral de
  viscosidad y el de degradación son incompatibles

## 12. Trabajo futuro

**Vías competitivas (opción C del brainstorming).** Modelar oxidación e hidrólisis del enlace
glicosídico por separado, con la aglicona liberada degradándose más rápido y balance de masa
entre especies. Es lo único que predeciría el **cambio de perfil** —aparición de bandas de
aglicona— que es literalmente lo que se observa en placa HPTLC. Requiere parámetros que hoy
no son medibles con el equipamiento disponible.

**Decisión diferida:** se retoma después del módulo de compatibilidad HPTLC, cuando existan
datos de perfil que permitan separar las dos vías.

## 13. Parámetros a fijar experimentalmente

Este documento es vivo: los parámetros se corrigen a medida que el protocolo experimental se
ajusta. Orden de prioridad para medición:

| Parámetro | Estado | Cómo se fija |
|---|---|---|
| `C_res` por clase | Peor sustentado | Curva de almacenamiento propia, ≥ 5 puntos |
| `T_g` por sistema | Peor sustentado | DSC |
| `k_ref` térmico por clase | Requiere recalibración tras §4 | Literatura de vidas medias térmicas |
| `k_clase` almacenamiento | Literatura de otras matrices | Curva propia |
| `γ` (ec. 8) | Ajustado a dos puntos ancla | Comparación NADES vs EtOH propia |
| `f_cc` y ventana de fusión (ec. 12) | Estimado | Ensayo de congelación–descongelación |
| `τ` térmico del vial (ec. 11) | No fijado | Termopar en vial testigo — **es el más fácil de medir de toda la lista** |
| Umbral de viscosidad de siembra | No fijado | Ensayo de reproducibilidad con el aplicador de banda |

## 14. Referencias

Referencias ya usadas y vetadas en el código base del proyecto:

- Chanioti & Tzia (2017) *Food Bioprocess Technol.* 10, 1999 — NADES vs EtOH, retención de antocianinas
- Benvenutti et al. (2019) *Food Res. Int.* 119, 710 — estabilidad de antocianinas en NADES
- Dai & Verpoorte (2014) — red de H-bonds y difusión de O₂ en DES
- Torskangerpoll & Andersen (2005) *Food Chem.* 89, 427 — cinética de antocianinas
- Oliveira et al. (2016) *Food Chem.* 213, 557 — polifenoles generales
- Wang & Xu (2007) *Food Chem.* 104, 1320 — ácidos hidroxicinámicos
- Florindo et al. (2019) *ACS Sustain. Chem. Eng.* 7 — reutilización y estabilidad de DES
- Ruiz et al. (2024) *Horticulturae* 10, 458 — perfil fenólico de *Berberis microphylla*

**Pendiente de verificación antes de uso en tesis:** citas específicas para crioconcentración
en sistemas parcialmente acuosos, comportamiento WLF bajo T_g en DES, y coeficientes de
fotodegradación por clase. Estas se identifican pero **no se consignan aquí con referencia
concreta**, en cumplimiento de la regla de no inventar citas.

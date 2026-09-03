# Módulo de Compatibilidad HPTLC + Reordenamiento del programa

**Proyecto:** Simulador NADES — Tesis Doctoral PUCV 2026
**Fecha:** 2026-09-02
**Estado:** diseño aprobado, pendiente de plan de implementación
**Autor del diseño:** Cristofher Ferrada (con Claude Code)

---

## 1. Contexto y problema

SimNADES responde hoy *qué NADES extrae mejor*. No responde la pregunta que viene
inmediatamente después en el trabajo real: **si ese extracto se puede sembrar directo en la
placa, o si hay que limpiarlo antes**.

Esa pregunta no es menor. Un NADES es no volátil por diseño: lo que se deposita en el origen
se queda ahí. Si la respuesta es "hay que limpiar", aparece un paso de SPE que cambia el
costo, el tiempo y el balance de masa de todo el protocolo — y que hoy el simulador no
contempla en ninguna parte.

El uso previsto del HPTLC en esta tesis es **huella dactilar cualitativa**: comparar qué
saca cada NADES. Existe además la intención de raspar bandas y reinyectarlas en HPLC
(§4.6).

## 2. Regla de construcción: nada sin fuente

Restricción impuesta por el autor y que gobierna todo el módulo:

> Cada parámetro que el módulo emita debe tener una fuente verificable. Donde no exista
> literatura, el módulo declara el vacío y **no emite número**.

Se implementa con una insignia obligatoria por factor:

| Insignia | Significado |
|---|---|
| 🟩 `MEDIDO` | Hay valor o resultado publicado para este sistema, con cita |
| 🟨 `INFERIDO` | Hay mecanismo publicado, pero no medido con NADES |
| ⬜ `SIN_FUENTE` | Hueco declarado. No se emite valor. |

Un factor sin fuente no baja ni sube el veredicto: lo vuelve **incierto**, que es distinto
de malo. Esa distinción es el punto del módulo.

## 3. Lo que la literatura establece

### 3.1 Los dos obstáculos, nombrados en fuente primaria 🟩

Liu, Ahlgren, Korthout, Salomé-Abarca, Bayona, Verpoorte & Choi (2017).
*Broad range chemical profiling of natural deep eutectic solvent extracts using a high
performance thin layer chromatography-based method.* J. Chromatogr. A 1532:198-207.
DOI [10.1016/j.chroma.2017.12.009](https://doi.org/10.1016/j.chroma.2017.12.009)

Los autores sitúan la dificultad analítica de los NADES en dos propiedades: baja presión de
vapor y alta viscosidad. No es una lista larga de factores — son esos dos.

NADES ensayados: málico–ChCl (1:1), málico–glucosa (1:1), ChCl–glucosa (5:2),
málico–prolina (1:1), glucosa–fructosa–sacarosa (1:1:1), glicerol–prolina–sacarosa (9:4:1).
Óptimo de rendimiento cerca de **20 % de agua (w/w)**.

### 3.2 En fase normal la siembra directa fracasa 🟩

Estudio de NADES sobre hojas de quinoa con análisis HPTLC semicuantitativo
([PMC12195850](https://pmc.ncbi.nlm.nih.gov/articles/PMC12195850/)).

Sobre **sílica gel 60 F254**, la aplicación directa perturbó la migración cromatográfica y
produjo colas severas en *todas* las muestras, **incluso diluyendo 1/10 con agua**. Los
autores debieron introducir SPE (cartucho polimérico Strata-X, carga 1 mL, lavado con agua,
elución con etanol) antes de aplicar.

Método: 4 µL (flavonoides), 6 µL (DPPH), 8 µL (α-amilasa); ATS 4; bandas a 8 mm del borde;
cámara AMD2; secado 105 °C / 60 min; revelado con difenilborinato de aminoetilo + PEG 400,
DPPH, y α-amilasa/almidón/vapor de yodo.

**Este es el punto de fracaso que sirve de metro:** 4–8 µL diluidos 1/10 equivalen a
0,4–0,8 µL de NADES neto por banda, y aun así falló.

### 3.3 Por qué la fase reversa es otro problema 🟨

*Reversed Phase HPTLC of Aqueous Samples in Student Laboratories Using the Example of
Anthocyanin Patterns from Flower Petals.* J. Chem. Educ. 2019, 96(9).
DOI [10.1021/acs.jchemed.8b00900](https://doi.org/10.1021/acs.jchemed.8b00900)

En placas de fase reversa **el agua tiene bajo poder eluyente**, y eso se aprovecha
justamente para aplicar muestras acuosas como banda estrecha. El trabajo lo demuestra con
patrones de antocianinas de pétalos y frutos, y añade que sobre la placa se puede estudiar
el comportamiento de pH y la complejación con metales, y hacer hidrólisis pre-cromatográfica
del glicósido.

En sílica el agua es eluyente **fuerte**; en RP es **débil**. El signo se invierte. Por eso
el fracaso documentado en fase normal **no se traslada** a RP-18 — pero tampoco hay
publicación que lo confirme con NADES (§4.1).

### 3.3.b El aplicador automático pierde su mecanismo de enfoque 🟨

Documentación CAMAG del Linomat 5 (técnica spray-on): el disolvente se evapora casi por
completo durante la aplicación, y por eso la muestra se concentra en banda angosta. Es lo
que permite aplicar volúmenes grandes en disolventes polares como metanol o agua obteniendo
zonas compactas.

Combinado con §3.1 (el NADES tiene baja presión de vapor por definición), se sigue que
**el mecanismo de enfoque no opera sobre la fracción NADES**: el disolvente volátil se va,
el NADES permanece como película líquida sobre la capa. El aplicador sigue dosificando un
volumen reproducible, pero pierde el paso que convierte ese volumen en banda estrecha.

Explica mecanísticamente el resultado de §3.2: diluir 1/10 reduce la masa depositada, pero
no restituye el mecanismo de enfoque.

Dos consecuencias de diseño:

1. Refuerza §10.1. La siembra se declara determinista en SimEluent *porque* enfoca.
2. La zona de concentración (§3.5) enfoca por migración cromatográfica, no por evaporación:
   es un mecanismo independiente que sigue operando con matriz no volátil. Deja de ser una
   comodidad y pasa a ser la vía que restituye el supuesto.

Vacío asociado ⬜: obstrucción de aguja/boquilla y arrastre entre muestras con líquido
viscoso. Sin fuente; no se afirma.

### 3.4 Especificaciones de placa 🟩

Folleto técnico Merck Millipore *Fast and precise Thin Layer Chromatography*.

| | TLC | HPTLC |
|---|---|---|
| Partícula media | 10–12 µm | 5–6 µm |
| Distribución | 5–20 µm | 4–8 µm |
| Espesor de capa | 250 µm (vidrio) / 200 µm (Al) | 200 µm (100 µm extrafina) |

Volumen de aplicación del ensayo de aptitud de Ph. Eur.: **10 µL en placa TLC normal,
1–2 µL en placa de partícula fina**. Es el único volumen de aplicación con respaldo
normativo que el módulo usa como referencia.

Indicadores: **F₂₅₄** (verde) y **F₂₅₄s** (azul, estable a ácido). Distinción relevante
porque la mayoría de los HBD del simulador son ácidos.

**W** en el catálogo = completamente humectable con agua. Sin la W, la placa RP-18 no moja
bien con fases móviles muy acuosas.

Placas del catálogo relevantes para este trabajo:

| Producto | Cat. Merck | Formato | Capa |
|---|---|---|---|
| TLC Sílica 60G F₂₅₄ (yeso) — *la que hay en el laboratorio* | 1.00390 | 20×20 vidrio | 250 µm |
| TLC Sílica 60 RP-18 F₂₅₄s | 1.05559 | grado TLC | 250 µm |
| HPTLC Sílica 60 RP-18 F₂₅₄s | 1.13724 / 1.16225 | 10×10 / 20×10 | 200 µm |
| HPTLC Sílica 60 RP-18 **W** F₂₅₄s | 1.13124 | 10×10 | 200 µm |
| HPTLC RP-18 F₂₅₄s con zona de concentración | 1.15498 | 20×2,5 cm | — |
| TLC Sílica 60 F₂₅₄ con zona de concentración | 1.11798 | 20×20 vidrio | 250 µm |

`60G` = aglutinante de yeso, designación de farmacopea (sílica G con yeso frente a sílica H
sin aglutinante ajeno); ~200 monografías de Ph. Eur. la referencian.

### 3.5 Zona de concentración 🟩

Del mismo folleto: son placas de dos adsorbentes — uno inerte de poro grande donde se
siembra, y la capa selectiva donde se separa. La muestra se concentra en banda estrecha en
la interfaz en segundos, sin importar forma, tamaño ni posición del depósito. El fabricante
declara además que la zona **sirve como paso de limpieza para matrices complejas**, y lista
entre los beneficios que incorpora una etapa de purificación y concentración.

Zona de 2,5 cm en placas analíticas (TLC y HPTLC); 4 cm en preparativas (PLC).

Es decir: **existe una placa catalogada que hace sobre la placa parte de lo que el trabajo
de quinoa tuvo que hacer con SPE.** Es la tercera vía del módulo.

## 4. Vacíos declarados

Estos no se rellenan. Se muestran como tales y alimentan el diseño experimental.

### 4.1 NADES sembrado directo en RP-18 ⬜ — el vacío central

El fracaso publicado es en fase normal. El mecanismo favorable en RP está publicado, pero
con muestras acuosas, no con NADES. **El cruce no existe en la literatura.**

Se trata como **hipótesis a ensayar**, no como predicción. El módulo genera el protocolo
candidato; la etapa ③ registra si funcionó.

### 4.2 Umbral de dosificación por viscosidad ⬜

Es una especificación del aplicador, no un dato de literatura. El módulo pregunta qué
aplicador se usa y muestra la viscosidad calculada, sin inventar el corte.

### 4.3 Carga no volátil tolerable por banda ⬜

No hay valor publicado. Lo que sí hay es el **punto de fracaso** de §3.2 (0,4–0,8 µL de
NADES neto sobre sílica). El módulo compara contra ese punto y lo dice explícitamente.

### 4.4 Interferencia en revelado sin limpieza previa ⬜

Lo documentado (§3.2) es que NP/PEG, DPPH y α-amilasa funcionan **después** de SPE. Sin SPE
no hay dato.

### 4.5 Volatilidad e higroscopicidad de los 39 componentes ⬜

No existe como tabla publicada. Requiere sourcear componente por componente. Fuera del
alcance de esta iteración; el módulo deja el campo vacío y visible.

### 4.6 Raspado de banda → HPLC ⬜

Buscado, sin fuente específica para NADES. Solo hay guía genérica de TLC preparativa
(raspar, eluir con disolvente polar, filtrar) y la advertencia de que el adsorbente
finamente dividido capta vapores orgánicos y humedad del ambiente por su gran superficie.

Queda como pregunta abierta de la tesis.

## 5. Alcance

**Entra:**
- Módulo `hptlc.py` con el registro de evidencia y la evaluación por placa.
- Sección de UI con veredicto por placa, protocolo candidato y lista de vacíos.
- Reordenamiento de las 8 pestañas en 3 etapas de flujo de trabajo (§7).
- Persistencia de "Mis Datos" (§8).
- División de `app.py` en `app.py` + `tabs/*.py`, requisito del reordenamiento.

**No entra:**
- Índice numérico 0–100 % de "probabilidad de siembra". Fue descartado explícitamente:
  exigiría coeficientes sin respaldo.
- Poblar los 39 componentes con parámetros HPTLC (§4.5).
- Modelar el paso de SPE en el análisis económico.

## 6. Arquitectura

Archivo nuevo `hptlc.py`. No se agrega a `model.py`, que ya tiene 1276 líneas y una
responsabilidad distinta (fisicoquímica de extracción).

```
hptlc.py
├── EVIDENCIA: dict[str, Fuente]        # autores, año, revista, DOI, qué afirma
├── PLACAS: dict[str, Placa]            # catálogo §3.4 con especificaciones
├── Factor(NamedTuple)                  # valor | nivel | fuente_id | texto
├── evaluar_placa(props, placa, volumen_uL, dilucion) -> Veredicto
└── protocolo_candidato(veredicto) -> Protocolo
```

`Veredicto` no lleva score. Lleva:
- `estado`: `VIABLE` | `REQUIERE_LIMPIEZA` | `NO_VIABLE` | `SIN_EVIDENCIA`
- `factores`: lista de `Factor`, cada uno con su insignia y su cita
- `vacios`: lista de los `SIN_FUENTE` que afectan a esta placa

`hptlc.py` no importa `app.py` ni Streamlit. Se puede probar sin levantar la app.

## 7. Reordenamiento

Las 8 pestañas están hoy ordenadas por **técnica**. Pasan a ordenarse por **flujo de
trabajo**, conservándose como sub-pestañas para no perder nada:

| Etapa | Contiene |
|---|---|
| **① DISEÑAR** — antes del laboratorio | Recomendador · Resultados · Análisis · Optimización |
| **② EJECUTAR** — protocolo para el mesón | Proceso UAE·3 pasos · **Compatibilidad HPTLC** · Economía |
| **③ REGISTRAR** — después del laboratorio | Mis Datos, como bitácora persistente |
| Metodología | siempre accesible |

Corrige además que los bloques estén escritos fuera de orden en el fuente (el de `tab5`
está entre `tab3` y `tab4`).

## 8. Persistencia de "Mis Datos"

Hoy el CSV subido vive en `session_state` y muere al cerrar la app.

Pasa a un archivo local versionable (`data/experimentos.csv`) que **acumula entre
sesiones**. El parity plot crece a medida que se cargan ensayos, en vez de reconstruirse
desde cero cada vez.

Ahí aterriza el resultado del ensayo de RP-18: la hipótesis de §4.1 se confronta con lo que
efectivamente pasó en la placa. Ese es el ciclo que el programa hoy no cierra —
planificar → ensayar → registrar.

## 9. Criterios de aceptación

1. Ningún factor emite valor numérico sin `fuente_id` resoluble en `EVIDENCIA`.
2. Cada uno de los seis vacíos de §4 aparece en la UI cuando corresponde a la placa elegida.
3. El veredicto sobre sílica 60G reproduce el resultado publicado: requiere limpieza.
4. El veredicto sobre RP-18 sale como `SIN_EVIDENCIA` con hipótesis y protocolo candidato,
   nunca como `VIABLE`.
5. `hptlc.py` se importa y se prueba sin Streamlit.
6. Un experimento cargado en ③ sobrevive al reinicio de la app.

## 10. Acople con SimEluent

Este diseño no termina en SimNADES. SimEluent (`../SimEluent`) optimiza la fase móvil
HPTLC, y los hallazgos de §3 tocan su supuesto central.

### 10.1 σ₀ es la variable de acople

`SimEluent/docs/02_VARIABLES_HPTLC.md` declara la siembra como variable 1, **determinista**
por usar aplicador automático, y la describe como el único parámetro sin incertidumbre.
Esa nota es explícita en que ahí reside la defensibilidad del modelo: como σ₀ es conocido,
la incertidumbre queda acotada a las variables 4–7 (cámara, HR, T, Zf). Semilla:
`σ₀ = 1,0 mm, fijo`.

**Ese supuesto vale para una muestra limpia, no para un extracto NADES sembrado directo.**
El aplicador entrega un volumen reproducible; el ancho de zona resultante lo fija la matriz.
Las colas severas de §3.2 son un σ₀ arruinado.

La afirmación defendible no es que σ₀ se dispare en RP-18 — eso es justamente el vacío de
§4.1. Es que **σ₀ deja de ser determinista y pasa a ser dependiente de la matriz y no
medido**, que es donde se apoyaba el argumento de robustez.

σ₀ propaga por `conditions.sigma_zone()` → `conditions.plates_N()` → `resolution.py` → la
función objetivo. Es decir, atraviesa el modelo entero.

**Interfaz entre los dos programas:** el veredicto del módulo HPTLC de SimNADES determina
el régimen de σ₀; σ₀ es entrada de SimEluent. Mientras el veredicto sea `SIN_EVIDENCIA`,
SimEluent debe tratar σ₀ como incierto y propagarlo por Monte Carlo junto con las variables
manuales, en vez de fijarlo.

### 10.2 `Phase` es demasiado delgada

`SimEluent/engine/data_loader.py` define `Phase` con tres campos: `name`, `mode` (NP|RP),
`w_spec`. `constants.py` instancia tres fases fijas. Eso no alcanza para expresar lo que
§3.4 documenta:

| Falta en `Phase` | Consecuencia | Fuente |
|---|---|---|
| Tamaño de partícula y espesor | No distingue TLC (10–12 µm) de HPTLC (5–6 µm). `docs/02` var. 8 ya dice que entra por `κ` (15) y `N` base (17): **documentado pero no implementado** | §3.4 |
| Humectabilidad (W) | El optimizador puede recomendar un eluyente muy acuoso sobre una RP-18 que no moja | §3.4 |
| Indicador F₂₅₄ vs F₂₅₄s | No puede expresar incompatibilidad con eluyentes ácidos | §3.4 |
| Zona de concentración | Es un control sobre σ₀, no una placa más | §3.5 |

El caso de indicador no es hipotético: las tres referencias de antocianinas de
`data/referencias.csv` (R001, R002, R003) usan ácido fórmico o fórmico+acético, y las placas
disponibles en el laboratorio son F₂₅₄. `docs/02` var. 2 ya nombra "RP-18 F254s", pero el
dataclass no tiene el campo.

### 10.3 Alcance de este spec respecto a SimEluent

Aquí **solo se define la interfaz** (σ₀ y su régimen). Los cambios dentro de SimEluent
—extender `Phase`, poblar el catálogo de placas de §3.4, propagar σ₀ como incierto— van en
su propio spec y su propio plan, en el repositorio de SimEluent.

Lo que este spec sí exige: que `hptlc.py` exponga el veredicto en una forma que SimEluent
pueda consumir sin importar Streamlit ni SimNADES completo.

## 11. Riesgo principal

Que el módulo se lea como una predicción cuando es un mapa de lo que se sabe y lo que no.
Se mitiga con la insignia obligatoria y con que el estado `SIN_EVIDENCIA` sea visualmente
distinto de `VIABLE`, no una gradación del mismo color.

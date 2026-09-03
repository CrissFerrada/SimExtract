# Compatibilidad HPTLC — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Que SimExtract diga, con evidencia citada y vacíos declarados, si un extracto NADES se puede sembrar directo en una placa dada, y que SimEluent deje de tratar σ₀ como determinista.

**Architecture:** Módulo puro `hptlc.py` en SimExtract (sin Streamlit), con registro de evidencia y catálogo de placas reales de Merck. Su veredicto define el régimen de σ₀, que SimEluent consume para propagarlo por Monte Carlo junto a las variables manuales. Las 8 pestañas de SimExtract se reagrupan en tres etapas de flujo de trabajo y "Mis Datos" pasa a persistir en disco.

**Tech Stack:** Python 3.11 · Streamlit · pandas · NumPy · pytest · black/ruff (line-length 100)

## Global Constraints

- **Ninguna cifra sin fuente.** Todo `Factor` con `valor is not None` debe tener `fuente_id` resoluble en `EVIDENCIA`. Sin fuente ⇒ `Nivel.SIN_FUENTE` y `valor=None`.
- **RP nunca sale `VIABLE`.** El cruce NADES × RP-18 no está publicado (spec §4.1). El estado máximo para una placa RP es `SIN_EVIDENCIA`.
- `hptlc.py` no importa `streamlit`, `app` ni `model`. Se prueba sin levantar la app.
- Docstrings estilo Google en inglés. Comentarios solo el "por qué".
- Rutas con `pathlib.Path`, nunca strings.
- Commits convencionales en español (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`).
- `line-length = 100` (black y ruff ya configurados en ambos repos).
- Repos: `SN = C:\Users\crist\OneDrive\Desktop\Proyectos\Tesis\Simulador NADES`, `SE = C:\Users\crist\OneDrive\Desktop\Proyectos\Tesis\SimEluent`.
- Intérprete SimExtract: `.venv\Scripts\python.exe` (nunca los stubs `.exe` de pip).

---

## Estructura de archivos

| Archivo | Responsabilidad | Fase |
|---|---|---|
| `SN/evidencia.py` | Registro único de fuentes y niveles de evidencia | 1 |
| `SN/hptlc.py` | Catálogo de placas, evaluación, veredicto | 1 |
| `SN/explicacion.py` | Lectura en lenguaje llano de cada propiedad | 4 |
| `SN/tabs/componentes.py` | Ficha explicada y franja de NADES activo | 4-5 |
| `SN/tema.py` | Paleta, tipografía y movimiento | 6 |
| `SN/tests/test_hptlc.py` | Pruebas del módulo puro | 1 |
| `SN/tabs/hptlc_tab.py` | UI de la sección HPTLC | 2 |
| `SN/experimentos.py` | Persistencia de la bitácora experimental | 3 |
| `SN/data/experimentos.csv` | Bitácora (creada en runtime) | 3 |
| `SN/tabs/__init__.py`, `tabs/*.py` | Las 8 pestañas extraídas de `app.py` | 4 |
| `SE/data/placas.csv` | Catálogo de placas con especificaciones | 5 |
| `SE/engine/data_loader.py` | `Phase` extendida + `load_phases()` | 5 |
| `SE/engine/optimizer.py` | σ₀ muestreado en `ConditionPrior` | 6 |
| `SE/engine/sigma0.py` | Régimen de σ₀ según veredicto y placa | 6 |

---

# FASE 1 — El módulo `hptlc.py`

Núcleo del trabajo. Produce software probable sin tocar UI.

### Task 1: Registro de evidencia y catálogo de placas

**Files:**
- Create: `SN/evidencia.py`, `SN/hptlc.py`
- Test: `SN/tests/test_hptlc.py`

**Interfaces:**
- Produces: `Fuente`, `Nivel`, `EVIDENCIA: dict[str, Fuente]` en `evidencia.py`; `Placa`, `PLACAS: dict[str, Placa]` en `hptlc.py`

El registro vive en su propio módulo porque lo comparten el veredicto HPTLC (Fase 1) y la
capa de explicación (Fase 4): una sola fuente de verdad bibliográfica para todo el programa.

- [ ] **Step 1: Write the failing test**

```python
# SN/tests/test_hptlc.py
from evidencia import EVIDENCIA
from hptlc import PLACAS


def test_toda_fuente_tiene_doi_y_afirmacion() -> None:
    assert EVIDENCIA, "el registro de evidencia no puede estar vacio"
    for fuente_id, fuente in EVIDENCIA.items():
        assert fuente.id == fuente_id
        assert fuente.doi, f"{fuente_id} sin DOI"
        assert fuente.afirma, f"{fuente_id} sin afirmacion"


def test_catalogo_incluye_la_placa_del_laboratorio_y_las_rp() -> None:
    assert "silice-60G-F254" in PLACAS
    assert "rp18-w-f254s" in PLACAS
    assert "rp18-zona-concentracion" in PLACAS


def test_placa_del_laboratorio_es_grado_tlc_fase_normal() -> None:
    placa = PLACAS["silice-60G-F254"]
    assert placa.modo == "NP"
    assert placa.grado == "TLC"
    assert placa.indicador == "F254"
    assert placa.catalogo == "1.00390"
    assert placa.espesor_um == 250.0


def test_la_w_implica_humectable_con_agua() -> None:
    assert PLACAS["rp18-w-f254s"].humectable_agua is True
    assert PLACAS["rp18-f254s"].humectable_agua is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$SN" && .venv/Scripts/python.exe -m pytest tests/test_hptlc.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'hptlc'`

- [ ] **Step 3: Write minimal implementation**

```python
# SN/evidencia.py
"""Single bibliographic registry for the whole program.

Shared by the HPTLC verdict and by the property explanations, so a source is
described once and cited from anywhere. Imports nothing from the rest of the app.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Nivel(str, Enum):
    """Evidence level attached to every claim the program makes."""

    MEDIDO = "MEDIDO"
    INFERIDO = "INFERIDO"
    SIN_FUENTE = "SIN_FUENTE"


@dataclass(frozen=True)
class Fuente:
    """A verifiable bibliographic source backing one or more factors."""

    id: str
    cita: str
    doi: str
    afirma: str


EVIDENCIA: dict[str, Fuente] = {
    "liu2017": Fuente(
        id="liu2017",
        cita=(
            "Liu X., Ahlgren S., Korthout H.A.A.J., Salomé-Abarca L.F., Bayona L.M., "
            "Verpoorte R., Choi Y.H. (2017). Broad range chemical profiling of natural "
            "deep eutectic solvent extracts using a high performance thin layer "
            "chromatography-based method. J. Chromatogr. A 1532:198-207."
        ),
        doi="10.1016/j.chroma.2017.12.009",
        afirma=(
            "Sitúa la dificultad analítica de los NADES en dos propiedades: baja presión "
            "de vapor y alta viscosidad. Óptimo de rendimiento cerca de 20% de agua (w/w)."
        ),
    ),
    "quinoa2025": Fuente(
        id="quinoa2025",
        cita=(
            "NADES para la extracción de compuestos bioactivos de hojas de quinoa "
            "(Chenopodium quinoa Willd.): análisis semicuantitativo por HPTLC. "
            "PMC12195850."
        ),
        doi="PMC12195850",
        afirma=(
            "Sobre sílica gel 60 F254 la aplicación directa perturbó la migración y "
            "produjo colas severas en todas las muestras, incluso diluyendo 1/10 con "
            "agua. Requirió SPE (Strata-X). Aplicaron 4-8 uL."
        ),
    ),
    "jchemed2019": Fuente(
        id="jchemed2019",
        cita=(
            "Reversed Phase High Performance Thin Layer Chromatography of Aqueous "
            "Samples in Student Laboratories Using the Example of Anthocyanin Patterns "
            "from Flower Petals. J. Chem. Educ. 2019, 96(9)."
        ),
        doi="10.1021/acs.jchemed.8b00900",
        afirma=(
            "En placas de fase reversa el agua tiene bajo poder eluyente, y eso se "
            "aprovecha para aplicar muestras acuosas como banda estrecha."
        ),
    ),
    "merck-placas": Fuente(
        id="merck-placas",
        cita=(
            "Merck Millipore, folleto técnico 'Fast and precise Thin Layer "
            "Chromatography'."
        ),
        doi="catalogo-merck",
        afirma=(
            "TLC: 10-12 um de partícula, capa 250 um en vidrio. HPTLC: 5-6 um, capa "
            "200 um. Ensayo de aptitud Ph. Eur.: 10 uL en placa TLC normal, 1-2 uL en "
            "placa de partícula fina. 'W' = completamente humectable con agua. F254s = "
            "indicador estable a ácido. 60G = aglutinante de yeso."
        ),
    ),
    "merck-zona": Fuente(
        id="merck-zona",
        cita=(
            "Merck Millipore, folleto técnico, sección 'Concentrating zone plates "
            "(TLC, HPTLC, PLC)'."
        ),
        doi="catalogo-merck",
        afirma=(
            "Dos adsorbentes: uno inerte de poro grande donde se siembra y la capa "
            "selectiva donde se separa. La muestra se concentra en banda estrecha en la "
            "interfaz en segundos, sin importar forma, tamaño ni posición del depósito. "
            "El fabricante declara que la zona sirve como paso de limpieza para "
            "matrices complejas."
        ),
    ),
    "camag-linomat": Fuente(
        id="camag-linomat",
        cita="CAMAG, documentación de la técnica spray-on del Linomat 5.",
        doi="documentacion-camag",
        afirma=(
            "En el spray-on el disolvente se evapora casi por completo durante la "
            "aplicación, y ese es el paso que concentra la muestra en banda angosta."
        ),
    ),
}
"""Verifiable sources. Every factor with a value must name one of these."""
```

```python
# SN/hptlc.py
"""HPTLC direct-spotting compatibility for NADES extracts.

Every emitted value carries a resolvable source. Where the literature is silent
the module declares the gap instead of producing a number: that distinction is
the point of the module, not a limitation of it.

Imports neither Streamlit nor the extraction model, so it can be tested and reused
(notably by SimEluent) on its own.
"""

from __future__ import annotations

from dataclasses import dataclass

from enum import Enum

from evidencia import EVIDENCIA, Nivel


@dataclass(frozen=True)
class Placa:
    """A real catalogued plate with the specifications the model needs."""

    id: str
    nombre: str
    catalogo: str
    modo: str
    grado: str
    particula_um: tuple[float, float]
    espesor_um: float
    humectable_agua: bool
    indicador: str
    zona_concentracion: bool

    def __post_init__(self) -> None:
        """Validate the fields the verdict logic branches on."""
        if self.modo not in {"NP", "RP"}:
            raise ValueError("placa.modo debe ser 'NP' o 'RP'")
        if self.grado not in {"TLC", "HPTLC"}:
            raise ValueError("placa.grado debe ser 'TLC' o 'HPTLC'")
        if self.indicador not in {"F254", "F254s", "ninguno"}:
            raise ValueError("placa.indicador debe ser 'F254', 'F254s' o 'ninguno'")


PLACAS: dict[str, Placa] = {
    "silice-60G-F254": Placa(
        id="silice-60G-F254",
        nombre="TLC Sílica 60G F254 (yeso) — la del laboratorio",
        catalogo="1.00390",
        modo="NP",
        grado="TLC",
        particula_um=(10.0, 12.0),
        espesor_um=250.0,
        humectable_agua=False,
        indicador="F254",
        zona_concentracion=False,
    ),
    "rp18-f254s": Placa(
        id="rp18-f254s",
        nombre="HPTLC Sílica 60 RP-18 F254s",
        catalogo="1.13724",
        modo="RP",
        grado="HPTLC",
        particula_um=(5.0, 6.0),
        espesor_um=200.0,
        humectable_agua=False,
        indicador="F254s",
        zona_concentracion=False,
    ),
    "rp18-w-f254s": Placa(
        id="rp18-w-f254s",
        nombre="HPTLC Sílica 60 RP-18 W F254s (humectable con agua)",
        catalogo="1.13124",
        modo="RP",
        grado="HPTLC",
        particula_um=(5.0, 6.0),
        espesor_um=200.0,
        humectable_agua=True,
        indicador="F254s",
        zona_concentracion=False,
    ),
    "rp18-zona-concentracion": Placa(
        id="rp18-zona-concentracion",
        nombre="HPTLC RP-18 F254s con zona de concentración 20 x 2,5 cm",
        catalogo="1.15498",
        modo="RP",
        grado="HPTLC",
        particula_um=(5.0, 6.0),
        espesor_um=200.0,
        humectable_agua=False,
        indicador="F254s",
        zona_concentracion=True,
    ),
    "silice-zona-concentracion": Placa(
        id="silice-zona-concentracion",
        nombre="TLC Sílica 60 F254 con zona de concentración 2,5 x 20 cm",
        catalogo="1.11798",
        modo="NP",
        grado="TLC",
        particula_um=(10.0, 12.0),
        espesor_um=250.0,
        humectable_agua=False,
        indicador="F254",
        zona_concentracion=True,
    ),
}
"""Catalogued plates. Specifications from EVIDENCIA['merck-placas']."""
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "$SN" && .venv/Scripts/python.exe -m pytest tests/test_hptlc.py -v`
Expected: PASS, 4 pruebas

- [ ] **Step 5: Commit**

```bash
git add evidencia.py hptlc.py tests/test_hptlc.py
git commit -m "feat: registro de evidencia y catalogo de placas HPTLC"
```

---

### Task 2: Factores, niveles de evidencia y veredicto

**Files:**
- Modify: `SN/hptlc.py`
- Test: `SN/tests/test_hptlc.py`

**Interfaces:**
- Consumes: `Placa`, `PLACAS`, `EVIDENCIA` (Task 1)
- Produces: `Nivel`, `Estado`, `Factor`, `Veredicto`, `evaluar_placa(props: dict, placa: Placa, volumen_uL: float, dilucion: float) -> Veredicto`

`props` es el dict que devuelve `model.calculate_nades_properties()`. Se usan solo tres
claves: `viscosidad` (cP), `water_pct` (%) y `pH`. No se importa `model`.

- [ ] **Step 1: Write the failing test**

```python
# añadir a SN/tests/test_hptlc.py
import pytest

from evidencia import EVIDENCIA, Nivel
from hptlc import PLACAS, Estado, evaluar_placa

PROPS_ACIDO = {"viscosidad": 120.0, "water_pct": 30.0, "pH": 3.1}


def test_fase_normal_reproduce_el_fracaso_publicado() -> None:
    v = evaluar_placa(PROPS_ACIDO, PLACAS["silice-60G-F254"], volumen_uL=4.0, dilucion=10.0)
    assert v.estado is Estado.REQUIERE_LIMPIEZA
    assert any(f.fuente_id == "quinoa2025" for f in v.factores)


def test_fase_reversa_nunca_sale_viable() -> None:
    for placa_id in ("rp18-f254s", "rp18-w-f254s", "rp18-zona-concentracion"):
        v = evaluar_placa(PROPS_ACIDO, PLACAS[placa_id], volumen_uL=2.0, dilucion=10.0)
        assert v.estado is not Estado.VIABLE, placa_id
        assert v.estado is Estado.SIN_EVIDENCIA, placa_id


def test_ningun_factor_emite_valor_sin_fuente_resoluble() -> None:
    for placa in PLACAS.values():
        v = evaluar_placa(PROPS_ACIDO, placa, volumen_uL=4.0, dilucion=10.0)
        for f in v.factores:
            if f.valor is not None:
                assert f.fuente_id in EVIDENCIA, f"{f.id} emite valor sin fuente"
            if f.nivel is Nivel.SIN_FUENTE:
                assert f.valor is None, f"{f.id} es SIN_FUENTE pero trae valor"


def test_los_vacios_se_declaran_y_no_se_rellenan() -> None:
    v = evaluar_placa(PROPS_ACIDO, PLACAS["rp18-w-f254s"], volumen_uL=2.0, dilucion=10.0)
    ids = {f.id for f in v.vacios}
    assert ids == {
        "cruce-nades-rp18",
        "umbral-viscosidad",
        "carga-tolerable",
        "revelado-sin-limpieza",
        "componentes-hptlc",
        "raspado-hplc",
        "obstruccion-aplicador",
    }
    assert all(f.valor is None for f in v.vacios)


def test_indicador_no_acido_con_nades_acido_produce_aviso() -> None:
    v = evaluar_placa(PROPS_ACIDO, PLACAS["silice-60G-F254"], volumen_uL=4.0, dilucion=10.0)
    aviso = next(f for f in v.factores if f.id == "indicador")
    assert "F254s" in aviso.texto
    assert aviso.fuente_id == "merck-placas"


def test_zona_de_concentracion_repone_el_enfoque_de_banda() -> None:
    sin_zona = evaluar_placa(PROPS_ACIDO, PLACAS["rp18-w-f254s"], 2.0, 10.0)
    con_zona = evaluar_placa(PROPS_ACIDO, PLACAS["rp18-zona-concentracion"], 2.0, 10.0)
    f_sin = next(f for f in sin_zona.factores if f.id == "enfoque-banda")
    f_con = next(f for f in con_zona.factores if f.id == "enfoque-banda")
    assert f_sin.fuente_id == "camag-linomat"
    assert f_con.fuente_id == "merck-zona"


def test_carga_no_volatil_se_compara_contra_el_punto_de_fracaso() -> None:
    v = evaluar_placa(PROPS_ACIDO, PLACAS["silice-60G-F254"], volumen_uL=4.0, dilucion=10.0)
    carga = next(f for f in v.factores if f.id == "carga-no-volatil")
    assert carga.valor == pytest.approx(0.4)
    assert carga.fuente_id == "quinoa2025"


def test_dilucion_invalida_es_error() -> None:
    with pytest.raises(ValueError):
        evaluar_placa(PROPS_ACIDO, PLACAS["rp18-w-f254s"], volumen_uL=2.0, dilucion=0.0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$SN" && .venv/Scripts/python.exe -m pytest tests/test_hptlc.py -v`
Expected: FAIL con `ImportError: cannot import name 'Estado' from 'hptlc'`

- [ ] **Step 3: Write minimal implementation**

Añadir al final de `SN/hptlc.py`:

```python
class Estado(str, Enum):
    """Verdict for one plate."""

    VIABLE = "VIABLE"
    REQUIERE_LIMPIEZA = "REQUIERE_LIMPIEZA"
    NO_VIABLE = "NO_VIABLE"
    SIN_EVIDENCIA = "SIN_EVIDENCIA"


@dataclass(frozen=True)
class Factor:
    """One evaluated aspect, with its evidence level and source."""

    id: str
    titulo: str
    nivel: Nivel
    texto: str
    fuente_id: str | None = None
    valor: float | None = None

    def __post_init__(self) -> None:
        """Enforce the project-wide rule: no value without a resolvable source."""
        if self.valor is not None and self.fuente_id not in EVIDENCIA:
            raise ValueError(f"factor '{self.id}' emite valor sin fuente resoluble")
        if self.nivel is Nivel.SIN_FUENTE and self.valor is not None:
            raise ValueError(f"factor '{self.id}' es SIN_FUENTE pero trae valor")


@dataclass(frozen=True)
class Veredicto:
    """Result of evaluating one plate against one NADES."""

    placa: Placa
    estado: Estado
    factores: tuple[Factor, ...]
    vacios: tuple[Factor, ...]


# El punto de fracaso publicado, en uL de NADES neto por banda: la quinoa aplicó
# 4-8 uL de extracto diluido 1/10 sobre sílica y aun así obtuvo colas severas.
FRACASO_NP_UL_NETO = (0.4, 0.8)


def _vacios_base() -> tuple[Factor, ...]:
    """Return the gaps that apply to every evaluation."""
    return (
        Factor(
            id="umbral-viscosidad",
            titulo="Umbral de dosificación del aplicador",
            nivel=Nivel.SIN_FUENTE,
            texto=(
                "El límite de viscosidad dosificable es una especificación del "
                "aplicador, no un dato de literatura. Consultar el manual del equipo."
            ),
        ),
        Factor(
            id="raspado-hplc",
            titulo="Raspado de banda y reinyección en HPLC",
            nivel=Nivel.SIN_FUENTE,
            texto=(
                "Sin fuente específica para NADES. Solo hay guía genérica de TLC "
                "preparativa. Pregunta abierta de la tesis."
            ),
        ),
        Factor(
            id="componentes-hptlc",
            titulo="Volatilidad e higroscopicidad por componente",
            nivel=Nivel.SIN_FUENTE,
            texto=(
                "No existe como tabla publicada para los 39 componentes del "
                "simulador. Requiere sourcear componente por componente."
            ),
        ),
        Factor(
            id="obstruccion-aplicador",
            titulo="Obstrucción de aguja y arrastre entre muestras",
            nivel=Nivel.SIN_FUENTE,
            texto=(
                "Sin fuente. No se afirma que un líquido viscoso no volátil tape la "
                "boquilla ni que contamine la muestra siguiente."
            ),
        ),
        Factor(
            id="carga-tolerable",
            titulo="Carga no volátil tolerable por banda",
            nivel=Nivel.SIN_FUENTE,
            texto=(
                "No hay valor publicado de cuánta matriz no volátil admite una banda "
                "antes de distorsionarse. Lo que sí hay es el punto de fracaso ajeno "
                "que el factor 'carga no volátil' usa como referencia."
            ),
        ),
        Factor(
            id="revelado-sin-limpieza",
            titulo="Interferencia en revelado sin limpieza previa",
            nivel=Nivel.SIN_FUENTE,
            texto=(
                "Lo documentado es que NP/PEG, DPPH y α-amilasa funcionan después de "
                "SPE. Sin SPE no hay dato."
            ),
        ),
    )


def evaluar_placa(
    props: dict,
    placa: Placa,
    volumen_uL: float,
    dilucion: float,
) -> Veredicto:
    """Evaluate direct spotting of a NADES extract on one plate.

    Args:
        props: Properties from `model.calculate_nades_properties`. Only
            `viscosidad`, `water_pct` and `pH` are read.
        placa: The catalogued plate to evaluate.
        volumen_uL: Volume applied per band, in microlitres.
        dilucion: Dilution factor of the extract (10.0 means 1/10).

    Returns:
        The verdict, with every factor carrying its evidence level.

    Raises:
        ValueError: If `dilucion` or `volumen_uL` are not positive.
    """
    if dilucion <= 0:
        raise ValueError("dilucion debe ser positiva")
    if volumen_uL <= 0:
        raise ValueError("volumen_uL debe ser positivo")

    factores: list[Factor] = []
    neto = volumen_uL / dilucion

    # F1 — carga no volátil, medida contra el punto de fracaso publicado
    bajo, alto = FRACASO_NP_UL_NETO
    factores.append(
        Factor(
            id="carga-no-volatil",
            titulo="Carga no volátil en el origen",
            nivel=Nivel.MEDIDO,
            fuente_id="quinoa2025",
            valor=round(neto, 3),
            texto=(
                f"Se depositan {neto:.2f} uL de NADES neto por banda. El punto de "
                f"fracaso publicado en fase normal está en {bajo}-{alto} uL netos, "
                "que produjo colas severas incluso a dilución 1/10."
            ),
        )
    )

    # F2 — viscosidad: obstáculo documentado, umbral sin fuente
    factores.append(
        Factor(
            id="viscosidad",
            titulo="Viscosidad efectiva",
            nivel=Nivel.MEDIDO,
            fuente_id="liu2017",
            valor=float(props["viscosidad"]),
            texto=(
                f"{props['viscosidad']:.0f} cP a la temperatura de trabajo. La alta "
                "viscosidad es uno de los dos obstáculos analíticos que la fuente "
                "primaria atribuye a los NADES."
            ),
        )
    )

    # F3 — enfoque de banda: el aplicador pierde su mecanismo, la zona lo repone
    if placa.zona_concentracion:
        factores.append(
            Factor(
                id="enfoque-banda",
                titulo="Enfoque de banda",
                nivel=Nivel.INFERIDO,
                fuente_id="merck-zona",
                texto=(
                    "La zona de concentración enfoca por migración cromatográfica en "
                    "el adsorbente inerte, no por evaporación, y el fabricante la "
                    "declara además como paso de limpieza para matrices complejas. "
                    "Es un mecanismo que sigue operando con matriz no volátil."
                ),
            )
        )
    else:
        factores.append(
            Factor(
                id="enfoque-banda",
                titulo="Enfoque de banda",
                nivel=Nivel.INFERIDO,
                fuente_id="camag-linomat",
                texto=(
                    "El spray-on forma banda angosta porque el disolvente se evapora "
                    "durante la aplicación. Un NADES no evapora, así que el mecanismo "
                    "de enfoque no opera sobre esa fracción: el aplicador dosifica un "
                    "volumen reproducible pero no lo convierte en banda estrecha."
                ),
            )
        )

    # F4 — el agua cambia de signo según el soporte
    agua = float(props["water_pct"])
    if placa.modo == "RP":
        factores.append(
            Factor(
                id="agua",
                titulo="Agua del NADES",
                nivel=Nivel.INFERIDO,
                fuente_id="jchemed2019",
                valor=agua,
                texto=(
                    f"{agua:.0f}% de agua. En fase reversa el agua es eluyente débil, "
                    "lo que se aprovecha para aplicar muestras acuosas como banda "
                    "estrecha: aquí el agua juega a favor."
                ),
            )
        )
    else:
        factores.append(
            Factor(
                id="agua",
                titulo="Agua del NADES",
                nivel=Nivel.MEDIDO,
                fuente_id="quinoa2025",
                valor=agua,
                texto=(
                    f"{agua:.0f}% de agua. En sílica el agua es eluyente fuerte y la "
                    "muestra polar se desparrama: aquí el agua juega en contra."
                ),
            )
        )

    # F5 — humectabilidad: solo tiene sentido en RP
    if placa.modo == "RP" and not placa.humectable_agua:
        factores.append(
            Factor(
                id="humectabilidad",
                titulo="Humectabilidad de la placa",
                nivel=Nivel.MEDIDO,
                fuente_id="merck-placas",
                texto=(
                    "Placa RP-18 sin el grado W. Con fases móviles muy acuosas conviene "
                    "la variante W, catalogada como completamente humectable con agua."
                ),
            )
        )

    # F6 — indicador frente a la acidez del NADES
    pH = float(props["pH"])
    if placa.indicador == "F254" and pH < 4.5:
        factores.append(
            Factor(
                id="indicador",
                titulo="Indicador de fluorescencia",
                nivel=Nivel.MEDIDO,
                fuente_id="merck-placas",
                texto=(
                    f"NADES ácido (pH {pH:.1f}) sobre placa F254. El catálogo ofrece "
                    "F254s, indicador estable a ácido, para justamente este caso."
                ),
            )
        )
    else:
        factores.append(
            Factor(
                id="indicador",
                titulo="Indicador de fluorescencia",
                nivel=Nivel.MEDIDO,
                fuente_id="merck-placas",
                texto=f"Indicador {placa.indicador} frente a un NADES de pH {pH:.1f}.",
            )
        )

    vacios = list(_vacios_base())
    if placa.modo == "RP":
        vacios.insert(
            0,
            Factor(
                id="cruce-nades-rp18",
                titulo="NADES sembrado directo en RP-18",
                nivel=Nivel.SIN_FUENTE,
                texto=(
                    "El fracaso publicado es en fase normal; el mecanismo favorable en "
                    "RP está publicado con muestras acuosas, no con NADES. El cruce no "
                    "existe en la literatura: es hipótesis a ensayar, no predicción."
                ),
            ),
        )
        estado = Estado.SIN_EVIDENCIA
    else:
        estado = Estado.REQUIERE_LIMPIEZA

    return Veredicto(
        placa=placa,
        estado=estado,
        factores=tuple(factores),
        vacios=tuple(vacios),
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "$SN" && .venv/Scripts/python.exe -m pytest tests/test_hptlc.py -v`
Expected: PASS, 12 pruebas

- [ ] **Step 5: Verificar que no arrastra Streamlit**

Run:
```bash
cd "$SN" && .venv/Scripts/python.exe -c "import sys; import hptlc; assert 'streamlit' not in sys.modules; print('limpio')"
```
Expected: `limpio`

- [ ] **Step 6: Commit**

```bash
git add hptlc.py tests/test_hptlc.py
git commit -m "feat: veredicto de siembra directa con nivel de evidencia por factor"
```

---

### Task 3: Protocolo candidato

**Files:**
- Modify: `SN/hptlc.py`
- Test: `SN/tests/test_hptlc.py`

**Interfaces:**
- Consumes: `Veredicto`, `Placa` (Task 2)
- Produces: `Protocolo`, `protocolo_candidato(veredicto: Veredicto) -> Protocolo`

- [ ] **Step 1: Write the failing test**

```python
# añadir a SN/tests/test_hptlc.py
from hptlc import protocolo_candidato


def test_protocolo_usa_el_volumen_de_farmacopea_segun_grado() -> None:
    v_tlc = evaluar_placa(PROPS_ACIDO, PLACAS["silice-60G-F254"], 4.0, 10.0)
    v_hptlc = evaluar_placa(PROPS_ACIDO, PLACAS["rp18-w-f254s"], 2.0, 10.0)
    assert protocolo_candidato(v_tlc).volumen_max_uL == 10.0
    assert protocolo_candidato(v_hptlc).volumen_max_uL == 2.0
    assert protocolo_candidato(v_tlc).fuente_volumen == "merck-placas"


def test_protocolo_en_fase_normal_exige_limpieza_previa() -> None:
    v = evaluar_placa(PROPS_ACIDO, PLACAS["silice-60G-F254"], 4.0, 10.0)
    p = protocolo_candidato(v)
    assert p.limpieza_previa is True
    assert "SPE" in p.notas


def test_protocolo_con_zona_de_concentracion_no_exige_spe() -> None:
    v = evaluar_placa(PROPS_ACIDO, PLACAS["rp18-zona-concentracion"], 2.0, 10.0)
    assert protocolo_candidato(v).limpieza_previa is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$SN" && .venv/Scripts/python.exe -m pytest tests/test_hptlc.py -k protocolo -v`
Expected: FAIL con `ImportError: cannot import name 'protocolo_candidato'`

- [ ] **Step 3: Write minimal implementation**

Añadir al final de `SN/hptlc.py`:

```python
# Volúmenes del ensayo de aptitud de Ph. Eur., por grado de placa.
VOLUMEN_PH_EUR_UL: dict[str, float] = {"TLC": 10.0, "HPTLC": 2.0}


@dataclass(frozen=True)
class Protocolo:
    """Candidate application protocol derived from a verdict."""

    volumen_max_uL: float
    fuente_volumen: str
    limpieza_previa: bool
    notas: str


def protocolo_candidato(veredicto: Veredicto) -> Protocolo:
    """Build the candidate protocol for a verdict.

    Args:
        veredicto: The evaluated verdict.

    Returns:
        The protocol, whose volume comes from the Ph. Eur. suitability test
        rather than from any threshold chosen by this module.
    """
    placa = veredicto.placa
    volumen = VOLUMEN_PH_EUR_UL[placa.grado]

    if placa.zona_concentracion:
        limpieza = False
        notas = (
            "La zona de concentración incorpora, según el fabricante, una etapa de "
            "purificación y concentración: se ensaya sin limpieza previa y se compara "
            "contra un blanco de NADES sin extracto."
        )
    elif placa.modo == "NP":
        limpieza = True
        notas = (
            "En fase normal la siembra directa está documentada como fracaso incluso a "
            "dilución 1/10. Se requiere SPE previa (cartucho polimérico tipo Strata-X)."
        )
    else:
        limpieza = False
        notas = (
            "Sin evidencia publicada para NADES en RP-18. Se ensaya como hipótesis: "
            "sembrar por duplicado con y sin SPE, y registrar el resultado en la "
            "bitácora para confrontar la hipótesis con la placa."
        )

    return Protocolo(
        volumen_max_uL=volumen,
        fuente_volumen="merck-placas",
        limpieza_previa=limpieza,
        notas=notas,
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "$SN" && .venv/Scripts/python.exe -m pytest tests/test_hptlc.py -v`
Expected: PASS, 15 pruebas

- [ ] **Step 5: Formato y linter**

Run: `cd "$SN" && .venv/Scripts/python.exe -m black hptlc.py tests/test_hptlc.py && .venv/Scripts/python.exe -m ruff check hptlc.py tests/test_hptlc.py`
Expected: reformateo si aplica, y `All checks passed!`

- [ ] **Step 6: Commit**

```bash
git add hptlc.py tests/test_hptlc.py
git commit -m "feat: protocolo candidato con volumen anclado en Ph. Eur."
```

---

# FASE 2 — La sección HPTLC en la UI

### Task 4: Renderizador de la sección

**Files:**
- Create: `SN/tabs/__init__.py`, `SN/tabs/hptlc_tab.py`
- Modify: `SN/app.py` (añadir la pestaña)
- Test: `SN/tests/test_hptlc_tab.py`

**Interfaces:**
- Consumes: `evaluar_placa`, `protocolo_candidato`, `PLACAS`, `Estado`, `Nivel` (Fase 1)
- Produces: `render_hptlc(props: dict) -> None`, `insignia(nivel: Nivel) -> str`, `color_estado(estado: Estado) -> str`

- [ ] **Step 1: Write the failing test**

```python
# SN/tests/test_hptlc_tab.py
from evidencia import Nivel
from hptlc import Estado


def test_insignia_por_nivel() -> None:
    from tabs.hptlc_tab import insignia

    assert insignia(Nivel.MEDIDO).startswith("🟩")
    assert insignia(Nivel.INFERIDO).startswith("🟨")
    assert insignia(Nivel.SIN_FUENTE).startswith("⬜")


def test_sin_evidencia_no_comparte_color_con_viable() -> None:
    from tabs.hptlc_tab import color_estado

    assert color_estado(Estado.SIN_EVIDENCIA) != color_estado(Estado.VIABLE)
    assert color_estado(Estado.SIN_EVIDENCIA) == "gray"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$SN" && .venv/Scripts/python.exe -m pytest tests/test_hptlc_tab.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'tabs'`

- [ ] **Step 3: Write minimal implementation**

```python
# SN/tabs/__init__.py
"""Streamlit tab renderers extracted from app.py."""
```

```python
# SN/tabs/hptlc_tab.py
"""HPTLC compatibility section.

Rendering only. All the reasoning lives in `hptlc.py`, which stays importable
without Streamlit.
"""

from __future__ import annotations

import streamlit as st

from evidencia import EVIDENCIA, Nivel
from hptlc import PLACAS, Estado, evaluar_placa, protocolo_candidato

_INSIGNIAS = {
    Nivel.MEDIDO: "🟩 MEDIDO",
    Nivel.INFERIDO: "🟨 INFERIDO",
    Nivel.SIN_FUENTE: "⬜ SIN FUENTE",
}

# SIN_EVIDENCIA es gris, no una gradación del verde: la incertidumbre no es una
# versión débil de "viable", es una categoría distinta.
_COLORES = {
    Estado.VIABLE: "green",
    Estado.REQUIERE_LIMPIEZA: "orange",
    Estado.NO_VIABLE: "red",
    Estado.SIN_EVIDENCIA: "gray",
}


def insignia(nivel: Nivel) -> str:
    """Return the badge label for an evidence level."""
    return _INSIGNIAS[nivel]


def color_estado(estado: Estado) -> str:
    """Return the Streamlit colour name for a verdict state."""
    return _COLORES[estado]


def render_hptlc(props: dict) -> None:
    """Render the HPTLC compatibility section for the active NADES."""
    st.markdown("### 🧫 Compatibilidad HPTLC")
    st.caption(
        "Ningún valor se emite sin fuente. Donde la literatura calla, el módulo "
        "declara el vacío en vez de rellenarlo."
    )

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        placa_id = st.selectbox(
            "Placa",
            options=list(PLACAS),
            format_func=lambda k: PLACAS[k].nombre,
            index=list(PLACAS).index("rp18-w-f254s"),
        )
    with col_b:
        volumen = st.number_input("Volumen por banda (µL)", 0.5, 20.0, 2.0, 0.5)
    with col_c:
        dilucion = st.number_input("Dilución (1 : n)", 1.0, 100.0, 10.0, 1.0)

    placa = PLACAS[placa_id]
    veredicto = evaluar_placa(props, placa, volumen, dilucion)
    protocolo = protocolo_candidato(veredicto)

    st.markdown(
        f"#### Veredicto: :{color_estado(veredicto.estado)}[{veredicto.estado.value}]"
    )
    st.caption(f"{placa.nombre} · cat. {placa.catalogo} · capa {placa.espesor_um:.0f} µm")

    for f in veredicto.factores:
        with st.expander(f"{insignia(f.nivel)} — {f.titulo}", expanded=False):
            st.write(f.texto)
            if f.fuente_id:
                fuente = EVIDENCIA[f.fuente_id]
                st.caption(f"Fuente: {fuente.cita}")
                st.caption(f"DOI: {fuente.doi}")

    st.markdown("#### Protocolo candidato")
    st.write(
        f"Volumen máximo por banda: **{protocolo.volumen_max_uL:.0f} µL** "
        f"(ensayo de aptitud Ph. Eur., grado {placa.grado})"
    )
    st.write(f"Limpieza previa: **{'sí' if protocolo.limpieza_previa else 'no'}**")
    st.info(protocolo.notas)

    st.markdown("#### Qué falta medir")
    st.caption("Esto es el diseño del próximo ensayo, no una carencia del módulo.")
    for f in veredicto.vacios:
        st.markdown(f"- **{f.titulo}** — {f.texto}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "$SN" && .venv/Scripts/python.exe -m pytest tests/test_hptlc_tab.py -v`
Expected: PASS, 2 pruebas

- [ ] **Step 5: Enganchar en app.py**

En `SN/app.py`, cambiar la línea 764 para abrir una novena pestaña:

```python
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs(
    [
        t("tab1"),
        t("tab2"),
        t("tab3"),
        t("tab4"),
        t("tab5"),
        t("tab6"),
        t("tab7"),
        t("tab8"),
        t("tab9"),
    ]
)
```

Añadir la etiqueta junto a las demás (cerca de la línea 188):

```python
    "tab9": {"es": "🧫 HPTLC", "en": "🧫 HPTLC"},
```

Y al final del archivo:

```python
# ══════════════════════════════════════════════════════════
# TAB 9 — COMPATIBILIDAD HPTLC
# ══════════════════════════════════════════════════════════
with tab9:
    from tabs.hptlc_tab import render_hptlc

    render_hptlc(props)
```

`props` es la variable que `app.py` ya tiene con el resultado de
`calculate_nades_properties`. Verificar su nombre exacto antes de escribir:
`grep -n "props = calculate_nades_properties" app.py`

- [ ] **Step 6: Verificar en el navegador**

Run: `cd "$SN" && .venv/Scripts/python.exe -m streamlit run app.py --server.headless true --server.port 8512`
Abrir `http://localhost:8512`, ir a la pestaña 🧫 HPTLC, comprobar que:
- La placa por defecto es RP-18 W F254s
- El veredicto sale gris `SIN_EVIDENCIA`
- Los cuatro vacíos aparecen listados
Detener con Ctrl+C.

- [ ] **Step 7: Commit**

```bash
git add tabs/ tests/test_hptlc_tab.py app.py
git commit -m "feat: seccion de compatibilidad HPTLC en la interfaz"
```

---

# FASE 3 — Bitácora experimental persistente

### Task 5: Persistencia de "Mis Datos"

**Files:**
- Create: `SN/experimentos.py`, `SN/tests/test_experimentos.py`
- Modify: `SN/app.py` (tab6, líneas 3475-3510)

**Interfaces:**
- Produces: `RUTA_BITACORA`, `COLUMNAS`, `cargar_bitacora(ruta: Path) -> pd.DataFrame`, `anexar_experimentos(df: pd.DataFrame, ruta: Path) -> pd.DataFrame`

- [ ] **Step 1: Write the failing test**

```python
# SN/tests/test_experimentos.py
from pathlib import Path

import pandas as pd

from experimentos import COLUMNAS, anexar_experimentos, cargar_bitacora


def _fila() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "fecha": "2026-09-02",
                "NADES": "ChCl:Ac.Citrico",
                "HBA": "Cloruro de Colina (ChCl)",
                "HBD": "Ácido Cítrico",
                "Ratio": "1:1",
                "Agua (%)": 30,
                "Temp (°C)": 40,
                "TPC_exp": 85.2,
                "placa": "rp18-w-f254s",
                "siembra_directa_ok": True,
                "notas": "sin cola visible",
            }
        ]
    )


def test_bitacora_vacia_devuelve_columnas_esperadas(tmp_path: Path) -> None:
    df = cargar_bitacora(tmp_path / "experimentos.csv")
    assert list(df.columns) == COLUMNAS
    assert df.empty


def test_lo_anexado_sobrevive_a_releer_el_archivo(tmp_path: Path) -> None:
    ruta = tmp_path / "experimentos.csv"
    anexar_experimentos(_fila(), ruta)
    recargado = cargar_bitacora(ruta)
    assert len(recargado) == 1
    assert recargado.iloc[0]["NADES"] == "ChCl:Ac.Citrico"
    assert bool(recargado.iloc[0]["siembra_directa_ok"]) is True


def test_anexar_dos_veces_acumula_no_reemplaza(tmp_path: Path) -> None:
    ruta = tmp_path / "experimentos.csv"
    anexar_experimentos(_fila(), ruta)
    anexar_experimentos(_fila(), ruta)
    assert len(cargar_bitacora(ruta)) == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$SN" && .venv/Scripts/python.exe -m pytest tests/test_experimentos.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'experimentos'`

- [ ] **Step 3: Write minimal implementation**

```python
# SN/experimentos.py
"""Persistent experimental log.

Results used to live in `st.session_state` and died with the session. They now
accumulate on disk so the parity plot grows across sessions and the RP-18
hypothesis can be confronted with what actually happened on the plate.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

RUTA_BITACORA = Path(__file__).parent / "data" / "experimentos.csv"

COLUMNAS = [
    "fecha",
    "NADES",
    "HBA",
    "HBD",
    "Ratio",
    "Agua (%)",
    "Temp (°C)",
    "TPC_exp",
    "placa",
    "siembra_directa_ok",
    "notas",
]


def cargar_bitacora(ruta: Path = RUTA_BITACORA) -> pd.DataFrame:
    """Load the experimental log, returning an empty frame if absent.

    Args:
        ruta: Path to the CSV log.

    Returns:
        The log with `COLUMNAS` as its columns, possibly empty.
    """
    if not ruta.exists():
        return pd.DataFrame(columns=COLUMNAS)
    df = pd.read_csv(ruta)
    for columna in COLUMNAS:
        if columna not in df.columns:
            df[columna] = pd.NA
    return df[COLUMNAS]


def anexar_experimentos(df: pd.DataFrame, ruta: Path = RUTA_BITACORA) -> pd.DataFrame:
    """Append rows to the log and persist it.

    Args:
        df: Rows to append. Missing columns are filled with NA.
        ruta: Path to the CSV log.

    Returns:
        The full log after appending.
    """
    ruta.parent.mkdir(parents=True, exist_ok=True)
    entrante = df.copy()
    for columna in COLUMNAS:
        if columna not in entrante.columns:
            entrante[columna] = pd.NA
    completo = pd.concat([cargar_bitacora(ruta), entrante[COLUMNAS]], ignore_index=True)
    completo.to_csv(ruta, index=False)
    return completo
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "$SN" && .venv/Scripts/python.exe -m pytest tests/test_experimentos.py -v`
Expected: PASS, 3 pruebas

- [ ] **Step 5: Conectar con tab6**

En `SN/app.py`, tras el bloque `st.session_state["exp_df"] = exp_df` (cerca de la línea 3517), añadir el botón que persiste:

```python
            from experimentos import anexar_experimentos, cargar_bitacora

            if st.button("💾 Guardar en la bitácora"):
                total = anexar_experimentos(exp_df)
                st.success(f"Bitácora actualizada: {len(total)} ensayos acumulados")

            bitacora = cargar_bitacora()
            if not bitacora.empty:
                st.markdown("#### Bitácora acumulada")
                st.dataframe(bitacora, use_container_width=True, hide_index=True)
```

Añadir `data/experimentos.csv` a `.gitignore` — es dato de laboratorio, no código:

```bash
echo "data/experimentos.csv" >> .gitignore
```

- [ ] **Step 6: Commit**

```bash
git add experimentos.py tests/test_experimentos.py app.py .gitignore
git commit -m "feat: bitacora experimental persistente entre sesiones"
```

---

# FASE 4 — La capa de explicación

El diagnóstico del autor: *"tiene referencias pero no explica el porqué de las
decisiones"*. Las fuentes ya están en la app, pero como nota al pie de los gráficos. Esta
fase las pega al número que justifican.

Reutiliza `evidencia.py` (Task 1), de modo que haya **un solo registro de fuentes** para el
módulo HPTLC y para la interpretación de propiedades.

### Task 6: `explicacion.py` — valor, lectura, porqué y fuente

**Files:**
- Create: `SN/explicacion.py`, `SN/tests/test_explicacion.py`
- Modify: `SN/evidencia.py` (tres fuentes nuevas)

**Interfaces:**
- Consumes: `Fuente`, `Nivel`, `EVIDENCIA` de `evidencia.py` (Task 1)
- Produces: `Lectura`, `explicar_propiedades(props: dict) -> tuple[Lectura, ...]`

- [ ] **Step 1: Write the failing test**

```python
# SN/tests/test_explicacion.py
from evidencia import EVIDENCIA
from explicacion import explicar_propiedades

PROPS = {
    "polaridad": 0.815,
    "viscosidad": 15.0,
    "pH": 4.17,
    "cap_hbd": 3.05,
    "antioxidant_nades": 0.53,
}


def test_devuelve_una_lectura_por_propiedad() -> None:
    lecturas = explicar_propiedades(PROPS)
    assert {lectura.clave for lectura in lecturas} == set(PROPS)


def test_cada_lectura_explica_por_que_importa_y_cita() -> None:
    for lectura in explicar_propiedades(PROPS):
        assert lectura.por_que, f"{lectura.clave} sin porque"
        assert lectura.fuente_id in EVIDENCIA, f"{lectura.clave} sin fuente resoluble"


def test_el_calificativo_cambia_con_el_valor() -> None:
    alta = explicar_propiedades({**PROPS, "polaridad": 0.95})
    baja = explicar_propiedades({**PROPS, "polaridad": 0.35})
    cal_alta = next(x for x in alta if x.clave == "polaridad").calificativo
    cal_baja = next(x for x in baja if x.clave == "polaridad").calificativo
    assert cal_alta != cal_baja


def test_ph_acido_se_lee_como_favorable_para_antocianinas() -> None:
    lecturas = explicar_propiedades({**PROPS, "pH": 3.0})
    lectura = next(x for x in lecturas if x.clave == "pH")
    assert "flavilio" in lectura.por_que.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$SN" && .venv/Scripts/python.exe -m pytest tests/test_explicacion.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'explicacion'`

- [ ] **Step 3: Añadir las tres fuentes a `evidencia.py`**

Estas referencias ya estaban en la app, al pie de los gráficos. Aquí pasan al registro
único para poder colgarlas de cada número.

```python
    "espino2016": Fuente(
        id="espino2016",
        cita=(
            "Espino M., de los Ángeles Fernández M., Gomez F.J.V., Silva M.F. (2016). "
            "Natural designer solvents for greening analytical chemistry. "
            "Talanta 162:412."
        ),
        doi="10.1016/j.talanta.2016.10.078",
        afirma=(
            "Modelo de extracción por polaridad, capacidad HBD y pH. Es la referencia "
            "que el simulador ya citaba al pie de los gráficos de índice EP."
        ),
    ),
    "dai2013": Fuente(
        id="dai2013",
        cita=(
            "Dai Y., van Spronsen J., Witkamp G.-J., Verpoorte R., Choi Y.H. (2013). "
            "Natural deep eutectic solvents as new potential media for green "
            "technology. Anal. Chim. Acta 766:61."
        ),
        doi="10.1016/j.aca.2012.12.019",
        afirma=(
            "Efecto del contenido de agua sobre la red supramolecular del NADES y sobre "
            "la estabilidad de los compuestos disueltos."
        ),
    ),
    "ruiz2024": Fuente(
        id="ruiz2024",
        cita=(
            "Ruiz A. et al. (2024). Calafate (Berberis microphylla G. Forst) "
            "populations from Chilean Patagonia exhibit similar structuring at the "
            "genetic and metabolic levels. Horticulturae 10:458."
        ),
        doi="10.3390/horticulturae10050458",
        afirma=(
            "Perfil de 28 polifenoles de Berberis microphylla por HPLC-DAD-ESI-MS/MS. "
            "Es la base de la fracción EP del simulador."
        ),
    ),
```

- [ ] **Step 4: Write minimal implementation**

```python
# SN/explicacion.py
"""Plain-language reading of each computed property.

The simulator already cited its sources, but as footnotes under charts: the number
and the reason it matters were never in the same place. This module pairs each
computed quantity with what its value means for Berberis polyphenols, and with the
source that backs the claim.

Imports neither Streamlit nor the model: it reads the properties dict and nothing else.
"""

from __future__ import annotations

from dataclasses import dataclass

from evidencia import EVIDENCIA, Nivel


@dataclass(frozen=True)
class Lectura:
    """One property, read in plain language and backed by a source."""

    clave: str
    titulo: str
    valor: float
    unidad: str
    calificativo: str
    por_que: str
    fuente_id: str
    nivel: Nivel

    def __post_init__(self) -> None:
        """Keep the project-wide rule: no claim without a resolvable source."""
        if self.fuente_id not in EVIDENCIA:
            raise ValueError(f"lectura '{self.clave}' sin fuente resoluble")


def _tramo(
    valor: float, bajo: float, alto: float, etiquetas: tuple[str, str, str]
) -> str:
    """Return the qualitative label for a value against two cut points."""
    if valor < bajo:
        return etiquetas[0]
    if valor > alto:
        return etiquetas[2]
    return etiquetas[1]


def explicar_propiedades(props: dict) -> tuple[Lectura, ...]:
    """Read the five NADES properties in plain language.

    Args:
        props: Output of `model.calculate_nades_properties`.

    Returns:
        One `Lectura` per property, each carrying its source.
    """
    return (
        Lectura(
            clave="polaridad",
            titulo="Polaridad (ETN)",
            valor=float(props["polaridad"]),
            unidad="",
            calificativo=_tramo(
                float(props["polaridad"]), 0.45, 0.80, ("baja", "media", "alta")
            ),
            por_que=(
                "Las antocianinas 3-glicosiladas del calafate son muy polares: el azúcar "
                "unido al flavilio las lleva hacia la fracción acuosa. Un NADES de "
                "polaridad alta las solvata mejor, pero se aleja de los flavonoles, que "
                "son menos polares. Por eso el óptimo no es el máximo, y por eso el "
                "score combinado penaliza la asimetría entre fracciones."
            ),
            fuente_id="espino2016",
            nivel=Nivel.MEDIDO,
        ),
        Lectura(
            clave="viscosidad",
            titulo="Viscosidad",
            valor=float(props["viscosidad"]),
            unidad="cP",
            calificativo=_tramo(
                float(props["viscosidad"]), 50.0, 200.0, ("baja", "media", "alta")
            ),
            por_que=(
                "La viscosidad gobierna la difusión del soluto desde la matriz vegetal: "
                "más viscoso extrae más lento y satura antes, y por eso el agua añadida "
                "sube el rendimiento aunque baje la polaridad relativa del solvente. Es "
                "además uno de los dos obstáculos que la literatura atribuye a los NADES "
                "en el análisis posterior por capa fina."
            ),
            fuente_id="liu2017",
            nivel=Nivel.MEDIDO,
        ),
        Lectura(
            clave="pH",
            titulo="pH efectivo",
            valor=float(props["pH"]),
            unidad="",
            calificativo=_tramo(
                float(props["pH"]), 3.5, 5.5, ("muy ácido", "ácido", "cercano a neutro")
            ),
            por_que=(
                "El pH decide en qué forma está la antocianina. Bajo pH 3 domina el "
                "catión flavilio, rojo y estable; sobre pH 4 aparecen la pseudobase "
                "carbinol y la chalcona, incoloras y lábiles. Un NADES ácido no solo "
                "extrae el pigmento: lo mantiene en la forma que se puede medir."
            ),
            fuente_id="espino2016",
            nivel=Nivel.MEDIDO,
        ),
        Lectura(
            clave="cap_hbd",
            titulo="Capacidad HBD efectiva",
            valor=float(props["cap_hbd"]),
            unidad="",
            calificativo=_tramo(
                float(props["cap_hbd"]), 1.5, 3.0, ("baja", "media", "alta")
            ),
            por_que=(
                "Los donadores de puente de hidrógeno del solvente compiten con la pared "
                "celular por los hidroxilos fenólicos. Más capacidad HBD libera más "
                "polifenol unido a la matriz, que es justamente el mecanismo detrás de "
                "la fracción no extraíble (NEP)."
            ),
            fuente_id="espino2016",
            nivel=Nivel.MEDIDO,
        ),
        Lectura(
            clave="antioxidant_nades",
            titulo="Antioxidante del NADES",
            valor=float(props["antioxidant_nades"]),
            unidad="",
            calificativo=_tramo(
                float(props["antioxidant_nades"]), 0.25, 0.55, ("bajo", "medio", "alto")
            ),
            por_que=(
                "En este trabajo el NADES sustituye a la atmósfera inerte: el "
                "laboratorio no tiene línea de nitrógeno, y la hipótesis es que la red "
                "supramolecular del solvente aporta por sí sola la protección frente a "
                "oxidación. Este número es esa hipótesis, cuantificada."
            ),
            fuente_id="dai2013",
            nivel=Nivel.INFERIDO,
        ),
    )
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd "$SN" && .venv/Scripts/python.exe -m pytest tests/test_explicacion.py -v`
Expected: PASS, 4 pruebas

- [ ] **Step 6: Commit**

```bash
git add explicacion.py evidencia.py tests/test_explicacion.py
git commit -m "feat: capa de explicacion que pega cada fuente al numero que justifica"
```

---

### Task 7: Ficha explicada en lugar de `prop_card`

**Files:**
- Create: `SN/tabs/componentes.py`, `SN/tests/test_componentes.py`
- Modify: `SN/app.py:694-707`

**Interfaces:**
- Consumes: `Lectura` (Task 6), `Nivel`, `EVIDENCIA` (Task 1)
- Produces: `ficha_explicada(lectura: Lectura) -> None`, `texto_ficha(lectura: Lectura) -> str`

- [ ] **Step 1: Write the failing test**

```python
# SN/tests/test_componentes.py
from evidencia import Nivel
from explicacion import Lectura


def _lectura() -> Lectura:
    return Lectura(
        clave="polaridad",
        titulo="Polaridad (ETN)",
        valor=0.815,
        unidad="",
        calificativo="alta",
        por_que="Las antocianinas glicosiladas son muy polares.",
        fuente_id="espino2016",
        nivel=Nivel.MEDIDO,
    )


def test_el_texto_muestra_valor_y_calificativo_juntos() -> None:
    from tabs.componentes import texto_ficha

    texto = texto_ficha(_lectura())

    assert "0.815" in texto
    assert "alta" in texto
    assert "Polaridad" in texto
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$SN" && .venv/Scripts/python.exe -m pytest tests/test_componentes.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'tabs.componentes'`

- [ ] **Step 3: Write minimal implementation**

```python
# SN/tabs/componentes.py
"""Shared display components.

The explained card replaces `prop_card`: a bare number in a coloured box told the
user what the value was, but never why it mattered nor who says so.
"""

from __future__ import annotations

import streamlit as st

from evidencia import EVIDENCIA, Nivel
from explicacion import Lectura

_INSIGNIAS = {
    Nivel.MEDIDO: "🟩",
    Nivel.INFERIDO: "🟨",
    Nivel.SIN_FUENTE: "⬜",
}


def texto_ficha(lectura: Lectura) -> str:
    """Return the one-line headline for a reading."""
    unidad = f" {lectura.unidad}" if lectura.unidad else ""
    return f"{lectura.titulo}: {lectura.valor:g}{unidad} — {lectura.calificativo}"


def ficha_explicada(lectura: Lectura) -> None:
    """Render one reading with its value, its meaning and its source."""
    unidad = f" {lectura.unidad}" if lectura.unidad else ""
    st.metric(lectura.titulo, f"{lectura.valor:g}{unidad}", lectura.calificativo)
    with st.expander("¿Por qué importa?", expanded=False):
        st.write(lectura.por_que)
        fuente = EVIDENCIA[lectura.fuente_id]
        st.caption(f"{_INSIGNIAS[lectura.nivel]} {fuente.cita}")
        st.caption(f"DOI: {fuente.doi}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "$SN" && .venv/Scripts/python.exe -m pytest tests/test_componentes.py -v`
Expected: PASS, 1 prueba

- [ ] **Step 5: Reemplazar `prop_card` en el panel lateral**

En `SN/app.py`, sustituir las líneas 694-707 (la definición de `prop_card` y sus cinco
llamadas) por:

```python
    from explicacion import explicar_propiedades
    from tabs.componentes import ficha_explicada

    for lectura in explicar_propiedades(props):
        ficha_explicada(lectura)
```

- [ ] **Step 6: Commit**

```bash
git add tabs/componentes.py tests/test_componentes.py app.py
git commit -m "feat: ficha explicada con porque y fuente en vez de prop_card"
```

---

# FASE 5 — Dos pestañas y una sola fuente de verdad

Se descarta la agrupación en tres etapas del spec §7: creaba **etapa → pestaña →
sub-pestaña**, tres niveles de profundidad, y habría añadido un clic para llegar a todo.
La guía de UX consultada marca los 3+ niveles como el punto donde hace falta indicar la
ubicación del usuario; la respuesta correcta es reducir niveles, no señalizarlos.

### Task 8: Franja de NADES activo y dos pestañas

**Files:**
- Modify: `SN/app.py` (etiquetas cerca de 181, construcción de pestañas en 764)
- Modify: `SN/tabs/componentes.py`
- Create: `SN/tests/test_navegacion.py`

**Interfaces:**
- Consumes: `texto_ficha` (Task 7)
- Produces: `nades_activo(props: dict, hba: str, hbd: str, ratio: str) -> str`

- [ ] **Step 1: Write the failing test**

```python
# SN/tests/test_navegacion.py
def test_la_franja_nombra_el_nades_activo_con_sus_condiciones() -> None:
    from tabs.componentes import nades_activo

    texto = nades_activo(
        {"water_pct": 30, "temp_C": 40},
        hba="Cloruro de Colina (ChCl)",
        hbd="Ácido Ascórbico (Vit. C)",
        ratio="1:1",
    )

    assert "Cloruro de Colina" in texto
    assert "Ácido Ascórbico" in texto
    assert "1:1" in texto
    assert "30" in texto
    assert "40" in texto
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$SN" && .venv/Scripts/python.exe -m pytest tests/test_navegacion.py -v`
Expected: FAIL con `ImportError: cannot import name 'nades_activo'`

- [ ] **Step 3: Write minimal implementation**

Añadir a `SN/tabs/componentes.py`:

```python
def nades_activo(props: dict, hba: str, hbd: str, ratio: str) -> str:
    """Return the one-line description of the mixture currently being shown."""
    return (
        f"{hba} : {hbd} ({ratio}, {props['water_pct']:.0f}% H₂O, "
        f"{props['temp_C']:.0f} °C)"
    )
```

- [ ] **Step 4: Añadir las etiquetas de las dos pestañas**

En `SN/app.py`, junto a las etiquetas existentes (cerca de la línea 181):

```python
    "nav_disenar": {"es": "🧪 Diseñar", "en": "🧪 Design"},
    "nav_lab": {"es": "🔬 Laboratorio", "en": "🔬 Laboratory"},
```

- [ ] **Step 5: Reemplazar la construcción de pestañas**

Antes de escribir, confirmar los nombres reales de las variables del panel lateral:

```bash
grep -n "hba_sel\|hbd_sel\|ratio_sel\|selectbox" app.py | head -10
```

Sustituir el bloque de la línea 764 por, usando los nombres reales:

```python
from tabs.componentes import nades_activo

st.info(f"**NADES activo** · {nades_activo(props, hba_sel, hbd_sel, ratio_sel)}")

nav_disenar, nav_lab = st.tabs([t("nav_disenar"), t("nav_lab")])

with nav_disenar:
    tab7, tab1, tab2, tab4, tab5 = st.tabs(
        [t("tab7"), t("tab1"), t("tab2"), t("tab4"), t("tab5")]
    )

with nav_lab:
    tab3, tab9, tab6, tab8 = st.tabs([t("tab3"), t("tab9"), t("tab6"), t("tab8")])
```

- [ ] **Step 6: Verificar en el navegador**

Run: `cd "$SN" && .venv/Scripts/python.exe -m streamlit run app.py --server.headless true --server.port 8512`
Comprobar: la franja de NADES activo aparece sobre las pestañas y cambia al mover el panel
lateral. Dos pestañas, un solo nivel de sub-pestañas. Detener con Ctrl+C.

- [ ] **Step 7: Commit**

```bash
git add app.py tabs/componentes.py tests/test_navegacion.py
git commit -m "refactor: dos pestanas y franja de NADES activo"
```

---

### Task 9: El Recomendador escribe el NADES activo

**Files:**
- Modify: `SN/app.py` (sub-pestaña del Recomendador Global, cerca de 4307)

- [ ] **Step 1: Localizar el DataFrame del ranking**

Run: `grep -n "ranking\|df_rank\|top_nades\|sweep_all_nades" app.py | head -10`
Anotar el nombre real de la variable; abajo se la llama `ranking_df`.

- [ ] **Step 2: Añadir el adoptador tras la tabla del ranking**

Hoy el ranking lista los mejores NADES pero no hay forma de adoptarlos: hay que copiar
HBA, HBD, razón y agua a mano al panel lateral. Ese copiado manual es la queja principal,
y es también la razón de que convivan dos fuentes de verdad sobre cuál es el NADES activo.

```python
        st.markdown("#### Adoptar uno de estos")
        elegido = st.selectbox(
            "NADES del ranking",
            options=list(range(len(ranking_df))),
            format_func=lambda i: (
                f"#{i + 1} · {ranking_df.iloc[i]['HBA']} : "
                f"{ranking_df.iloc[i]['HBD']} ({ranking_df.iloc[i]['Ratio']})"
            ),
        )
        if st.button("✅ Usar este NADES", type="primary"):
            fila = ranking_df.iloc[elegido]
            st.session_state["sel_hba"] = str(fila["HBA"])
            st.session_state["sel_hbd"] = str(fila["HBD"])
            st.session_state["sel_ratio"] = str(fila["Ratio"])
            st.rerun()
```

- [ ] **Step 3: Enganchar el panel lateral a `session_state`**

Los `st.selectbox` del panel lateral que eligen HBA, HBD y razón deben recibir
`key="sel_hba"`, `key="sel_hbd"` y `key="sel_ratio"` respectivamente, para que el botón
anterior los sobrescriba.

- [ ] **Step 4: Verificar el ciclo completo**

Run: `cd "$SN" && .venv/Scripts/python.exe -m streamlit run app.py --server.headless true --server.port 8512`
En Diseñar → Recomendador, elegir el #1 del ranking y pulsar "Usar este NADES". Comprobar
que la franja superior cambia y que las demás sub-pestañas muestran ese NADES.
Detener con Ctrl+C.

- [ ] **Step 5: Commit**

```bash
git add app.py
git commit -m "feat: el recomendador escribe el NADES activo en vez de solo listarlo"
```

---

# FASE 6 — Tema visual y movimiento

Patrón elegido: **Data-Dense + Drill-Down**, que es lo que ya hacen la franja fija y el
desplegable "¿Por qué importa?". La paleta no se toma del recomendador genérico —era azul
corporativo— sino de la identidad que el programa ya tiene: el morado del calafate y el
turquesa del disolvente, los mismos del icono en `assets/simextract.ico`.

Se aparta a conciencia de dos reglas de la guía: se conservan los emoji como iconos,
porque en Streamlit sustituirlos por SVG es peleado y la app ya es coherente con ellos; y
la monoespaciada se reserva para **cifras**, donde alinea columnas, en vez de para títulos.

### Task 10: Tema y animaciones respetuosas del movimiento

**Files:**
- Create: `SN/tema.py`, `SN/tests/test_tema.py`
- Modify: `SN/app.py` (llamada tras `st.set_page_config`)

**Interfaces:**
- Produces: `PALETA: dict[str, str]`, `css() -> str`, `inyectar_tema() -> None`

- [ ] **Step 1: Write the failing test**

```python
# SN/tests/test_tema.py
import re

from tema import PALETA, css


def test_la_paleta_es_la_del_calafate_no_azul_generico() -> None:
    assert PALETA["primario"] == "#4A2A7A"
    assert PALETA["acento"] == "#60CDD6"


def test_toda_animacion_queda_bajo_prefers_reduced_motion() -> None:
    hoja = css()
    assert "prefers-reduced-motion: no-preference" in hoja
    # Ninguna transicion ni animacion puede vivir fuera de esa consulta.
    fuera = hoja.split("@media (prefers-reduced-motion: no-preference)")[0]
    assert "transition:" not in fuera
    assert "animation:" not in fuera


def test_las_transiciones_estan_en_la_ventana_recomendada() -> None:
    duraciones = [int(x) for x in re.findall(r"(\d+)ms", css())]
    assert duraciones, "no se declaro ninguna duracion"
    assert all(150 <= d <= 300 for d in duraciones), duraciones


def test_el_texto_principal_es_oscuro_para_contraste() -> None:
    assert PALETA["texto"] == "#1E1633"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$SN" && .venv/Scripts/python.exe -m pytest tests/test_tema.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'tema'`

- [ ] **Step 3: Write minimal implementation**

```python
# SN/tema.py
"""Visual theme.

Palette taken from the product's own identity — the calafate purple and the solvent
teal of `assets/simextract.ico` — rather than from a generic dashboard blue.

Every transition and keyframe lives inside a `prefers-reduced-motion: no-preference`
query, so a user who asked their system for less movement gets none: motion is an
enhancement here, never a carrier of information.
"""

from __future__ import annotations

import streamlit as st

PALETA: dict[str, str] = {
    "primario": "#4A2A7A",
    "primario_claro": "#8A5CBA",
    "acento": "#60CDD6",
    "llamada": "#F59E0B",
    "fondo": "#F8FAFC",
    "superficie": "#FFFFFF",
    "texto": "#1E1633",
    "texto_tenue": "#475569",
    "borde": "#E2E8F0",
}
"""Calafate purple over a near-white ground, teal for accents, amber for actions."""

_DURACION_MS = 180


def css() -> str:
    """Return the stylesheet injected into the app."""
    p = PALETA
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Sans:wght@300;400;500;600;700&family=Fira+Code:wght@400;500&display=swap');

:root {{
    --sn-primario: {p["primario"]};
    --sn-primario-claro: {p["primario_claro"]};
    --sn-acento: {p["acento"]};
    --sn-llamada: {p["llamada"]};
    --sn-superficie: {p["superficie"]};
    --sn-texto: {p["texto"]};
    --sn-texto-tenue: {p["texto_tenue"]};
    --sn-borde: {p["borde"]};
}}

html, body, [class*="css"] {{
    font-family: 'Fira Sans', system-ui, -apple-system, sans-serif;
    color: var(--sn-texto);
}}

h1, h2, h3, h4 {{
    font-family: 'Fira Sans', system-ui, sans-serif;
    font-weight: 600;
    letter-spacing: -0.01em;
    color: var(--sn-primario);
}}

/* Monoespaciada solo para cifras: alinea columnas y digitos entre filas. */
[data-testid="stMetricValue"] {{
    font-family: 'Fira Code', ui-monospace, monospace;
    font-variant-numeric: tabular-nums;
    color: var(--sn-primario);
}}

[data-testid="stMetric"] {{
    background: var(--sn-superficie);
    border: 1px solid var(--sn-borde);
    border-left: 3px solid var(--sn-acento);
    border-radius: 8px;
    padding: 0.75rem 1rem;
}}

.stTabs [data-baseweb="tab"] {{
    font-weight: 500;
}}

.stTabs [aria-selected="true"] {{
    color: var(--sn-primario);
    border-bottom-color: var(--sn-primario);
}}

.stButton > button {{
    border-radius: 8px;
    font-weight: 500;
}}

/* El cursor debe decir que algo se puede pulsar. */
.stButton > button,
.stTabs [data-baseweb="tab"],
[data-testid="stExpander"] summary {{
    cursor: pointer;
}}

/* Foco visible: la navegacion por teclado no puede quedarse a ciegas. */
.stButton > button:focus-visible,
[data-testid="stExpander"] summary:focus-visible {{
    outline: 2px solid var(--sn-acento);
    outline-offset: 2px;
}}

@media (prefers-reduced-motion: no-preference) {{
    [data-testid="stMetric"] {{
        transition: border-left-color {_DURACION_MS}ms ease,
                    box-shadow {_DURACION_MS}ms ease;
    }}
    [data-testid="stMetric"]:hover {{
        border-left-color: var(--sn-primario);
        box-shadow: 0 2px 12px rgba(74, 42, 122, 0.12);
    }}

    .stButton > button {{
        transition: background-color {_DURACION_MS}ms ease,
                    transform {_DURACION_MS}ms ease;
    }}
    /* Se mueve con transform, no con width/height: no reflow, no salto de layout. */
    .stButton > button:hover {{
        transform: translateY(-1px);
    }}

    .stTabs [data-baseweb="tab"] {{
        transition: color {_DURACION_MS}ms ease;
    }}

    [data-testid="stDataFrame"] tbody tr {{
        transition: background-color {_DURACION_MS}ms ease;
    }}
    [data-testid="stDataFrame"] tbody tr:hover {{
        background-color: rgba(96, 205, 214, 0.10);
    }}

    @keyframes sn-entrada {{
        from {{ opacity: 0; transform: translateY(6px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
    [data-testid="stMetric"],
    [data-testid="stAlert"] {{
        animation: sn-entrada {_DURACION_MS}ms ease-out;
    }}
}}
</style>
"""


def inyectar_tema() -> None:
    """Inject the stylesheet. Call once, right after `st.set_page_config`."""
    st.markdown(css(), unsafe_allow_html=True)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "$SN" && .venv/Scripts/python.exe -m pytest tests/test_tema.py -v`
Expected: PASS, 4 pruebas

- [ ] **Step 5: Enganchar en `app.py`**

Justo después de la llamada a `st.set_page_config(...)`:

```python
from tema import inyectar_tema

inyectar_tema()
```

- [ ] **Step 6: Comprobar el contraste**

El texto principal `#1E1633` sobre fondo `#F8FAFC` supera con holgura el 4.5:1 que exige
WCAG AA. Verificarlo:

```bash
cd "$SN" && .venv/Scripts/python.exe -c "
def lum(h):
    c = [int(h[i:i+2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
a, b = lum('#1E1633'), lum('#F8FAFC')
print('contraste texto/fondo:', round((max(a, b) + 0.05) / (min(a, b) + 0.05), 2))
a = lum('#4A2A7A')
print('contraste primario/fondo:', round((max(a, b) + 0.05) / (min(a, b) + 0.05), 2))
"
```
Expected: ambos por encima de 4.5

- [ ] **Step 7: Verificar en el navegador y con movimiento reducido**

Run: `cd "$SN" && .venv/Scripts/python.exe -m streamlit run app.py --server.headless true --server.port 8512`
Comprobar el hover de fichas, botones y filas de tabla. Luego activar "reducir movimiento"
en Windows (Configuración → Accesibilidad → Efectos visuales → Efectos de animación:
desactivado), recargar, y comprobar que no queda ninguna animación. Detener con Ctrl+C.

- [ ] **Step 8: Commit**

```bash
git add tema.py tests/test_tema.py app.py
git commit -m "feat: tema de calafate con movimiento sujeto a prefers-reduced-motion"
```

---
# FASE 7 — SimEluent: catálogo de placas

### Task 11: `Phase` extendida y `data/placas.csv`

**Files:**
- Create: `SE/data/placas.csv`
- Modify: `SE/engine/data_loader.py`, `SE/engine/constants.py`
- Test: `SE/tests/test_data_loader.py`

**Interfaces:**
- Produces: `Phase` con `particula_um_min`, `particula_um_max`, `espesor_um`, `humectable_agua`, `indicador`, `zona_concentracion`; `load_phases(path: Path) -> dict[str, Phase]`

- [ ] **Step 1: Write the failing test**

```python
# añadir a SE/tests/test_data_loader.py
def test_load_phases_lee_el_catalogo_de_placas() -> None:
    from pathlib import Path

    from engine.data_loader import load_phases

    fases = load_phases(Path("data/placas.csv"))
    assert "rp18-w-f254s" in fases
    rp_w = fases["rp18-w-f254s"]
    assert rp_w.mode == "RP"
    assert rp_w.humectable_agua is True
    assert rp_w.indicador == "F254s"
    assert rp_w.particula_um_min == 5.0


def test_placa_tlc_y_hptlc_difieren_en_particula() -> None:
    from pathlib import Path

    from engine.data_loader import load_phases

    fases = load_phases(Path("data/placas.csv"))
    assert fases["silice-60G-F254"].particula_um_min == 10.0
    assert fases["rp18-f254s"].particula_um_min == 5.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$SE" && python -m pytest tests/test_data_loader.py -k phases -v`
Expected: FAIL con `ImportError: cannot import name 'load_phases'`

- [ ] **Step 3: Crear el catálogo**

```csv
# SE/data/placas.csv
id,nombre,catalogo,modo,grado,particula_um_min,particula_um_max,espesor_um,humectable_agua,indicador,zona_concentracion,w_spec
silice-60G-F254,TLC Silica 60G F254 (yeso),1.00390,NP,TLC,10.0,12.0,250.0,0,F254,0,0.95
rp18-f254s,HPTLC Silica 60 RP-18 F254s,1.13724,RP,HPTLC,5.0,6.0,200.0,0,F254s,0,0.90
rp18-w-f254s,HPTLC Silica 60 RP-18 W F254s,1.13124,RP,HPTLC,5.0,6.0,200.0,1,F254s,0,0.90
rp18-zona-concentracion,HPTLC RP-18 F254s con zona de concentracion,1.15498,RP,HPTLC,5.0,6.0,200.0,0,F254s,1,0.90
silice-zona-concentracion,TLC Silica 60 F254 con zona de concentracion,1.11798,NP,TLC,10.0,12.0,250.0,0,F254,1,0.95
```

- [ ] **Step 4: Extender `Phase` y añadir el loader**

En `SE/engine/data_loader.py`, sustituir la clase `Phase` (líneas 40-52) por:

```python
@dataclass(frozen=True)
class Phase:
    """Stationary phase configuration for eq (28).

    The plate specification fields come from the Merck catalogue. `particula_um_*`
    feeds the base plate count of eq (17) via docs/02 variable 8; `humectable_agua`
    and `indicador` gate eluent compatibility, which the three-field version of this
    dataclass could not express.
    """

    name: str
    mode: str
    w_spec: float
    catalogo: str = ""
    grado: str = "HPTLC"
    particula_um_min: float = 5.0
    particula_um_max: float = 6.0
    espesor_um: float = 200.0
    humectable_agua: bool = False
    indicador: str = "F254s"
    zona_concentracion: bool = False

    def __post_init__(self) -> None:
        """Validate stationary phase mode and spectral weight."""
        if self.mode not in {"NP", "RP"}:
            raise ValueError("phase.mode must be 'NP' or 'RP'")
        if not 0 < self.w_spec <= 1:
            raise ValueError("phase.w_spec must be in (0, 1]")
        if self.grado not in {"TLC", "HPTLC"}:
            raise ValueError("phase.grado must be 'TLC' or 'HPTLC'")
```

Añadir al final del mismo archivo, siguiendo el patrón de `load_solvents`:

```python
PHASE_COLUMNS = [
    "id",
    "nombre",
    "catalogo",
    "modo",
    "grado",
    "particula_um_min",
    "particula_um_max",
    "espesor_um",
    "humectable_agua",
    "indicador",
    "zona_concentracion",
    "w_spec",
]


def load_phases(path: Path) -> dict[str, Phase]:
    """Load the plate catalogue from `data/placas.csv`."""
    data = _read_csv(path, PHASE_COLUMNS)
    phases: dict[str, Phase] = {}
    for row in data.itertuples(index=False):
        phase = Phase(
            name=str(row.id),
            mode=str(row.modo),
            w_spec=float(row.w_spec),
            catalogo=str(row.catalogo),
            grado=str(row.grado),
            particula_um_min=float(row.particula_um_min),
            particula_um_max=float(row.particula_um_max),
            espesor_um=float(row.espesor_um),
            humectable_agua=bool(int(row.humectable_agua)),
            indicador=str(row.indicador),
            zona_concentracion=bool(int(row.zona_concentracion)),
        )
        phases[phase.name] = phase
    return phases
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd "$SE" && python -m pytest -q`
Expected: PASS, toda la suite (las fases por defecto de `constants.py` siguen válidas
porque los campos nuevos tienen valor por defecto)

- [ ] **Step 6: Commit**

```bash
git add data/placas.csv engine/data_loader.py tests/test_data_loader.py
git commit -m "feat: catalogo de placas con especificaciones de fabricante"
```

---

# FASE 8 — SimEluent: σ₀ deja de ser determinista

### Task 12: Régimen de σ₀ según veredicto

**Files:**
- Create: `SE/engine/sigma0.py`, `SE/tests/test_sigma0.py`

**Interfaces:**
- Produces: `RegimenSigma0`, `regimen_sigma0(estado: str, zona_concentracion: bool) -> RegimenSigma0`

- [ ] **Step 1: Write the failing test**

```python
# SE/tests/test_sigma0.py
from engine.sigma0 import regimen_sigma0


def test_muestra_limpia_conserva_el_supuesto_determinista() -> None:
    r = regimen_sigma0("LIMPIA", zona_concentracion=False)
    assert r.mu == 1.0
    assert r.sigma == 0.0
    assert r.determinista is True


def test_sin_evidencia_deja_de_ser_determinista() -> None:
    r = regimen_sigma0("SIN_EVIDENCIA", zona_concentracion=False)
    assert r.determinista is False
    assert r.sigma > 0.0


def test_la_zona_de_concentracion_restituye_el_determinismo() -> None:
    r = regimen_sigma0("SIN_EVIDENCIA", zona_concentracion=True)
    assert r.determinista is True
    assert r.sigma == 0.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$SE" && python -m pytest tests/test_sigma0.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'engine.sigma0'`

- [ ] **Step 3: Write minimal implementation**

```python
# SE/engine/sigma0.py
"""Initial band width regime.

docs/02 declares sample application deterministic because the automatic applicator
gives a reproducible sigma0, and rests the model's defensibility on that. The
spray-on technique produces a narrow band because the solvent evaporates during
application (CAMAG); a NADES has negligible vapour pressure (Liu et al. 2017,
DOI 10.1016/j.chroma.2017.12.009), so that focusing step does not operate on the
NADES fraction.

The defensible claim is not that sigma0 blows up on RP-18 — nobody has measured
that. It is that sigma0 stops being deterministic and becomes matrix-dependent and
unmeasured, which is exactly where the robustness argument was anchored.

A concentrating zone focuses by chromatographic migration in the inert adsorbent
rather than by evaporation, so it restores the assumption.
"""

from __future__ import annotations

from dataclasses import dataclass

SIGMA0_NOMINAL_MM = 1.0

# Sin medición propia, la dispersión de sigma0 con matriz no volátil es desconocida.
# Se declara una incertidumbre amplia y explícita en vez de fingir un valor fino:
# el objetivo es que la optimización robusta deje de tratar sigma0 como certeza.
SIGMA0_INCIERTO_MM = 0.5


@dataclass(frozen=True)
class RegimenSigma0:
    """Prior over the initial band width."""

    mu: float
    sigma: float
    determinista: bool
    motivo: str


def regimen_sigma0(estado: str, zona_concentracion: bool) -> RegimenSigma0:
    """Return the sigma0 prior implied by a SimExtract HPTLC verdict.

    Args:
        estado: Verdict state. "LIMPIA" for a cleaned-up sample; otherwise the
            value of `hptlc.Estado` from SimExtract.
        zona_concentracion: Whether the plate carries a concentrating zone.

    Returns:
        The prior, deterministic only when band focusing is actually available.
    """
    if zona_concentracion:
        return RegimenSigma0(
            mu=SIGMA0_NOMINAL_MM,
            sigma=0.0,
            determinista=True,
            motivo=(
                "La zona de concentración enfoca por migración cromatográfica, no por "
                "evaporación: el supuesto determinista se sostiene."
            ),
        )
    if estado == "LIMPIA":
        return RegimenSigma0(
            mu=SIGMA0_NOMINAL_MM,
            sigma=0.0,
            determinista=True,
            motivo="Muestra limpia: el spray-on enfoca y sigma0 es reproducible.",
        )
    return RegimenSigma0(
        mu=SIGMA0_NOMINAL_MM,
        sigma=SIGMA0_INCIERTO_MM,
        determinista=False,
        motivo=(
            "Matriz NADES no volátil sin zona de concentración: el aplicador dosifica "
            "volumen pero no enfoca. sigma0 pasa a incierto y se propaga por Monte "
            "Carlo junto con las variables manuales."
        ),
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "$SE" && python -m pytest tests/test_sigma0.py -v`
Expected: PASS, 3 pruebas

- [ ] **Step 5: Commit**

```bash
git add engine/sigma0.py tests/test_sigma0.py
git commit -m "feat: regimen de sigma0 segun el veredicto de siembra"
```

---

### Task 13: Propagar σ₀ por Monte Carlo

**Files:**
- Modify: `SE/engine/optimizer.py` (líneas 18-49)
- Test: `SE/tests/test_optimizer.py`

**Interfaces:**
- Consumes: `RegimenSigma0` (Task 12)
- Produces: `ConditionPrior` con `sigma0_mu` y `sigma0_sigma`, y `ConditionPrior.desde_regimen(regimen) -> ConditionPrior`

- [ ] **Step 1: Write the failing test**

```python
# añadir a SE/tests/test_optimizer.py
def test_sigma0_determinista_da_replicas_identicas() -> None:
    from engine.optimizer import ConditionPrior

    prior = ConditionPrior(sigma0_mu=1.0, sigma0_sigma=0.0)
    valores = {c.sigma0 for c in prior.sample(16)}
    assert valores == {1.0}


def test_sigma0_incierto_varia_entre_replicas() -> None:
    from engine.optimizer import ConditionPrior

    prior = ConditionPrior(sigma0_mu=1.0, sigma0_sigma=0.5)
    valores = {c.sigma0 for c in prior.sample(16)}
    assert len(valores) > 1
    assert all(v > 0 for v in valores)


def test_prior_desde_regimen_hereda_la_incertidumbre() -> None:
    from engine.optimizer import ConditionPrior
    from engine.sigma0 import regimen_sigma0

    prior = ConditionPrior.desde_regimen(
        regimen_sigma0("SIN_EVIDENCIA", zona_concentracion=False)
    )
    assert prior.sigma0_sigma > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$SE" && python -m pytest tests/test_optimizer.py -k sigma0 -v`
Expected: FAIL con `TypeError: ConditionPrior.__init__() got an unexpected keyword argument 'sigma0_mu'`

- [ ] **Step 3: Write minimal implementation**

En `SE/engine/optimizer.py`, sustituir el campo `sigma0: float = 1.0` y el método
`sample` por:

```python
    sigma0_mu: float = 1.0
    sigma0_sigma: float = 0.0
    seed: int = 1234

    @classmethod
    def desde_regimen(cls, regimen, **kwargs) -> "ConditionPrior":
        """Build a prior whose sigma0 follows a SimExtract verdict regime.

        Args:
            regimen: A `engine.sigma0.RegimenSigma0`.
            **kwargs: Any other prior field to override.

        Returns:
            The prior with sigma0 taken from the regime.
        """
        return cls(sigma0_mu=regimen.mu, sigma0_sigma=regimen.sigma, **kwargs)

    def sample(self, M: int) -> list[Conditions]:
        """Draw deterministic Monte Carlo condition replicas."""
        rng = np.random.default_rng(self.seed)
        rhs = np.clip(rng.normal(self.rh_mu, self.rh_sigma, M), 0, 95)
        temps = rng.normal(self.T_mu, self.T_sigma, M)
        deltas = rng.uniform(self.delta_sat_low, self.delta_sat_high, M)
        zfs = np.clip(rng.normal(self.zf_mu, self.zf_sigma, M), 20, 150)
        # sigma0 deja de copiarse idéntico a cada réplica: con matriz NADES no
        # volátil el aplicador ya no lo fija (ver engine/sigma0.py).
        if self.sigma0_sigma > 0:
            sigma0s = np.clip(
                rng.normal(self.sigma0_mu, self.sigma0_sigma, M), 0.1, None
            )
        else:
            sigma0s = np.full(M, self.sigma0_mu)
        return [
            Conditions(
                rh=float(rh),
                T=float(temp),
                delta_sat=float(delta),
                zf=float(zf),
                sigma0=float(s0),
            )
            for rh, temp, delta, zf, s0 in zip(rhs, temps, deltas, zfs, sigma0s)
        ]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd "$SE" && python -m pytest -q`
Expected: PASS, toda la suite

- [ ] **Step 5: Actualizar la documentación que ahora es falsa**

En `SE/docs/02_VARIABLES_HPTLC.md`, la fila 1 de la tabla y la nota "1. Siembra"
afirman que σ₀ es el único parámetro sin incertidumbre. Sustituir la nota por:

```markdown
**1. Siembra.** Con muestra limpia, `σ₀` es conocido y reproducible: la técnica
spray-on forma banda angosta porque el disolvente se evapora durante la aplicación
(CAMAG), y ahí se apoyaba el argumento de defensibilidad del modelo.

Ese supuesto **no se traslada a un extracto NADES sembrado directo**. Un NADES tiene
baja presión de vapor por definición (Liu et al. 2017, DOI 10.1016/j.chroma.2017.12.009),
de modo que el mecanismo de enfoque no opera sobre esa fracción: el aplicador dosifica
un volumen reproducible pero no lo convierte en banda estrecha. `σ₀` pasa entonces de
determinista a dependiente de la matriz y no medido, y se propaga por Monte Carlo junto
con las variables 4-7 (ver `engine/sigma0.py`).

Una placa con zona de concentración restituye el supuesto, porque enfoca por migración
cromatográfica en un adsorbente inerte en vez de por evaporación.
```

Y en la tabla de semillas, cambiar la fila de `σ₀`:

```markdown
| `σ₀` (mm, siembra) | 1.0 | fijo con muestra limpia o zona de concentración; ±0.5 con matriz NADES |
```

- [ ] **Step 6: Commit**

```bash
git add engine/optimizer.py tests/test_optimizer.py docs/02_VARIABLES_HPTLC.md
git commit -m "feat: sigma0 se propaga como incierto con matriz NADES"
```

---

## Verificación final

- [ ] `cd "$SN" && .venv/Scripts/python.exe -m pytest -q` — toda la suite pasa
- [ ] `cd "$SE" && python -m pytest -q` — toda la suite pasa
- [ ] `cd "$SN" && .venv/Scripts/python.exe -m black --check . && .venv/Scripts/python.exe -m ruff check .`
- [ ] Doble clic en `SimExtract.lnk` del escritorio: la app abre en las cuatro etapas
- [ ] La pestaña 🧫 HPTLC da `SIN_EVIDENCIA` gris para RP-18 W y lista los siete vacíos
- [ ] Un ensayo guardado en ③ Registrar sigue ahí tras cerrar y reabrir la app

## Criterios de aceptación del spec

| # | Criterio | Cubierto por |
|---|---|---|
| 1 | Ningún factor emite valor sin `fuente_id` resoluble | Task 2, `Factor.__post_init__` + `test_ningun_factor_emite_valor_sin_fuente_resoluble` |
| 2 | Cada vacío aparece en la UI según la placa | Task 2 `_vacios_base`, Task 4 sección "Qué falta medir" |
| 3 | Sílica 60G reproduce el resultado publicado | Task 2, `test_fase_normal_reproduce_el_fracaso_publicado` |
| 4 | RP-18 sale `SIN_EVIDENCIA`, nunca `VIABLE` | Task 2, `test_fase_reversa_nunca_sale_viable` |
| 5 | `hptlc.py` se prueba sin Streamlit | Task 2 Step 5 |
| 6 | Un experimento sobrevive al reinicio | Task 5, `test_lo_anexado_sobrevive_a_releer_el_archivo` |

### Cobertura de los vacíos del spec §4

| Vacío del spec | `Factor.id` | Tarea |
|---|---|---|
| §4.1 NADES directo en RP-18 | `cruce-nades-rp18` | Task 2 |
| §4.2 Umbral de dosificación | `umbral-viscosidad` | Task 2 |
| §4.3 Carga no volátil tolerable | `carga-tolerable` | Task 2 |
| §4.4 Interferencia en revelado sin limpieza | `revelado-sin-limpieza` | Task 2 |
| §4.5 Volatilidad/higroscopicidad de los 39 componentes | `componentes-hptlc` | Task 2 |
| §4.6 Raspado de banda → HPLC | `raspado-hplc` | Task 2 |
| §3.3.b Obstrucción y arrastre del aplicador | `obstruccion-aplicador` | Task 2 |

### Cobertura de §10 (acople con SimEluent)

| Punto del spec | Tarea |
|---|---|
| §10.1 σ₀ deja de ser determinista | Task 12, Task 13 |
| §10.2 `Phase` sin tamaño de partícula | Task 11 |
| §10.2 `Phase` sin humectabilidad (W) | Task 11 |
| §10.2 `Phase` sin indicador F254/F254s | Task 11 |
| §10.2 Zona de concentración como control de σ₀ | Task 11, Task 12 |
| §10.3 `hptlc.py` consumible sin Streamlit | Task 2 Step 5 |

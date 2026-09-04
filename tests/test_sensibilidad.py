import pytest

import model
from data import HBA_COMPONENTS, HBD_COMPONENTS, get_polyphenol_database
from evidencia import PARAMETROS_SIN_FUENTE
from model import calculate_nades_properties
from sensibilidad import banda, comparar, score_ep_medio

POLY = get_polyphenol_database()

# EtOH:H2O 70:30 acidificado. ETN por las ecuaciones de Spange 2024.
ETOH_AC = {
    "polaridad": 0.716,
    "pH": 2.5,
    "cap_hbd": 1.58,
    "viscosidad": 2.0,
    "water_pct": 30,
    "water_pct_efectivo": 30,
}


def _nades() -> dict:
    return calculate_nades_properties(
        "Cloruro de Colina (ChCl)", "Ácido Cítrico", 1, 1, 30, 40, HBA_COMPONENTS, HBD_COMPONENTS
    )


# ── El registro de parámetros sin fuente ──────────────────────────


def test_los_dos_parametros_sin_fuente_estan_declarados() -> None:
    assert set(PARAMETROS_SIN_FUENTE) == {"polaridad-optima", "sigma-polaridad"}
    for p in PARAMETROS_SIN_FUENTE.values():
        assert p.hallazgo, f"{p.id} sin hallazgo de la auditoria"
        assert p.como_cerrarlo, f"{p.id} sin via para cerrarlo"


def test_los_sigmas_son_constantes_con_nombre_no_literales() -> None:
    assert model.SIGMA_POLARIDAD_EP == 0.08
    assert model.SIGMA_POLARIDAD_NEP == 0.10


# ── La sensibilidad ───────────────────────────────────────────────


def test_desplazar_la_polaridad_optima_cambia_el_puntaje() -> None:
    base = score_ep_medio(_nades(), POLY, 0.0)
    movido = score_ep_medio(_nades(), POLY, -0.10)
    assert base != pytest.approx(movido, abs=1e-6)


def test_el_sigma_se_restaura_aunque_se_pase_uno_distinto() -> None:
    score_ep_medio(_nades(), POLY, sigma=0.30)
    assert model.SIGMA_POLARIDAD_EP == 0.08


def test_una_gaussiana_ancha_acerca_los_sistemas() -> None:
    """Con sigma amplio la ventaja del NADES casi desaparece."""
    estrecho = score_ep_medio(_nades(), POLY, sigma=0.08) - score_ep_medio(
        ETOH_AC, POLY, sigma=0.08
    )
    ancho = score_ep_medio(_nades(), POLY, sigma=0.30) - score_ep_medio(ETOH_AC, POLY, sigma=0.30)
    assert ancho < estrecho / 2


def test_la_banda_contiene_al_valor_central() -> None:
    b = banda("NADES", _nades(), POLY)
    assert b.minimo <= b.central <= b.maximo
    assert b.amplitud > 0


# ── La comparación ────────────────────────────────────────────────


def test_el_ranking_nades_vs_etanol_no_es_estable() -> None:
    """Hallazgo de la auditoria: el orden se invierte dentro del rango explorado."""
    c = comparar({"NADES": _nades(), "EtOH:H2O 70:30 ac.": ETOH_AC}, POLY)
    assert c.ganador_central == "NADES"
    assert c.estable is False
    assert "EtOH:H2O 70:30 ac." in c.otros_ganadores
    assert "NO es estable" in c.veredicto


def test_comparar_exige_al_menos_dos_sistemas() -> None:
    with pytest.raises(ValueError):
        comparar({"solo uno": _nades()}, POLY)


def test_el_veredicto_nombra_al_rival_cuando_hay_vuelco() -> None:
    c = comparar({"NADES": _nades(), "EtOH:H2O 70:30 ac.": ETOH_AC}, POLY)
    assert "EtOH" in c.veredicto

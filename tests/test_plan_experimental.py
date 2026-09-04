import pytest

from evidencia import PARAMETROS_SIN_FUENTE
from plan_experimental import ENSAYOS, Ensayo, huecos_abiertos, sin_ensayo


def test_cada_ensayo_nombra_huecos_que_existen() -> None:
    """El validador impide que el plan se desincronice del registro."""
    for e in ENSAYOS:
        assert e.cierra, f"{e.id} no cierra ningun hueco"
        for clave in e.cierra:
            assert clave in PARAMETROS_SIN_FUENTE or clave.startswith("hptlc:")


def test_un_ensayo_que_inventa_un_hueco_es_error() -> None:
    with pytest.raises(ValueError, match="hueco inexistente"):
        Ensayo(
            id="falso",
            titulo="",
            pregunta="",
            cierra=("parametro-que-no-existe",),
            condiciones=(),
            que_medir="",
            como_entra="",
            esfuerzo="",
            porque_ahora="",
        )


def test_los_cuatro_parametros_declarados_tienen_ensayo() -> None:
    """Ningun hueco registrado queda sin via experimental."""
    assert sin_ensayo() == ()


def test_la_serie_de_etanol_cierra_los_dos_parametros_de_polaridad() -> None:
    serie = next(e for e in ENSAYOS if e.id == "serie-etanol")
    assert set(serie.cierra) == {"polaridad-optima", "sigma-polaridad"}


def test_la_cinetica_cierra_lo_calibrado() -> None:
    """Lo calibrado solo se cierra midiendo, no reponderando."""
    cin = next(e for e in ENSAYOS if e.id == "cinetica-almacenamiento")
    assert set(cin.cierra) == {"estabilidad-pesos", "bonus-des"}
    for clave in cin.cierra:
        assert PARAMETROS_SIN_FUENTE[clave].circular is True


def test_cada_ensayo_dice_que_medir_y_por_que_ahora() -> None:
    for e in ENSAYOS:
        assert e.que_medir and e.como_entra and e.porque_ahora and e.esfuerzo


def test_el_mapa_de_huecos_cubre_el_registro_completo() -> None:
    mapa = huecos_abiertos()
    for clave in PARAMETROS_SIN_FUENTE:
        assert clave in mapa

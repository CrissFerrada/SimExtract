import pytest

from aplicador import TEMP_APLICACION_C, lectura_aplicador
from data import HBA_COMPONENTS, HBD_COMPONENTS
from plan_experimental import ENSAYOS


def _lectura(agua: float = 30, temp_ext: float = 40):
    return lectura_aplicador(
        "Cloruro de Colina (ChCl)",
        "Ácido Cítrico",
        1,
        1,
        agua,
        temp_ext,
        HBA_COMPONENTS,
        HBD_COMPONENTS,
    )


def test_el_aplicador_ve_un_liquido_mas_espeso_que_la_extraccion() -> None:
    """La app reportaba la viscosidad a temperatura de extraccion, no de siembra."""
    lec = _lectura()
    assert lec.temp_aplicacion == TEMP_APLICACION_C
    assert lec.visc_aplicacion > lec.visc_extraccion
    assert lec.factor_temperatura > 2.0


def test_perder_el_agua_dispara_la_viscosidad() -> None:
    """Es el mecanismo detras del riesgo de taponar el capilar."""
    lec = _lectura()
    aguas = [a for a, _ in lec.deriva]
    viscos = [v for _, v in lec.deriva]
    assert aguas == sorted(aguas, reverse=True)
    assert viscos == sorted(viscos), "la viscosidad debe crecer al perder agua"
    assert lec.factor_secado > 5.0


def test_un_nades_anhidro_no_tiene_deriva_que_explorar() -> None:
    lec = _lectura(agua=0)
    assert len(lec.deriva) == 1
    assert lec.factor_secado == pytest.approx(1.0, abs=1e-6)


def test_la_temperatura_de_aplicacion_es_configurable() -> None:
    frio = lectura_aplicador(
        "Cloruro de Colina (ChCl)",
        "Ácido Cítrico",
        1,
        1,
        30,
        40,
        HBA_COMPONENTS,
        HBD_COMPONENTS,
        temp_aplicacion=18.0,
    )
    templado = _lectura()
    assert frio.visc_aplicacion > templado.visc_aplicacion


def test_la_prueba_de_aplicador_va_primera_en_el_plan() -> None:
    """Es lo unico que puede danar material caro: precede a todo lo demas."""
    assert ENSAYOS[0].id == "prueba-aplicador"
    assert "NUNCA" in " ".join(ENSAYOS[0].condiciones)

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
